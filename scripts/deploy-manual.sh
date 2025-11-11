#!/bin/bash
# Script de déploiement manuel de l'API Social Score
# Usage: ./deploy-manual.sh [TAG]

set -e

PROJECT_ID="digital-social-score"
REGION="us-west1"
ZONE="us-west1-a"
CLUSTER_NAME="social-score-cluster"
TAG=${1:-latest}

echo "🚀 Déploiement manuel de l'API Social Score"
echo "   Tag: $TAG"
echo "   Cluster: $CLUSTER_NAME ($ZONE)"

# Se connecter au cluster
echo "🔗 Connexion au cluster GKE..."
gcloud container clusters get-credentials $CLUSTER_NAME \
  --zone $ZONE \
  --project $PROJECT_ID

# Créer le namespace production si nécessaire
echo "📦 Création du namespace production..."
kubectl create namespace production --dry-run=client -o yaml | kubectl apply -f -

# Appliquer les manifestes
echo "🚀 Application des manifestes Kubernetes..."
sed "s|PROJECT_ID|$PROJECT_ID|g" deployment/k8s/production-deployment.yaml | \
sed "s|gcr.io/PROJECT_ID/digital-social-score:latest|gcr.io/$PROJECT_ID/digital-social-score:$TAG|g" | \
kubectl apply -f -

echo "✅ Manifestes appliqués!"

# Attendre le déploiement
echo "⏳ Attente du déploiement..."
kubectl rollout status deployment/social-score-api -n production --timeout=300s

# Afficher l'état
echo "📊 État du déploiement:"
kubectl get pods -n production -l app=social-score-api

echo "🌐 Informations du service:"
kubectl get service social-score-service -n production

# Obtenir l'IP du LoadBalancer
echo "🔍 Recherche de l'IP externe..."
SERVICE_IP=$(kubectl get service social-score-service -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

if [ -n "$SERVICE_IP" ]; then
  echo "✅ Service accessible à: http://$SERVICE_IP"
  
  # Test de santé
  echo "🩺 Test de santé de l'API..."
  if curl -f --connect-timeout 10 http://$SERVICE_IP/health; then
    echo "✅ API répond correctement!"
  else
    echo "⚠️ API pas encore prête"
  fi
else
  echo "⚠️ IP externe pas encore assignée"
  echo "💡 Réessayez dans quelques minutes avec:"
  echo "   kubectl get service social-score-service -n production"
fi

echo "🎉 Déploiement terminé!"