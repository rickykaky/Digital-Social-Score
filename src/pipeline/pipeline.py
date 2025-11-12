"""
Pipeline Kubeflow (KFP v2) pour Digital Social Score
Composants: Préparation des données -> Entraînement -> Évaluation
"""

import logging

from kfp.v2 import dsl
from kfp.v2.dsl import Dataset, Input, Model, Output, component


# ============================================================================
# COMPOSANT 1: Préparation des données
# ============================================================================
@component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas", "scikit-learn", "nltk"],
)
def prepare_data_op(raw_csv_path: str, clean_csv_path: Output[Dataset]):
    """
    Préparation des données:
    - Charge le CSV brut (train.csv)
    - Supprime les valeurs manquantes
    - Nettoie le texte (stopwords, lemmatisation NLTK)
    - Sauvegarde le CSV nettoyé
    """
    import re

    import nltk
    import pandas as pd
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize

    logging.info(f"Chargement du fichier brut: {raw_csv_path}")

    # Télécharger les ressources NLTK
    for pkg in ["punkt", "stopwords", "wordnet", "averaged_perceptron_tagger"]:
        try:
            nltk.data.find(pkg)
        except LookupError:
            nltk.download(pkg)

    # Charger les données
    df = pd.read_csv(raw_csv_path)
    logging.info(f"Données chargées: {df.shape[0]} lignes, {df.shape[1]} colonnes")

    # Supprimer les valeurs manquantes dans comment_text
    df = df.dropna(subset=["comment_text"])
    df = df[df["comment_text"].str.strip() != ""]
    logging.info(f"Après suppression des NaN: {df.shape[0]} lignes")

    # Initialiser les outils NLTK
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

    def clean_text(text):
        """Nettoie un texte avec NLTK"""
        if not isinstance(text, str):
            return ""
        # Minuscules et suppression des caractères spéciaux
        text = re.sub(r"[^a-zA-Z\s]", "", text.lower())
        # Tokenisation
        tokens = word_tokenize(text)
        # Suppression des stopwords et lemmatisation
        tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
        return " ".join(tokens)

    # Appliquer le nettoyage
    logging.info("Nettoyage du texte en cours...")
    df["comment_text_clean"] = df["comment_text"].apply(clean_text)

    # Sauvegarder le CSV nettoyé
    df.to_csv(clean_csv_path.path, index=False)
    logging.info(f"Données nettoyées sauvegardées: {clean_csv_path.path}")


# ============================================================================
# COMPOSANT 2: Entraînement du modèle
# ============================================================================
@component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas", "scikit-learn", "joblib"],
)
def train_model_op(
    clean_csv_path: Input[Dataset],
    model_path: Output[Model],
    vectorizer_path: Output[Model],
):
    """
    Entraîne un modèle de classification (LogisticRegression + TfidfVectorizer):
    - Charge le CSV nettoyé
    - Vectorise le texte (TF-IDF)
    - Entraîne un modèle LogisticRegression
    - Sauvegarde le modèle et le vectoriseur
    """
    import joblib
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    logging.info(f"Chargement des données nettoyées: {clean_csv_path.path}")
    df = pd.read_csv(clean_csv_path.path)

    # Vérifier la présence de la colonne 'toxic'
    if "toxic" not in df.columns:
        raise ValueError("Colonne 'toxic' non trouvée dans les données")

    X = df["comment_text_clean"]
    y = df["toxic"]

    logging.info(f"Ensemble d'entraînement: {X.shape[0]} échantillons")
    logging.info(f"Distribution des classes: {y.value_counts().to_dict()}")

    # Vectorisation TF-IDF
    logging.info("Vectorisation TF-IDF en cours...")
    vectorizer = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.8)
    X_vectorized = vectorizer.fit_transform(X)

    # Entraînement du modèle
    logging.info("Entraînement du modèle LogisticRegression...")
    model = LogisticRegression(max_iter=1000, random_state=42, verbose=1)
    model.fit(X_vectorized, y)

    # Sauvegarder le modèle et le vectoriseur
    joblib.dump(model, model_path.path)
    joblib.dump(vectorizer, vectorizer_path.path)
    logging.info(f"Modèle sauvegardé: {model_path.path}")
    logging.info(f"Vectoriseur sauvegardé: {vectorizer_path.path}")


# ============================================================================
# COMPOSANT 3: Évaluation du modèle
# ============================================================================
@component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas", "scikit-learn", "joblib"],
)
def evaluate_model_op(
    clean_csv_path: Input[Dataset],
    model_path: Input[Model],
    vectorizer_path: Input[Model],
) -> float:
    """
    Évalue le modèle sur les données d'entraînement:
    - Charge le CSV nettoyé, le modèle et le vectoriseur
    - Calcule l'accuracy, precision, recall, F1-score
    - Retourne l'accuracy
    """
    import joblib
    import pandas as pd
    from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                                 precision_score, recall_score)

    logging.info(f"Chargement du modèle: {model_path.path}")
    model = joblib.load(model_path.path)
    vectorizer = joblib.load(vectorizer_path.path)

    logging.info(f"Chargement des données: {clean_csv_path.path}")
    df = pd.read_csv(clean_csv_path.path)

    X = df["comment_text_clean"]
    y = df["toxic"]

    # Vectorisation
    X_vectorized = vectorizer.transform(X)

    # Prédictions
    y_pred = model.predict(X_vectorized)

    # Métriques
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, average="binary")
    recall = recall_score(y, y_pred, average="binary")
    f1 = f1_score(y, y_pred, average="binary")
    cm = confusion_matrix(y, y_pred)

    logging.info(f"=== RÉSULTATS DE L'ÉVALUATION ===")
    logging.info(f"Accuracy:  {accuracy:.4f}")
    logging.info(f"Precision: {precision:.4f}")
    logging.info(f"Recall:    {recall:.4f}")
    logging.info(f"F1-Score:  {f1:.4f}")
    logging.info(f"Confusion Matrix:\n{cm}")

    return accuracy


# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================
@dsl.pipeline(
    name="digital-social-score-pipeline",
    description="Pipeline d'entraînement pour la détection de toxicité",
    pipeline_root="gs://digital-social-score/pipeline-root",
)
def digital_score_pipeline(
    raw_csv_path: str = "gs://digital-social-score/data/train.csv",
    clean_csv_path: str = "gs://digital-social-score/data/clean.csv",
):
    """
    Pipeline d'entraînement complet:
    1. Préparation des données (nettoyage, lemmatisation)
    2. Entraînement du modèle (TF-IDF + LogisticRegression)
    3. Évaluation du modèle
    """

    # Étape 1: Préparation
    prepare_task = prepare_data_op(
        raw_csv_path=raw_csv_path, clean_csv_path=clean_csv_path
    )
    prepare_task.set_display_name("Préparation des données")

    # Étape 2: Entraînement
    train_task = train_model_op(clean_csv_path=prepare_task.outputs["clean_csv_path"])
    train_task.set_display_name("Entraînement du modèle")

    # Étape 3: Évaluation
    eval_task = evaluate_model_op(
        clean_csv_path=prepare_task.outputs["clean_csv_path"],
        model_path=train_task.outputs["model_path"],
        vectorizer_path=train_task.outputs["vectorizer_path"],
    )
    eval_task.set_display_name("Évaluation du modèle")


# ============================================================================
# COMPILATION ET EXÉCUTION
# ============================================================================
if __name__ == "__main__":
    from kfp.v2 import compiler

    # Compiler le pipeline en fichier YAML
    output_file = "digital_score_pipeline.yaml"
    compiler.Compiler().compile(
        pipeline_func=digital_score_pipeline, package_path=output_file
    )

    print(f"Pipeline compilé: {output_file}")
    print("\nPour exécuter le pipeline:")
    print(
        f"  gcloud ai pipelines runs submit --region=us-west1 --pipeline-root=gs://digital-social-score/pipeline-root --display-name='Digital Score Pipeline' --yaml-pipeline-spec={output_file}"
    )
