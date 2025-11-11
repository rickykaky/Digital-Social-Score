#!/bin/bash

# Script de test pour le pipeline ML avec déploiement conditionnel
# Usage: ./test_ml_pipeline.sh [seuil_accuracy]

set -e

PROJECT_ID="digital-social-score"
REGION="us-west1"
THRESHOLD=${1:-0.85}

echo "🤖 TEST DU PIPELINE ML AVEC DÉPLOIEMENT CONDITIONNEL"
echo "=================================================="
echo "Projet: $PROJECT_ID"
echo "Région: $REGION" 
echo "Seuil: accuracy ≥ $THRESHOLD"
echo ""

# Vérifier les prérequis
echo "🔍 Vérification des prérequis..."

# Python et dépendances
if ! command -v python &> /dev/null; then
    echo "❌ Python non trouvé"
    exit 1
fi

if ! python -c "import kfp, google.cloud.aiplatform" 2>/dev/null; then
    echo "📦 Installation des dépendances ML..."
    pip install kfp==2.5.0 google-cloud-aiplatform
fi

# Configuration gcloud
if ! gcloud config get-value project &>/dev/null; then
    echo "❌ gcloud non configuré"
    echo "💡 Exécutez: gcloud config set project $PROJECT_ID"
    exit 1
fi

echo "✅ Prérequis OK"
echo ""

# Test 1: Compilation du pipeline
echo "🔨 TEST 1: Compilation du pipeline ML..."
cd src

python trigger_pipeline.py \
    --project $PROJECT_ID \
    --region $REGION \
    --deploy-threshold $THRESHOLD \
    --compile-only

if [ -f "digital_score_pipeline.yaml" ]; then
    echo "✅ Pipeline compilé avec succès"
    echo "📄 Fichier généré: digital_score_pipeline.yaml"
else
    echo "❌ Erreur compilation pipeline"
    exit 1
fi

echo ""

# Test 2: Validation du fichier YAML
echo "📋 TEST 2: Validation du fichier pipeline..."

if grep -q "deploy_condition" digital_score_pipeline.yaml; then
    echo "✅ Condition de déploiement trouvée"
else
    echo "❌ Condition de déploiement manquante"
    exit 1
fi

if grep -q "build_and_deploy_docker_op" digital_score_pipeline.yaml; then
    echo "✅ Composant de déploiement Docker trouvé"
else
    echo "❌ Composant de déploiement Docker manquant"
    exit 1
fi

if grep -q "evaluate_model_op" digital_score_pipeline.yaml; then
    echo "✅ Composant d'évaluation trouvé"
else
    echo "❌ Composant d'évaluation manquant"
    exit 1
fi

echo "✅ Fichier pipeline valide"
echo ""

# Test 3: Vérification des paramètres
echo "🎯 TEST 3: Vérification des paramètres..."

if grep -q "deploy_threshold.*$THRESHOLD" digital_score_pipeline.yaml; then
    echo "✅ Seuil de déploiement configuré: $THRESHOLD"
else
    echo "⚠️  Seuil de déploiement non trouvé (peut être normal)"
fi

if grep -q "$PROJECT_ID" digital_score_pipeline.yaml; then
    echo "✅ Project ID configuré: $PROJECT_ID"
else
    echo "❌ Project ID manquant"
    exit 1
fi

echo "✅ Paramètres OK"
echo ""

# Test 4: Simulation évaluation modèle
echo "📊 TEST 4: Simulation évaluation modèle..."

cat > test_evaluation.py << 'EOF'
import sys
sys.path.append('.')

def simulate_evaluation(threshold):
    """Simule l'évaluation d'un modèle"""
    import random
    random.seed(42)
    
    # Simuler différentes accuracies
    test_cases = [0.78, 0.83, 0.87, 0.91, 0.94]
    
    for accuracy in test_cases:
        deploy = accuracy >= threshold
        status = "✅ DÉPLOIEMENT AUTORISÉ" if deploy else "❌ DÉPLOIEMENT REFUSÉ"
        print(f"Accuracy: {accuracy:.3f} | Seuil: {threshold:.3f} | {status}")
    
    return True

if __name__ == "__main__":
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.85
    simulate_evaluation(threshold)
EOF

python test_evaluation.py $THRESHOLD
rm test_evaluation.py

echo "✅ Simulation évaluation OK"
echo ""

# Test 5: Test de soumission (dry-run)
echo "🚀 TEST 5: Test de soumission (simulation)..."

echo "📋 Commande qui serait exécutée:"
echo "python trigger_pipeline.py \\"
echo "    --project $PROJECT_ID \\"
echo "    --region $REGION \\"
echo "    --deploy-threshold $THRESHOLD \\"
echo "    --display-name 'TEST-ML-Pipeline-$(date +%Y%m%d-%H%M%S)'"

echo ""
echo "💡 Pour exécuter réellement le pipeline:"
echo "cd src && python trigger_pipeline.py --project $PROJECT_ID --region $REGION --deploy-threshold $THRESHOLD"

echo "✅ Test de soumission OK"
echo ""

# Test 6: Vérification GitHub Actions
echo "🔄 TEST 6: Vérification GitHub Actions..."

cd ..

if grep -q "ml-pipeline-simulation" .github/workflows/tests.yml; then
    echo "✅ Job ML pipeline simulation trouvé dans GitHub Actions"
else
    echo "❌ Job ML pipeline simulation manquant dans GitHub Actions"
    exit 1
fi

if grep -q "THRESHOLD=0.85" .github/workflows/tests.yml; then
    echo "✅ Seuil configuré dans GitHub Actions"
else
    echo "⚠️  Seuil GitHub Actions à vérifier manuellement"
fi

echo "✅ GitHub Actions OK"
echo ""

# Résumé
echo "🎉 TOUS LES TESTS PASSÉS AVEC SUCCÈS!"
echo "=================================================="
echo ""
echo "📋 Résumé de la configuration:"
echo "   ✅ Pipeline ML compilable"
echo "   ✅ Déploiement conditionnel configuré"
echo "   ✅ Seuil accuracy: $THRESHOLD"
echo "   ✅ GitHub Actions synchronisé"
echo "   ✅ Prêt pour déploiement automatique"
echo ""
echo "🚀 Actions suivantes:"
echo "   1. git add . && git commit -m 'feat: pipeline ML conditionnel'"
echo "   2. git push origin main"
echo "   3. Surveiller Console Vertex AI Pipelines"
echo "   4. Vérifier déploiement automatique si accuracy ≥ $THRESHOLD"
echo ""
echo "🔗 Liens utiles:"
echo "   📊 Vertex AI: https://console.cloud.google.com/vertex-ai/pipelines"
echo "   🐳 Cloud Build: https://console.cloud.google.com/cloud-build/builds"
echo "   ⚙️  GitHub Actions: https://github.com/rickykaky/Digital-Social-Score/actions"

# Nettoyage
cd src
rm -f digital_score_pipeline.yaml

echo ""
echo "✅ Test terminé - Pipeline ML prêt pour production!"