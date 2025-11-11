"""
Trigger Pipeline - Soumet le pipeline Kubeflow à Vertex AI Pipelines
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from google.cloud import aiplatform
from kfp import compiler, dsl
from kfp.dsl import Input, Model, Output, component, Metrics, Artifact
from typing import NamedTuple

# Définir le type de retour pour l'évaluation
ModelEvaluation = NamedTuple("ModelEvaluation", [
    ("accuracy", float), 
    ("precision", float), 
    ("recall", float), 
    ("f1_score", float), 
    ("deploy_decision", str)
])

# Configuration logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- COMPOSANTS KFP ---


@component(
    base_image="python:3.11",
    packages_to_install=["pandas", "nltk", "scikit-learn", "joblib"],
)
def prepare_data_op(raw_csv_path: str, clean_csv_path: str):
    """Prépare les données pour l'entraînement."""
    import re

    import nltk
    import pandas as pd
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize

    logger.info(f"Chargement des données depuis {raw_csv_path}")

    # Télécharger les ressources NLTK
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")

    # Charger les données
    df = pd.read_csv(raw_csv_path)
    logger.info(f"Données chargées: {len(df)} lignes")

    # Supprimer les valeurs manquantes
    df = df.dropna(subset=["comment_text"])
    df = df[df["comment_text"].str.strip() != ""]

    # Nettoyage du texte
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

    def clean_text(text):
        # Supprimer caractères spéciaux
        text = re.sub(r"[^a-zA-Z\s]", "", text.lower())
        # Tokenisation
        tokens = word_tokenize(text)
        # Suppression stopwords + lemmatisation
        tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
        return " ".join(tokens)

    df["comment_text_clean"] = df["comment_text"].apply(clean_text)

    # Sauvegarder
    df.to_csv(clean_csv_path, index=False)
    logger.info(f"Données nettoyées sauvegardées: {clean_csv_path}")


@component(
    base_image="python:3.11", packages_to_install=["pandas", "scikit-learn", "joblib"]
)
def train_model_op(
    clean_csv_path: str,
    model_path: Output[Model],
    vectorizer_path: str = "gs://digital-social-score/models/vectorizer.joblib",
):
    """Entraîne le modèle de toxicité."""
    import joblib
    import pandas as pd
    from google.cloud import storage
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression

    logger.info(f"Chargement des données depuis {clean_csv_path}")
    df = pd.read_csv(clean_csv_path)

    # Préparer X et y
    X = df["comment_text_clean"].fillna("")
    y = df["toxic"]

    logger.info(f"Entraînement avec {len(X)} échantillons")

    # Vectorisation TF-IDF
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_vec = vectorizer.fit_transform(X)

    # Entraînement
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_vec, y)

    logger.info("Modèle entraîné avec succès")

    # Sauvegarder localement
    joblib.dump(model, model_path.path)
    joblib.dump(vectorizer, "/tmp/vectorizer.joblib")

    # Upload vers GCS (optionnel)
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket("digital-social-score")

        # Upload modèle
        blob_model = bucket.blob("models/model.joblib")
        blob_model.upload_from_filename(model_path.path)

        # Upload vectorizer
        blob_vec = bucket.blob("models/vectorizer.joblib")
        blob_vec.upload_from_filename("/tmp/vectorizer.joblib")

        logger.info("Modèle uploadé vers GCS")
    except Exception as e:
        logger.warning(f"Impossible d'uploader vers GCS: {e}")


@component(
    base_image="python:3.11", 
    packages_to_install=["pandas", "scikit-learn", "joblib", "google-cloud-storage"],
)
def evaluate_model_op(
    model_path: Input[Model], 
    vectorizer_path: str,
    clean_csv_path: str,
    metrics: Output[Metrics]
) -> ModelEvaluation:
    """Évalue le modèle et retourne les métriques + décision de déploiement."""
    import joblib
    import pandas as pd
    from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                                 recall_score, classification_report)
    from google.cloud import storage
    import os
    import tempfile

    logger.info("🔍 Évaluation du modèle")

    # Charger données de test
    df = pd.read_csv(clean_csv_path)
    X_test = df["comment_text_clean"].fillna("")
    y_test = df["toxic"]

    logger.info(f"📊 Données de test: {len(X_test)} échantillons")

    # Charger modèle depuis l'artifact
    model = joblib.load(model_path.path)
    logger.info("✅ Modèle chargé")

    # Charger vectorizer depuis GCS
    try:
        storage_client = storage.Client()
        bucket_name, blob_path = vectorizer_path.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            blob.download_to_filename(tmp_file.name)
            vectorizer = joblib.load(tmp_file.name)
            os.unlink(tmp_file.name)
        
        logger.info("✅ Vectorizer chargé depuis GCS")
    except Exception as e:
        logger.error(f"❌ Erreur chargement vectorizer: {e}")
        raise

    # Vectorisation des données de test
    X_test_vec = vectorizer.transform(X_test)

    # Prédictions
    y_pred = model.predict(X_test_vec)
    y_pred_proba = model.predict_proba(X_test_vec)[:, 1]  # Probabilités classe positive

    # Calculer métriques
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    # Log des métriques dans Kubeflow
    metrics.log_metric("accuracy", accuracy)
    metrics.log_metric("precision", precision)
    metrics.log_metric("recall", recall)
    metrics.log_metric("f1_score", f1)

    # Log détaillé
    logger.info(f"📊 MÉTRIQUES DU MODÈLE:")
    logger.info(f"   🎯 Accuracy:  {accuracy:.4f}")
    logger.info(f"   🎯 Precision: {precision:.4f}")
    logger.info(f"   🎯 Recall:    {recall:.4f}")
    logger.info(f"   🎯 F1-Score:  {f1:.4f}")

    # Classification report
    report = classification_report(y_test, y_pred)
    logger.info(f"📋 Rapport de classification:\n{report}")

    # DÉCISION DE DÉPLOIEMENT BASÉE SUR L'ACCURACY
    deploy_threshold = 0.85
    deploy_decision = accuracy >= deploy_threshold
    
    if deploy_decision:
        logger.info(f"✅ DÉPLOIEMENT AUTORISÉ: Accuracy {accuracy:.4f} ≥ {deploy_threshold}")
        decision_str = "true"
    else:
        logger.info(f"❌ DÉPLOIEMENT REFUSÉ: Accuracy {accuracy:.4f} < {deploy_threshold}")
        decision_str = "false"

    # Retourner les métriques et la décision
    return ModelEvaluation(
        accuracy=float(accuracy),
        precision=float(precision), 
        recall=float(recall),
        f1_score=float(f1),
        deploy_decision=decision_str
    )


@component(
    base_image="python:3.11",
    packages_to_install=["google-cloud-build"],
)
def build_and_deploy_docker_op(
    project_id: str,
    region: str = "us-west1",
    cluster_name: str = "social-score-cluster", 
    zone: str = "us-west1-a",
    image_tag: str = "ml-auto-deploy",
) -> str:
    """Déclenche le build et déploiement automatique via Cloud Build."""
    import logging
    from datetime import datetime
    from google.cloud import cloudbuild_v1

    # Configuration
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    full_tag = f"{image_tag}-{timestamp}"
    
    logging.info(f"� DÉPLOIEMENT ML AUTOMATIQUE")
    logging.info(f"   Accuracy ≥ 0.85 → Déploiement autorisé!")
    logging.info(f"   Projet: {project_id}")
    logging.info(f"   Tag: {full_tag}")
    logging.info(f"   Cluster: {cluster_name} ({zone})")

    try:
        # Créer le client Cloud Build
        client = cloudbuild_v1.CloudBuildClient()
        project_path = f"projects/{project_id}"

        # Configuration du build avec déploiement
        build_config = cloudbuild_v1.Build(
            steps=[
                # Étape 1: Build Docker avec nouveau modèle
                cloudbuild_v1.BuildStep(
                    name="gcr.io/cloud-builders/docker",
                    args=[
                        "build",
                        "-f", "src/Dockerfile.optimized",
                        "-t", f"gcr.io/{project_id}/digital-social-score:{full_tag}",
                        "-t", f"gcr.io/{project_id}/digital-social-score:latest-ml",
                        "."
                    ]
                ),
                # Étape 2: Push vers Container Registry
                cloudbuild_v1.BuildStep(
                    name="gcr.io/cloud-builders/docker",
                    args=[
                        "push", "--all-tags",
                        f"gcr.io/{project_id}/digital-social-score"
                    ]
                ),
                # Étape 3: Déploiement GKE automatique
                cloudbuild_v1.BuildStep(
                    name="gcr.io/google.com/cloudsdktool/cloud-sdk",
                    entrypoint="bash",
                    args=[
                        "-c",
                        f"""
                        echo "🚀 Déploiement ML automatique avec nouveau modèle..."
                        gcloud container clusters get-credentials {cluster_name} --zone {zone} --project {project_id}
                        kubectl get namespace production || kubectl create namespace production
                        kubectl set image deployment/social-score-api social-score-api=gcr.io/{project_id}/digital-social-score:{full_tag} -n production
                        kubectl rollout status deployment/social-score-api -n production --timeout=10m
                        echo "✅ Déploiement ML automatique terminé!"
                        echo "📊 Image déployée: {full_tag}"
                        """
                    ]
                )
            ],
            images=[
                f"gcr.io/{project_id}/digital-social-score:{full_tag}",
                f"gcr.io/{project_id}/digital-social-score:latest-ml"
            ],
            substitutions={
                "_REGION": region,
                "_ZONE": zone,
                "_CLUSTER_NAME": cluster_name,
                "_TAG": full_tag
            }
        )

        # Lancer le build (asynchrone)
        logging.info("🔨 Lancement du build Cloud Build...")
        operation = client.create_build(
            parent=project_path,
            build=build_config
        )
        
        build_id = operation.metadata.build.id
        logging.info(f"✅ Build lancé avec succès!")
        logging.info(f"   Build ID: {build_id}")
        
        build_url = f"https://console.cloud.google.com/cloud-build/builds/{build_id}?project={project_id}"
        logging.info(f"📊 Suivre le build: {build_url}")
        
        return f"SUCCESS: Build automatique {full_tag} lancé (ID: {build_id})"
        
    except Exception as e:
        logging.error(f"❌ Erreur déploiement automatique: {e}")
        return f"FAILED: {str(e)}"


# --- PIPELINE ---


@dsl.pipeline(
    name="digital-social-score-pipeline",
    description="Pipeline ML avec déploiement automatique conditionnel (accuracy ≥ 0.85)",
    pipeline_root="gs://digital-social-score/pipeline-root",
)
def digital_score_pipeline(
    raw_csv_path: str = "gs://digital-social-score/data/train.csv",
    clean_csv_path: str = "gs://digital-social-score/data/clean.csv",
    project_id: str = "digital-social-score",
    region: str = "us-west1",
    cluster_name: str = "social-score-cluster",
    zone: str = "us-west1-a",
    deploy_threshold: float = 0.85,
):
    """
    Pipeline ML complet avec déploiement conditionnel:
    1. Préparation des données
    2. Entraînement du modèle NLTK
    3. Évaluation (accuracy, precision, recall, f1)
    4. SI accuracy ≥ 0.85 → Déploiement automatique Docker + GKE
    5. SINON → Pas de déploiement
    """

    # ========================================================================
    # ÉTAPE 1: Préparation des données
    # ========================================================================
    prepare_task = prepare_data_op(
        raw_csv_path=raw_csv_path, 
        clean_csv_path=clean_csv_path
    )
    prepare_task.set_display_name("📋 Préparation des données")

    # ========================================================================
    # ÉTAPE 2: Entraînement du modèle
    # ========================================================================
    train_task = train_model_op(
        clean_csv_path=clean_csv_path
    )
    train_task.after(prepare_task)
    train_task.set_display_name("🤖 Entraînement NLTK")

    # ========================================================================
    # ÉTAPE 3: Évaluation avec décision de déploiement
    # ========================================================================
    eval_task = evaluate_model_op(
        model_path=train_task.outputs["model_path"],
        vectorizer_path="gs://digital-social-score/models/vectorizer.joblib",
        clean_csv_path=clean_csv_path
    )
    eval_task.after(train_task)
    eval_task.set_display_name("📊 Évaluation du modèle")

    # ========================================================================
    # ÉTAPE 4: Déploiement conditionnel (SI accuracy ≥ 0.85)
    # ========================================================================
    with dsl.If(
        eval_task.outputs["deploy_decision"] == "true",  # decision_str from evaluate_model_op
        name="deploy_condition"
    ):
        deploy_task = build_and_deploy_docker_op(
            project_id=project_id,
            region=region,
            cluster_name=cluster_name,
            zone=zone,
            image_tag=f"ml-auto-v{deploy_threshold}"
        )
        deploy_task.set_display_name("🚀 Déploiement automatique")


# --- FONCTIONS DE SOUMISSION ---


def compile_pipeline(output_path: str = "digital_score_pipeline.yaml") -> str:
    """Compile le pipeline en YAML."""
    logger.info(f"Compilation du pipeline...")
    compiler.Compiler().compile(
        pipeline_func=digital_score_pipeline, package_path=output_path
    )
    logger.info(f"Pipeline compilé: {output_path}")
    return output_path


def submit_pipeline(
    project_id: str,
    region: str = "us-west1",
    pipeline_yaml: str = "digital_score_pipeline.yaml",
    display_name: str = "Digital-Social-Score-ML-Pipeline",
    cluster_name: str = "social-score-cluster",
    zone: str = "us-west1-a",
    deploy_threshold: float = 0.85,
) -> str:
    """Soumet le pipeline ML avec déploiement conditionnel à Vertex AI."""

    logger.info(f"🚀 Initialisation Vertex AI ML Pipeline")
    logger.info(f"   Projet: {project_id}")
    logger.info(f"   Région: {region}")
    logger.info(f"   Seuil déploiement: accuracy ≥ {deploy_threshold}")
    
    aiplatform.init(project=project_id, location=region)

    # Paramètres du pipeline avec déploiement conditionnel
    pipeline_params = {
        "raw_csv_path": "gs://digital-social-score/data/train.csv",
        "clean_csv_path": "gs://digital-social-score/data/clean.csv",
        "project_id": project_id,
        "region": region,
        "cluster_name": cluster_name,
        "zone": zone,
        "deploy_threshold": deploy_threshold,
    }

    logger.info(f"📋 Paramètres du pipeline:")
    for key, value in pipeline_params.items():
        logger.info(f"   {key}: {value}")

    # Créer le job pipeline
    job = aiplatform.PipelineJob(
        display_name=display_name,
        template_path=pipeline_yaml,
        pipeline_root="gs://digital-social-score/pipeline-root",
        parameter_values=pipeline_params,
        enable_caching=True,  # Cache pour optimiser les re-runs
    )

    logger.info(f"🔄 Soumission du pipeline ML...")
    job.submit()
    
    logger.info(f"✅ Pipeline ML soumis avec succès!")
    logger.info(f"   Job ID: {job.name}")
    logger.info(f"   Display Name: {display_name}")
    logger.info(f"📊 Console Vertex AI:")
    logger.info(f"   https://console.cloud.google.com/vertex-ai/pipelines")
    logger.info(f"💡 Le modèle sera déployé automatiquement si accuracy ≥ {deploy_threshold}")

    return job.name


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline ML Digital Social Score avec déploiement automatique conditionnel"
    )
    parser.add_argument("--project", required=True, help="Google Cloud Project ID")
    parser.add_argument("--region", default="us-west1", help="GCP Region (défaut: us-west1)")
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Compiler seulement, ne pas soumettre",
    )
    parser.add_argument(
        "--yaml",
        default="digital_score_pipeline.yaml",
        help="Chemin du fichier YAML compilé",
    )
    parser.add_argument(
        "--display-name",
        default="Digital-Social-Score-ML-Pipeline",
        help="Nom du pipeline",
    )
    parser.add_argument(
        "--cluster-name",
        default="social-score-cluster",
        help="Nom du cluster GKE pour déploiement",
    )
    parser.add_argument(
        "--zone",
        default="us-west1-a",
        help="Zone du cluster GKE",
    )
    parser.add_argument(
        "--deploy-threshold",
        type=float,
        default=0.85,
        help="Seuil d'accuracy pour déploiement automatique (défaut: 0.85)",
    )

    args = parser.parse_args()

    try:
        logger.info(f"🤖 PIPELINE ML DIGITAL SOCIAL SCORE")
        logger.info(f"   Mode: {'COMPILATION SEULEMENT' if args.compile_only else 'COMPILATION + SOUMISSION'}")
        logger.info(f"   Projet: {args.project}")
        logger.info(f"   Seuil déploiement: accuracy ≥ {args.deploy_threshold}")

        # Compiler le pipeline
        yaml_path = compile_pipeline(args.yaml)

        if args.compile_only:
            logger.info(f"✅ Pipeline compilé uniquement: {yaml_path}")
            return

        # Soumettre le pipeline avec déploiement conditionnel
        job_name = submit_pipeline(
            project_id=args.project,
            region=args.region,
            pipeline_yaml=yaml_path,
            display_name=args.display_name,
            cluster_name=args.cluster_name,
            zone=args.zone,
            deploy_threshold=args.deploy_threshold,
        )

        logger.info(f"🎉 SUCCÈS!")
        logger.info(f"   Pipeline Job: {job_name}")
        logger.info(f"   Le modèle sera déployé automatiquement si accuracy ≥ {args.deploy_threshold}")
        logger.info(f"📊 Suivez l'exécution sur Vertex AI Pipelines Console")

    except Exception as e:
        logger.error(f"❌ Erreur: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
