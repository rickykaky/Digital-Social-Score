import re

import joblib
import nltk
import numpy as np
import pandas as pd
from nltk import ne_chunk, pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

# Configuration centralisée
from config import config

# --- 1. Fonctions d'Anonymisation (Basées sur la configuration) ---

# Utilisation des patterns d'anonymisation de la configuration centralisée
EMAIL_RE = config.EMAIL_RE
PHONE_RE = config.PHONE_RE
CREDIT_RE = config.CREDIT_RE
DATE_RE = config.DATE_RE
AGE_RE = config.AGE_RE
ADDRESS_RE = config.ADDRESS_RE


def mask_regex_pii(text):
    s = text
    s = EMAIL_RE.sub("<EMAIL>", s)
    s = CREDIT_RE.sub("<CREDIT_CARD>", s)
    s = PHONE_RE.sub(
        lambda m: (
            "<PHONE>" if len(re.sub(r"[^\d]", "", m.group(0))) >= 6 else m.group(0)
        ),
        s,
    )
    s = DATE_RE.sub("<DATE>", s)
    s = AGE_RE.sub("<AGE>", s)
    s = ADDRESS_RE.sub("<ADDRESS>", s)
    return s


def mask_named_entities(text):
    try:
        tokens = word_tokenize(text)
        tags = pos_tag(tokens)
        tree = ne_chunk(tags, binary=False)
    except Exception:
        return text

    for subtree in tree:
        if hasattr(subtree, "label"):
            label = subtree.label()
            ent = " ".join([tok for tok, pos in subtree.leaves()])
            if label in config.NAMED_ENTITY_LABELS:
                try:
                    pattern = re.compile(
                        r"\b" + re.escape(ent) + r"\b", flags=re.IGNORECASE
                    )
                    tag = f"<{label}>" if label != "PERSON" else "<PERSON>"
                    text = pattern.sub(tag, text)
                except re.error:
                    pass
    return text


def anonymize_text(text):
    if not isinstance(text, str):
        return ""
    # 1. Mask regex-based PII
    s = mask_regex_pii(text)
    # 2. Mask named entities from NLTK
    s = mask_named_entities(s)
    return s


# --- 2. Fonctions de Nettoyage NLTK (Basées sur le guide) ---

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


def clean_text_nltk(text):
    # 1. Mise en minuscule et suppression des caractères spéciaux
    text = re.sub(r"[^a-zA-Z\s]", "", text.lower())

    # 2. Tokenisation
    tokens = word_tokenize(text)

    # 3. Suppression des stop words et lemmatisation
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]

    return " ".join(tokens)


# --- 3. Fonction Principale d'Entraînement ---


def train_and_save_model(file_path="../data/prod.csv"):
    print("--- Démarrage de l'entraînement du modèle ---")

    # 1. Chargement et préparation des données
    df = pd.read_csv(file_path)

    # Détecter automatiquement la colonne de texte
    text_column = None
    for col in ["comment_text", "anonymized_comment", "text"]:
        if col in df.columns:
            text_column = col
            break

    if text_column is None:
        raise ValueError(
            "Aucune colonne de texte trouvée dans les données. Colonnes attendues: 'comment_text', 'anonymized_comment', 'text'"
        )

    print(f"Utilisation de la colonne de texte: {text_column}")
    df = df.dropna(subset=[text_column])
    df = df[df[text_column].str.strip() != ""]

    # Calcul d'un score de toxicité composite basé sur toutes les colonnes disponibles
    available_columns = config.get_available_toxicity_columns(df.columns.tolist())

    if available_columns:
        print(f"Utilisation des colonnes de toxicité: {available_columns}")
        # Score composite: au moins une colonne de toxicité = 1
        y = df[available_columns].max(axis=1)
    else:
        # Fallback sur la colonne 'toxic' si disponible
        if "toxic" in df.columns:
            y = df["toxic"]
        else:
            raise ValueError("Aucune colonne de toxicité trouvée dans les données")

    print(f"Nombre de commentaires à traiter: {len(df)}")

    # 2. Anonymisation (Étape RGPD)
    print("Application de l'anonymisation (RGPD)...")
    df["text_anonymized"] = df[text_column].apply(anonymize_text)

    # 3. Nettoyage NLTK
    print("Application du nettoyage NLTK...")
    df["comment_text_clean"] = df["text_anonymized"].apply(clean_text_nltk)

    # 4. Vectorisation (TF-IDF)
    print("Vectorisation TF-IDF...")
    X_train, X_test, y_train, y_test = train_test_split(
        df["comment_text_clean"], y, test_size=0.3, random_state=42
    )

    # Ajuster les paramètres selon la taille du dataset
    min_df = min(config.MIN_DF, len(X_train) // 10) if len(X_train) > 10 else 1
    max_features = min(config.MAX_FEATURES, len(X_train) * 100)

    vectorizer = TfidfVectorizer(
        max_features=max_features, min_df=min_df, max_df=config.MAX_DF
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # 5. Entraînement du Modèle (Régression Logistique)
    print("Entraînement du modèle de Régression Logistique...")
    model = LogisticRegression(solver="liblinear", random_state=42, max_iter=1000)
    model.fit(X_train_vec, y_train)

    # 6. Évaluation
    y_pred = model.predict(X_test_vec)
    print("\n--- Rapport de Classification ---")
    print(
        classification_report(y_test, y_pred, target_names=["Non-Toxique", "Toxique"])
    )

    # 7. Sauvegarde du Modèle et du Vectoriseur
    print("Sauvegarde du modèle et du vectoriseur...")
    model_path = config.get_model_path()
    vectorizer_path = config.get_vectorizer_path()

    # Créer le dossier s'il n'existe pas
    model_path.parent.mkdir(exist_ok=True, parents=True)

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    print(f"Modèle sauvegardé sous '{model_path}'")
    print(f"Vectoriseur sauvegardé sous '{vectorizer_path}'")


if __name__ == "__main__":
    print(
        "Les ressources NLTK sont supposées être pré-téléchargées. Lancement de l'entraînement..."
    )
    train_and_save_model()
