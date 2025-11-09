# Utiliser une image de base Python légère
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances et installer
COPY requirements.txt .
# Debug: afficher le contenu pour vérifier
RUN echo "=== CONTENU requirements.txt ===" && cat requirements.txt && echo "=== FIN ==="
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger les ressources NLTK nécessaires pour l'exécution de l'API
# Les ressources sont nécessaires pour l'anonymisation et le nettoyage
RUN mkdir -p /usr/share/nltk_data && \
    python -m nltk.downloader -d /usr/share/nltk_data punkt punkt_tab averaged_perceptron_tagger maxent_ne_chunker words wordnet stopwords vader_lexicon

# Copier l'application et les modèles (qui seront créés par train.py)
COPY . .

# Exposer le port par défaut de Cloud Run (8080)
ENV PORT 8080

# Commande de démarrage de l'API avec Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
# Ajouter un utilisateur non-root pour l'exécution (Meilleure pratique de sécurité)
# L'utilisateur par défaut dans python:3.10-slim est root.
RUN adduser --disabled-password --gecos "" appuser
USER appuser # <-- AJOUTER CETTE LIGNE

# Commande de démarrage de l'API avec Gunicorn (pour la gestion des workers)
# Gunicorn utilise la configuration dans gunicorn_conf.py
#CMD ["gunicorn", "app:app", "--config", "gunicorn_conf.py"]