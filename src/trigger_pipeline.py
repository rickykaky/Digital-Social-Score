"""
Trigger Pipeline - Soumet le pipeline Kubeflow à Vertex AI Pipelines
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from google.cloud import aiplatform
from kfp.v2 import compiler, dsl
from kfp.v2.dsl import component, Input, Output, Model

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- COMPOSANTS KFP ---

@component(
    base_image="python:3.11",
    packages_to_install=["pandas", "nltk", "scikit-learn", "joblib"]
)
def prepare_data_op(raw_csv_path: str, clean_csv_path: str):
    """Prépare les données pour l'entraînement."""
    import pandas as pd
    import re
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    import nltk
    
    logger.info(f"Chargement des données depuis {raw_csv_path}")
    
    # Télécharger les ressources NLTK
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    
    # Charger les données
    df = pd.read_csv(raw_csv_path)
    logger.info(f"Données chargées: {len(df)} lignes")
    
    # Supprimer les valeurs manquantes
    df = df.dropna(subset=['comment_text'])
    df = df[df['comment_text'].str.strip() != ""]
    
    # Nettoyage du texte
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    def clean_text(text):
        # Supprimer caractères spéciaux
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        # Tokenisation
        tokens = word_tokenize(text)
        # Suppression stopwords + lemmatisation
        tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
        return " ".join(tokens)
    
    df['comment_text_clean'] = df['comment_text'].apply(clean_text)
    
    # Sauvegarder
    df.to_csv(clean_csv_path, index=False)
    logger.info(f"Données nettoyées sauvegardées: {clean_csv_path}")

@component(
    base_image="python:3.11",
    packages_to_install=["pandas", "scikit-learn", "joblib"]
)
def train_model_op(
    clean_csv_path: str,
    model_path: Output[Model],
    vectorizer_path: str = "gs://digital-social-score/models/vectorizer.joblib"
):
    """Entraîne le modèle de toxicité."""
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    import joblib
    from google.cloud import storage
    
    logger.info(f"Chargement des données depuis {clean_csv_path}")
    df = pd.read_csv(clean_csv_path)
    
    # Préparer X et y
    X = df['comment_text_clean'].fillna('')
    y = df['toxic']
    
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
    packages_to_install=["pandas", "scikit-learn", "joblib"]
)
def evaluate_model_op(
    model_path: Input[Model],
    clean_csv_path: str
) -> float:
    """Évalue le modèle."""
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    import joblib
    
    logger.info("Évaluation du modèle")
    
    # Charger données
    df = pd.read_csv(clean_csv_path)
    X = df['comment_text_clean'].fillna('')
    y = df['toxic']
    
    # Charger modèle
    model = joblib.load(model_path.path)
    
    # Vectorisation (il faudrait sauvegarder le vectorizer aussi)
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_vec = vectorizer.fit_transform(X)
    
    # Prédictions
    y_pred = model.predict(X_vec)
    
    # Métriques
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    
    logger.info(f"Accuracy: {accuracy:.4f}")
    logger.info(f"Precision: {precision:.4f}")
    logger.info(f"Recall: {recall:.4f}")
    logger.info(f"F1-Score: {f1:.4f}")
    
    return float(accuracy)

# --- PIPELINE ---

@dsl.pipeline(
    name="digital-social-score-pipeline",
    description="Pipeline d'entraînement et évaluation du modèle de toxicité",
    pipeline_root="gs://digital-social-score/pipeline-root"
)
def digital_score_pipeline(
    raw_csv_path: str = "gs://digital-social-score/data/train.csv",
    clean_csv_path: str = "gs://digital-social-score/data/clean.csv"
):
    """Pipeline complet: préparation → entraînement → évaluation"""
    
    # Étape 1: Préparation
    prepare_task = prepare_data_op(
        raw_csv_path=raw_csv_path,
        clean_csv_path=clean_csv_path
    )
    
    # Étape 2: Entraînement
    train_task = train_model_op(
        clean_csv_path=clean_csv_path
    )
    train_task.after(prepare_task)
    
    # Étape 3: Évaluation
    eval_task = evaluate_model_op(
        model_path=train_task.outputs['model_path'],
        clean_csv_path=clean_csv_path
    )
    eval_task.after(train_task)

# --- FONCTIONS DE SOUMISSION ---

def compile_pipeline(output_path: str = "digital_score_pipeline.yaml") -> str:
    """Compile le pipeline en YAML."""
    logger.info(f"Compilation du pipeline...")
    compiler.Compiler().compile(
        pipeline_func=digital_score_pipeline,
        package_path=output_path
    )
    logger.info(f"Pipeline compilé: {output_path}")
    return output_path

def submit_pipeline(
    project_id: str,
    region: str = "europe-west1",
    pipeline_yaml: str = "digital_score_pipeline.yaml",
    display_name: str = "Digital-Social-Score-Pipeline"
) -> str:
    """Soumet le pipeline à Vertex AI Pipelines."""
    
    logger.info(f"Initialisation de Vertex AI (projet: {project_id}, région: {region})")
    aiplatform.init(project=project_id, location=region)
    
    # Créer le job pipeline
    job = aiplatform.PipelineJob(
        display_name=display_name,
        template_path=pipeline_yaml,
        pipeline_root="gs://digital-social-score/pipeline-root",
        parameter_values={
            "raw_csv_path": "gs://digital-social-score/data/train.csv",
            "clean_csv_path": "gs://digital-social-score/data/clean.csv"
        }
    )
    
    logger.info(f"Soumission du pipeline...")
    job.submit()
    logger.info(f"Pipeline soumis avec succès! Job ID: {job.name}")
    
    return job.name

def main():
    parser = argparse.ArgumentParser(
        description="Trigger le pipeline Digital Social Score sur Vertex AI"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Google Cloud Project ID"
    )
    parser.add_argument(
        "--region",
        default="europe-west1",
        help="GCP Region"
    )
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Compiler seulement, ne pas soumettre"
    )
    parser.add_argument(
        "--yaml",
        default="digital_score_pipeline.yaml",
        help="Chemin du fichier YAML compilé"
    )
    parser.add_argument(
        "--display-name",
        default="Digital-Social-Score-Pipeline",
        help="Nom du pipeline"
    )
    
    args = parser.parse_args()
    
    try:
        # Compiler
        yaml_path = compile_pipeline(args.yaml)
        
        if args.compile_only:
            logger.info(f"Pipeline compilé: {yaml_path}")
            return
        
        # Soumettre
        job_name = submit_pipeline(
            project_id=args.project,
            region=args.region,
            pipeline_yaml=yaml_path,
            display_name=args.display_name
        )
        
        logger.info(f"✅ Pipeline soumis avec succès!")
        logger.info(f"Consultez le statut sur Vertex AI Pipelines")
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}", exc_info=True)
        exit(1)

if __name__ == "__main__":
    main()