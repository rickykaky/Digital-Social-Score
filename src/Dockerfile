# Utiliser une image de base Python légère
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer uv (package manager ultra-rapide)
RUN pip install uv

# Copier les fichiers de dépendances et installer
COPY requirements.txt .
# Debug: afficher le contenu pour vérifier
RUN echo "=== CONTENU requirements.txt ===" && cat requirements.txt && echo "=== FIN ==="

# Installer avec uv (10-100x plus rapide que pip)
RUN uv pip install --system --no-cache -r requirements.txt

# Télécharger les ressources NLTK nécessaires pour l'exécution de l'API
# Les ressources sont nécessaires pour l'anonymisation et le nettoyage
RUN mkdir -p /usr/share/nltk_data && \
    python -m nltk.downloader -d /usr/share/nltk_data punkt punkt_tab averaged_perceptron_tagger maxent_ne_chunker words wordnet stopwords vader_lexicon

# Ajouter un utilisateur non-root pour l'exécution (Meilleure pratique de sécurité)
RUN adduser --disabled-password --gecos "" appuser

# Copier l'application et les modèles (qui seront créés par train.py)
COPY . .

# Changer le propriétaire des fichiers copiés
RUN chown -R appuser:appuser /app

# Passer à l'utilisateur non-root
USER appuser

# Exposer le port par défaut de Cloud Run (8080)
ENV PORT 8080

# Commande de démarrage de l'API avec Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]