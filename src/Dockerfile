# Utiliser une image de base Python légère
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger les ressources NLTK nécessaires pour l'exécution de l'API
# Les ressources sont nécessaires pour l'anonymisation et le nettoyage
RUN python -m nltk.downloader punkt averaged_perceptron_tagger maxent_ne_chunker words wordnet stopwords vader_lexicon

# Copier l'application et les modèles (qui seront créés par train.py)
COPY . .

# Exposer le port par défaut de Cloud Run (8080)
ENV PORT 8080

# Commande de démarrage de l'API avec Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

# Commande de démarrage de l'API avec Gunicorn (pour la gestion des workers)
# Gunicorn utilise la configuration dans gunicorn_conf.py
#CMD ["gunicorn", "app:app", "--config", "gunicorn_conf.py"]