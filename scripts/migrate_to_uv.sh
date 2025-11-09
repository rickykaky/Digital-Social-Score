#!/bin/bash
# migrate_to_uv.sh - Migration vers uv package manager

echo "🚀 Migration vers uv (package manager ultra-rapide)"
echo "=================================================="

# 1. Installer uv si pas déjà fait
if ! command -v uv &> /dev/null; then
    echo "📦 Installation d'uv..."
    pip install uv
else
    echo "✅ uv déjà installé"
fi

# 2. Créer uv.lock si pyproject.toml existe
if [ -f "pyproject.toml" ]; then
    echo "🔒 Génération du fichier de lock..."
    uv lock
    echo "✅ uv.lock créé"
fi

# 3. Test d'installation avec uv
echo "🧪 Test d'installation des dépendances..."
if [ -f "requirements.txt" ]; then
    echo "   - Installation avec requirements.txt..."
    time uv pip install --system -r requirements.txt
    
    if [ -f "requirements-test.txt" ]; then
        echo "   - Installation des dépendances de test..."
        time uv pip install --system -r requirements-test.txt
    fi
else
    echo "   - Installation avec pyproject.toml..."
    time uv sync
fi

# 4. Comparaison de performance
echo ""
echo "📊 COMPARAISON DE PERFORMANCE"
echo "============================="
echo "🐌 pip install : ~60-120 secondes (typique)"
echo "🚀 uv install  : ~5-15 secondes (10-100x plus rapide)"
echo ""
echo "✅ Migration vers uv terminée !"
echo ""
echo "💡 Prochaines étapes :"
echo "   1. Tester vos builds localement"
echo "   2. Valider que GitHub Actions/Cloud Build fonctionnent"
echo "   3. Profiter de builds 10x plus rapides !"