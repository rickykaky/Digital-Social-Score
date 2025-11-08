import joblib
import os
import re
import nltk
# Indique à NLTK où chercher les données téléchargées dans le Dockerfile
nltk.data.path.append("/usr/share/nltk_data")
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
from fastapi import FastAPI
from pydantic import BaseModel

# Configuration centralisée
from config import config

# --- 1. Chargement du Modèle et du Vectoriseur ---

MODEL_PATH = config.get_model_path()
VECTORIZER_PATH = config.get_vectorizer_path()

try:
    # Charger le modèle et le vectoriseur
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("Modèle et vectoriseur chargés avec succès.")
except FileNotFoundError:
    print(f"Erreur: Fichiers de modèle ({MODEL_PATH} ou {VECTORIZER_PATH}) non trouvés. L'API démarrera mais ne pourra pas inférer.")
    model = None
    vectorizer = None

# --- 2. Fonctions de Traitement (Copie de train.py) ---

# Utilisation des patterns d'anonymisation de la configuration centralisée
EMAIL_RE = config.EMAIL_RE
PHONE_RE = config.PHONE_RE
CREDIT_RE = config.CREDIT_RE
DATE_RE = config.DATE_RE
AGE_RE = config.AGE_RE
ADDRESS_RE = config.ADDRESS_RE

def mask_regex_pii(text):
    s = text
    s = EMAIL_RE.sub('<EMAIL>', s)
    s = CREDIT_RE.sub('<CREDIT_CARD>', s)
    s = PHONE_RE.sub(lambda m: '<PHONE>' if len(re.sub(r'[^\d]', '', m.group(0))) >= 6 else m.group(0), s)
    s = DATE_RE.sub('<DATE>', s)
    s = AGE_RE.sub('<AGE>', s)
    s = ADDRESS_RE.sub('<ADDRESS>', s)
    return s

def mask_named_entities(text):
    try:
        tokens = word_tokenize(text)
        tags = pos_tag(tokens)
        tree = ne_chunk(tags, binary=False)
    except Exception:
        return text
    
    for subtree in tree:
        if hasattr(subtree, 'label'):
            label = subtree.label()
            ent = ' '.join([tok for tok, pos in subtree.leaves()])
            if label in config.NAMED_ENTITY_LABELS:
                try:
                    pattern = re.compile(r'\b' + re.escape(ent) + r'\b', flags=re.IGNORECASE)
                    tag = f'<{label}>' if label != 'PERSON' else '<PERSON>'
                    text = pattern.sub(tag, text)
                except re.error:
                    pass
    return text

def anonymize_text(text):
    if not isinstance(text, str):
        return ''
    s = mask_regex_pii(text)
    s = mask_named_entities(s)
    return s

# NLTK Cleaning
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text_nltk(text):
    # 1. Mise en minuscule et suppression des caractères spéciaux
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    
    # 2. Tokenisation
    tokens = word_tokenize(text)
    
    # 3. Suppression des stop words et lemmatisation
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
    
    return " ".join(tokens)

# --- 3. Définition de l'API FastAPI ---

app = FastAPI(
    title=config.API_CONFIG['title'],
    description=config.API_CONFIG['description'],
    version=config.API_CONFIG['version']
)

class TextPayload(BaseModel):
    text: str

def calculate_score(text: str) -> int:
    if model is None or vectorizer is None:
        # Retourne un score neutre si le modèle n'est pas chargé
        return 50 
        
    # 1. Anonymisation (RGPD)
    anonymized_text = anonymize_text(text)
    
    # 2. Nettoyage NLTK
    cleaned_text = clean_text_nltk(anonymized_text)
    
    # 3. Vectorisation
    text_vec = vectorizer.transform([cleaned_text])
    
    # 4. Prédiction (probabilité de toxicité)
    # model.predict_proba retourne [[Prob_Non_Toxique, Prob_Toxique]]
    prob_toxic = model.predict_proba(text_vec)[:, 1][0]
    
    # 5. Conversion en score social (0 à 100)
    # Score = 100 * (1 - Probabilité de Toxicité) 
    # Plus la probabilité de toxicité est faible, plus le score social est élevé.
    social_score = int(100 * (1 - prob_toxic))
    
    return max(0, min(100, social_score)) # Assurer que le score est entre 0 et 100

@app.post("/score")
def get_social_score(payload: TextPayload):
    """
    Calcule le score social (0-100) d'un texte en fonction de sa toxicité.
    Un score élevé signifie une faible toxicité.
    """
    score = calculate_score(payload.text)
    
    # Log de la transaction pour l'observabilité (Cloud Logging)
    print(f"INFO: Request processed. Text snippet: '{payload.text[:50]}...' | Score: {score}")
    
    return {
        "text_received": payload.text,
        "text_anonymized": anonymize_text(payload.text),
        "toxicity_score": score,
        "model_used": "LogisticRegression_TFIDF",
        "rgpd_compliant": True
    }

@app.get("/health")
def health_check():
    """Vérification de l'état de l'API et du chargement du modèle."""
    return {
        "status": "ok", 
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None
    }
