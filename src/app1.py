import os
import re
from typing import Optional

import joblib
import nltk
import numpy as np
import pandas as pd
from fastapi import FastAPI
from nltk import ne_chunk, pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from pydantic import BaseModel

# --- 1. Configuration ---

MODEL_PATH = "model.joblib"
VECTORIZER_PATH = "vectorizer.joblib"
PROD_CSV_PATH = "prod.csv"

# --- 2. Chargement du Modèle et du Vectoriseur ---

try:
    # Charger le modèle et le vectoriseur
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("Modèle et vectoriseur chargés avec succès.")
except FileNotFoundError:
    print(
        f"Erreur: Fichiers de modèle ({MODEL_PATH} ou {VECTORIZER_PATH}) non trouvés. L'API démarrera mais ne pourra pas inférer."
    )
    model = None
    vectorizer = None


# Charger ou initialiser prod.csv
def load_prod_csv():
    if os.path.exists(PROD_CSV_PATH):
        return pd.read_csv(
            PROD_CSV_PATH,
            dtype={
                "id": int,
                "user_id": int,
                "comment_text": str,
                "toxicity_score": float,
                "created_at": str,
            },
        )
    else:
        # Initialiser avec colonnes vides (structure complète actuelle)
        columns = ["id", "user_id", "comment_text", "toxicity_score", "created_at"]
        df = pd.DataFrame(columns=columns)
        # Définir les types de données
        df = df.astype(
            {
                "id": int,
                "user_id": int,
                "comment_text": str,
                "toxicity_score": float,
                "created_at": str,
            }
        )
        return df


# --- 3. Fonctions de Traitement et Anonymisation ---

# Regex patterns for common PII (données sensibles)
EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b", flags=re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-])?(?:\(?\d{2,4}\)?[\s.-])?[\d\s.-]{6,15}")
CREDIT_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
DATE_RE = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
    flags=re.IGNORECASE,
)
AGE_RE = re.compile(
    r"\b(?:age\s*[:]?\s*\d{1,3}|\d{1,3}\s?(?:years?\sold|yo|y/o|yrs|ans))\b",
    flags=re.IGNORECASE,
)
ADDRESS_RE = re.compile(
    r"\b\d{1,5}\s+(?:[\w\s]{1,60}?)\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Square|Sq)\b",
    flags=re.IGNORECASE,
)


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
        return text, []

    found = []
    for subtree in tree:
        if hasattr(subtree, "label"):
            label = subtree.label()
            ent = " ".join([tok for tok, pos in subtree.leaves()])
            if label in ("PERSON", "GPE", "LOCATION", "ORGANIZATION"):
                try:
                    pattern = re.compile(
                        r"\b" + re.escape(ent) + r"\b", flags=re.IGNORECASE
                    )
                    tag = f"<{label}>"
                    text = pattern.sub(tag, text)
                    found.append((ent, label))
                except re.error:
                    pass
    return text, found


def anonymize_text(text):
    if not isinstance(text, str):
        return "", []
    s = mask_regex_pii(text)
    s, entities = mask_named_entities(s)
    return s, entities


# NLTK Cleaning
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


# --- 4. Fonctions de Calcul de Toxicité et Score Social ---


def calculate_toxicity_score(text: str) -> int:
    """Calcule le score de toxicité (0-100) d'un texte.

    Retour :
    - Score 0 = peu/non toxique
    - Score 100 = très toxique
    """
    if model is None or vectorizer is None:
        return 50  # Score neutre si modèle non chargé

    try:
        # 1. Anonymisation (RGPD)
        anonymized_text, _ = anonymize_text(text)

        # 2. Nettoyage NLTK
        cleaned_text = clean_text_nltk(anonymized_text)

        # 3. Vectorisation
        text_vec = vectorizer.transform([cleaned_text])

        # 4. Prédiction (probabilité de toxicité)
        prob_toxic = model.predict_proba(text_vec)[:, 1][0]

        # 5. Conversion en score (0 à 100)
        # Score = 100 * Probabilité de Toxicité
        score = int(100 * prob_toxic)

        return max(0, min(100, score))  # Assurer que le score est entre 0 et 100
    except Exception as e:
        print(f"Erreur lors du calcul de toxicité : {e}")
        return 50


def calculate_user_social_score(user_id: int, prod_df: pd.DataFrame) -> float:
    """
    Calcule le score social d'un utilisateur.
    Score social = 100 / (moyenne des scores de toxicité du user)

    Si moyenne = 0, retourne 100 (user sain).
    """
    user_comments = prod_df[prod_df["user_id"] == user_id]

    if len(user_comments) == 0:
        return 100.0  # Nouveau user = score neutre

    avg_toxicity = user_comments["toxicity_score"].mean()

    if avg_toxicity == 0:
        return 100.0  # Aucune toxicité = score social maximal

    social_score = 100 / avg_toxicity
    return min(100.0, max(0.0, social_score))  # Clamped entre 0 et 100


# --- 5. Fonctions de Gestion du CSV ---


def add_or_update_comment(user_id: int, comment_text: str, toxicity_score: int) -> dict:
    """
    Ajoute ou met à jour un commentaire dans prod.csv.
    """
    prod_df = load_prod_csv()

    # Génération d'un ID unique (simple)
    if len(prod_df) == 0:
        new_id = 1
    else:
        new_id = prod_df["id"].max() + 1

    # Créer la nouvelle ligne
    from datetime import datetime

    new_row = pd.DataFrame(
        {
            "id": [new_id],
            "user_id": [user_id],
            "comment_text": [comment_text],
            "toxicity_score": [toxicity_score],
            "created_at": [datetime.now().isoformat()],
        }
    )

    # Ajouter à la DataFrame et sauvegarder
    prod_df = pd.concat([prod_df, new_row], ignore_index=True)
    prod_df.to_csv(PROD_CSV_PATH, index=False)

    # Recalculer le score social du user
    social_score = calculate_user_social_score(user_id, prod_df)

    return {
        "id": new_id,
        "user_id": user_id,
        "toxicity_score": toxicity_score,
        "user_social_score": social_score,
    }


def compute_all_toxicity_scores():
    """
    Calcule et met à jour les scores de toxicité de tous les commentaires
    dans prod.csv (fonction amont).
    """
    prod_df = load_prod_csv()

    if len(prod_df) == 0:
        print("prod.csv est vide. Aucun score à calculer.")
        return

    print(f"Calcul des scores de toxicité pour {len(prod_df)} commentaires...")

    scores = []
    for idx, row in prod_df.iterrows():
        text = row.get("comment_text", "")
        toxicity = calculate_toxicity_score(text)
        scores.append(toxicity)

        if (idx + 1) % 100 == 0:
            print(f"  Traité {idx + 1} commentaires...")

    prod_df["toxicity_score"] = scores
    prod_df.to_csv(PROD_CSV_PATH, index=False)
    print(f"Mise à jour terminée. {len(prod_df)} commentaires traités.")

    return prod_df


# --- 6. Définition de l'API FastAPI ---

app = FastAPI(
    title="Digital Social Score API",
    description="API pour la détection de toxicité, anonymisation RGPD et score social utilisateur.",
)


# Modèles Pydantic
class CommentPayload(BaseModel):
    user_id: int
    comment_text: str


class ToxicityPayload(BaseModel):
    text: str


# --- Endpoints ---


@app.post("/submit_comment")
def submit_comment(payload: CommentPayload):
    """
    Accepte un commentaire d'un utilisateur.
    Calcule le score de toxicité, l'ajoute au CSV et recalcule le score social du user.
    """
    user_id = payload.user_id
    comment_text = payload.comment_text

    # Calculer le score de toxicité
    toxicity_score = calculate_toxicity_score(comment_text)

    # Ajouter/mettre à jour dans prod.csv et récupérer le score social
    result = add_or_update_comment(user_id, comment_text, toxicity_score)

    print(
        f"INFO: Commentaire reçu - User {user_id}, Toxicity: {toxicity_score}, Social Score: {result['user_social_score']}"
    )

    return {
        "status": "success",
        "comment_id": result["id"],
        "user_id": result["user_id"],
        "toxicity_score": result["toxicity_score"],
        "user_social_score": round(result["user_social_score"], 2),
        "message": "Commentaire enregistré et scores mis à jour.",
    }


@app.get("/user_social_score/{user_id}")
def get_user_social_score(user_id: int):
    """Récupère le score social actuel d'un utilisateur."""
    prod_df = load_prod_csv()
    social_score = calculate_user_social_score(user_id, prod_df)

    user_comments = prod_df[prod_df["user_id"] == user_id]
    avg_toxicity = (
        user_comments["toxicity_score"].mean() if len(user_comments) > 0 else 0
    )

    return {
        "user_id": user_id,
        "user_social_score": round(social_score, 2),
        "average_toxicity": round(avg_toxicity, 2),
        "comment_count": len(user_comments),
    }


@app.post("/compute_all_toxicity")
def compute_all_toxicity():
    """
    Fonction amont : calcule les scores de toxicité de tous les commentaires
    dans prod.csv et les met à jour.
    """
    prod_df = compute_all_toxicity_scores()

    return {
        "status": "success",
        "message": "Tous les scores de toxicité ont été calculés et mis à jour.",
        "total_comments_processed": len(prod_df) if prod_df is not None else 0,
    }


@app.get("/health")
def health_check():
    """Vérification de l'état de l'API."""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "prod_csv_exists": os.path.exists(PROD_CSV_PATH),
    }


@app.get("/")
def root():
    """Endpoint racine avec documentation."""
    return {
        "API": "Digital Social Score",
        "endpoints": {
            "POST /submit_comment": "Soumettre un commentaire d'un user (user_id, comment_text)",
            "GET /user_social_score/{user_id}": "Obtenir le score social d'un user",
            "POST /compute_all_toxicity": "Calculer les scores de toxicité de tous les commentaires",
            "GET /health": "Vérifier l'état de l'API",
        },
    }
