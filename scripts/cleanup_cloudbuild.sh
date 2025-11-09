#!/bin/bash

# Script de nettoyage des fichiers Cloud Build
# Supprime les fichiers obsolètes et garde seulement les essentiels

echo "🧹 Nettoyage des fichiers Cloud Build..."

# Supprimer les fichiers temporaires/obsolètes
echo "❌ Suppression des fichiers obsolètes..."

# Fichier de test temporaire
if [ -f "cloudbuild-simple.yaml" ]; then
    rm cloudbuild-simple.yaml
    echo "  ✅ cloudbuild-simple.yaml supprimé"
fi

# Ancien fichier dans src/
if [ -f "src/cloudbuild.yaml" ]; then
    rm src/cloudbuild.yaml
    echo "  ✅ src/cloudbuild.yaml supprimé"
fi

# Fichier dans train.csv/ (mauvais emplacement)
if [ -f "train.csv/cloudbuild.yaml" ]; then
    rm train.csv/cloudbuild.yaml
    echo "  ✅ train.csv/cloudbuild.yaml supprimé"
fi

# Fichier de configuration temporaire
if [ -f "trigger-config.json" ]; then
    rm trigger-config.json
    echo "  ✅ trigger-config.json supprimé"
fi

# Vérifier le fichier vide dans ci_cd
if [ -f "ci_cd/cloud_build/cloudbuild-pipeline.yaml" ] && [ ! -s "ci_cd/cloud_build/cloudbuild-pipeline.yaml" ]; then
    rm ci_cd/cloud_build/cloudbuild-pipeline.yaml
    echo "  ✅ ci_cd/cloud_build/cloudbuild-pipeline.yaml (vide) supprimé"
fi

echo ""
echo "✅ FICHIERS ESSENTIELS CONSERVÉS:"
echo "  📋 cloudbuild.yaml (PRINCIPAL - Configuration Cloud Build)"
echo "  📚 TRIGGER_SETUP_GUIDE.md (Guide de configuration)"

echo ""
echo "📚 FICHIERS DOCUMENTATION (optionnels):"
echo "  📄 CLOUDBUILD_FIX.md (Documentation technique)"
echo "  📄 SOLUTION_FINALE.md (Résumé complet)"
echo "  📄 COHERENCE_REPORT.md (Rapport de cohérence)"

echo ""
echo "❓ VOULEZ-VOUS SUPPRIMER LES DOCS OPTIONNELLES? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    [ -f "CLOUDBUILD_FIX.md" ] && rm CLOUDBUILD_FIX.md && echo "  ✅ CLOUDBUILD_FIX.md supprimé"
    [ -f "SOLUTION_FINALE.md" ] && rm SOLUTION_FINALE.md && echo "  ✅ SOLUTION_FINALE.md supprimé"
    echo "📚 Documentation technique supprimée (TRIGGER_SETUP_GUIDE.md conservé)"
else
    echo "📚 Documentation complète conservée"
fi

echo ""
echo "🎯 CONFIGURATION FINALE:"
echo "  ✅ cloudbuild.yaml - Configuration principale Cloud Build"
echo "  ✅ TRIGGER_SETUP_GUIDE.md - Guide utilisateur"
if [ -f "COHERENCE_REPORT.md" ]; then
    echo "  ✅ COHERENCE_REPORT.md - Rapport de cohérence du projet"
fi

echo ""
echo "🚀 PRÊT POUR LA PRODUCTION!"
echo "👉 Suivez TRIGGER_SETUP_GUIDE.md pour créer le déclencheur"

# Commit automatique si dans un repo git
if [ -d ".git" ]; then
    echo ""
    echo "📝 Commit des changements? (y/N)"
    read -r commit_response
    if [[ "$commit_response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        git add .
        git commit -m "Clean: Nettoyage des fichiers Cloud Build obsolètes

- Suppression des doublons et fichiers temporaires
- Conservation de la configuration principale
- Documentation essentielle préservée"
        echo "✅ Changements committes"
    fi
fi