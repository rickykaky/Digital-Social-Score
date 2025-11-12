#!/bin/bash
# Script de Setup Cache GCS pour Cloud Build
# Fichier: scripts/setup_cache_bucket.sh

set -e

# Configuration par défaut
PROJECT_ID=${1:-"digital-social-score"}
REGION=${2:-"us-west1"}
BUCKET_NAME="${PROJECT_ID}-cache-optimized"

echo "🚀 Configuration du Cache GCS pour Cloud Build"
echo "=============================================="
echo "Projet: $PROJECT_ID"
echo "Région: $REGION"  
echo "Bucket: $BUCKET_NAME"
echo ""

# 1. Créer le bucket de cache s'il n'existe pas
echo "📦 Création du bucket de cache..."
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo "✅ Bucket $BUCKET_NAME existe déjà"
else
    echo "🆕 Création du bucket $BUCKET_NAME..."
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
    echo "✅ Bucket créé"
fi

# 2. Configurer les permissions pour Cloud Build
echo "🔐 Configuration des permissions Cloud Build..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Donner accès au bucket pour Cloud Build
gsutil iam ch serviceAccount:$CLOUDBUILD_SA:roles/storage.admin gs://$BUCKET_NAME
echo "✅ Permissions configurées pour $CLOUDBUILD_SA"

# 3. Configurer la lifecycle du bucket (nettoyer les anciens caches)
echo "🗑️ Configuration du nettoyage automatique..."
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 30, "matchesPrefix": ["uv-cache-", "nltk-cache-"]}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://$BUCKET_NAME
rm lifecycle.json
echo "✅ Nettoyage automatique configuré (30 jours)"

# 4. Créer un cache initial vide pour éviter les erreurs
echo "💾 Création du cache initial..."
echo "Cache bucket created on $(date)" > initial-cache.txt
gsutil cp initial-cache.txt gs://$BUCKET_NAME/
rm initial-cache.txt

# 5. Vérification
echo "🧪 Vérification de la configuration..."
echo "Contenu du bucket:"
gsutil ls gs://$BUCKET_NAME/

echo ""
echo "✅ CONFIGURATION TERMINÉE !"
echo "=============================================="
echo "📊 Utilisation:"
echo "   - Utilisez cloudbuild.optimized.yaml"
echo "   - Le cache sera automatiquement géré"
echo "   - Premier build: création du cache"
echo "   - Builds suivants: 40-60% plus rapides"
echo ""
echo "🔧 Commandes utiles:"
echo "   # Voir l'état du cache"
echo "   gsutil ls -la gs://$BUCKET_NAME/"
echo ""
echo "   # Nettoyer le cache manuellement"
echo "   gsutil rm gs://$BUCKET_NAME/uv-cache-*.tar.gz"
echo "   gsutil rm gs://$BUCKET_NAME/nltk-cache-*.tar.gz"
echo ""
echo "   # Statistiques du bucket"
echo "   gsutil du -s gs://$BUCKET_NAME/"