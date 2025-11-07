import pandas as pd
import numpy as np
import re
import nltk
import joblib
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# --- 1. Fonctions d'Anonymisation (Basées sur le code utilisateur) ---

# Regex patterns for common PII
EMAIL_RE = re.compile(r'\b[-]+@[-]+\.{2,}', flags=re.IGNORECASE)
PHONE_RE = re.compile(r'(?:\+?\d{1,3}[.-])?(?:\(?\d{2,4}\)?[.-])?[\d.-]{6,15}')
CREDIT_RE = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
DATE_RE = re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b', flags=re.IGNORECASE)
AGE_RE = re.compile(r'\b(?:age\s*[:]?\s*\d{1,3}|\d{1,3}\s?(?:years?\sold|yo|y/o|yrs|ans))\b', flags=re.IGNORECASE)
ADDRESS_RE = re.compile(r'\b\d{1,5}\s+(?:[\w\s]{1,60}?)\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Square|Sq)\b', flags=re.IGNORECASE)

def mask_regex_pii(text):
    s = text
    s = EMAIL_RE.sub('<EMAIL>', s)
    s = CREDIT_RE.sub('<CREDIT_CARD>', s)
    s = PHONE_RE.sub(lambda m: '<PHONE>' if len(re.sub('[^\d]', '', m.group(0))) >= 6 else m.group(0), s)
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
            if label in ('PERSON', 'GPE', 'LOCATION', 'ORGANIZATION'):
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
    # 1. Mask regex-based PII
    s = mask_regex_pii(text)
    # 2. Mask named entities from NLTK
    s = mask_named_entities(s)
    return s

# --- 2. Fonctions de Nettoyage NLTK (Basées sur le guide) ---

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

# --- 3. Fonction Principale d'Entraînement ---

def train_and_save_model(file_path='train.csv'):
    print("--- Démarrage de l'entraînement du modèle ---")
    
    # 1. Chargement et préparation des données
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["anonymized_comment"])
    df = df[df["anonymized_comment"].str.strip() != ""]
    
    # Pour ce TP, nous nous concentrons sur la toxicité binaire (toxic=1 vs non-toxic=0)
    # Si le TP exige un score global, il faut combiner les colonnes de toxicité.
    # Ici, nous utilisons la colonne 'toxic' comme cible binaire.
    y = df['toxic']
    
    print(f"Nombre de commentaires à traiter: {len(df)}")
    
    # 2. Anonymisation (Étape RGPD)
    print("Application de l'anonymisation (RGPD)...")
    #df['comment_text_anonymise'] = df['anonymized_comment'].apply(anonymize_text)
    
    # 3. Nettoyage NLTK
    print("Application du nettoyage NLTK...")
    #df['comment_text_clean'] = df['comment_text_anonymise'].apply(clean_text_nltk)
    df['comment_text_clean'] = df['anonymized_comment'].apply(clean_text_nltk)
    
    # 4. Vectorisation (TF-IDF)
    print("Vectorisation TF-IDF...")
    X_train, X_test, y_train, y_test = train_test_split(
        df['comment_text_clean'], y, test_size=0.3, random_state=42
    )
    
    vectorizer = TfidfVectorizer(max_features=10000) # Limiter les features pour la performance
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # 5. Entraînement du Modèle (Régression Logistique)
    print("Entraînement du modèle de Régression Logistique...")
    model = LogisticRegression(solver='liblinear', random_state=42)
    model.fit(X_train_vec, y_train)
    
    # 6. Évaluation
    y_pred = model.predict(X_test_vec)
    print("\n--- Rapport de Classification ---")
    print(classification_report(y_test, y_pred, target_names=['Non-Toxique', 'Toxique']))
    
    # 7. Sauvegarde du Modèle et du Vectoriseur
    print("Sauvegarde du modèle et du vectoriseur...")
    joblib.dump(model, 'model.joblib')
    joblib.dump(vectorizer, 'vectorizer.joblib')
    print("Modèle et vectoriseur sauvegardés sous 'model.joblib' et 'vectorizer.joblib'.")

if __name__ == '__main__':
    print("Les ressources NLTK sont supposées être pré-téléchargées. Lancement de l'entraînement...")
    train_and_save_model()
