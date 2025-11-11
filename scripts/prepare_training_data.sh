#!/bin/bash
# Script de préparation des données d'entraînement
# Fichier: scripts/prepare_training_data.sh

set -e

echo "🔍 Vérification des données d'entraînement..."

DATA_DIR="data"
TRAINING_FILE="$DATA_DIR/cleaned_training_sample.csv"
SOURCE_FILE="$DATA_DIR/prod.csv"
FALLBACK_FILE="train.csv/train.csv"

# Créer le dossier data s'il n'existe pas
mkdir -p "$DATA_DIR"

# Si le fichier d'entraînement existe déjà
if [ -f "$TRAINING_FILE" ]; then
    echo "✅ Fichier d'entraînement trouvé: $TRAINING_FILE"
    
    # Afficher quelques stats
    LINES=$(wc -l < "$TRAINING_FILE" 2>/dev/null || echo "0")
    echo "📊 Nombre de lignes: $LINES"
    
    if [ "$LINES" -gt 1 ]; then
        echo "✅ Fichier d'entraînement prêt pour l'utilisation"
        exit 0
    else
        echo "⚠️ Fichier d'entraînement vide, préparation nécessaire..."
    fi
fi

# Chercher une source de données
echo "🔍 Recherche de données source..."

if [ -f "$SOURCE_FILE" ]; then
    echo "✅ Fichier source trouvé: $SOURCE_FILE"
    SOURCE="$SOURCE_FILE"
elif [ -f "$FALLBACK_FILE" ]; then
    echo "✅ Fichier fallback trouvé: $FALLBACK_FILE"
    SOURCE="$FALLBACK_FILE"
else
    echo "❌ Aucun fichier de données trouvé!"
    echo "   Cherché: $SOURCE_FILE, $FALLBACK_FILE"
    
    # Créer un fichier d'exemple minimal
    echo "🔧 Création d'un dataset d'exemple minimal..."
    cat > "$TRAINING_FILE" << 'EOF'
comment_text,toxic,severe_toxic,obscene,threat,insult,identity_hate
"You are awesome!",0,0,0,0,0,0
"This is great work",0,0,0,0,0,0
"I love this project",0,0,0,0,0,0
"This sucks badly",1,0,1,0,1,0
"You are an idiot",1,0,0,0,1,0
"I hate everything",1,0,0,0,0,0
"Fantastic job everyone",0,0,0,0,0,0
"This is terrible work",1,0,0,0,0,0
"Well done team",0,0,0,0,0,0
"Complete garbage",1,0,0,0,1,0
EOF
    
    echo "✅ Dataset d'exemple créé: $TRAINING_FILE"
    echo "📊 $(wc -l < "$TRAINING_FILE") lignes créées"
    exit 0
fi

# Traitement des données source
echo "🔄 Préparation des données d'entraînement depuis $SOURCE..."

# Utiliser Python pour nettoyer et préparer les données
python3 -c "
import pandas as pd
import sys

print('📊 Chargement des données...')
try:
    df = pd.read_csv('$SOURCE')
    print(f'   Données chargées: {len(df)} lignes, {len(df.columns)} colonnes')
    print(f'   Colonnes: {list(df.columns)}')
    
    # Colonnes de texte possibles
    text_cols = ['comment_text', 'anonymized_comment', 'text']
    text_col = None
    for col in text_cols:
        if col in df.columns:
            text_col = col
            break
    
    if text_col is None:
        print('❌ Aucune colonne de texte trouvée')
        sys.exit(1)
    
    print(f'✅ Colonne de texte: {text_col}')
    
    # Colonnes de toxicité
    tox_cols = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    available_tox = [col for col in tox_cols if col in df.columns]
    
    if not available_tox:
        print('⚠️ Aucune colonne de toxicité, création de labels synthétiques...')
        df['toxic'] = 0  # Par défaut non-toxique
        available_tox = ['toxic']
    
    print(f'✅ Colonnes toxicité: {available_tox}')
    
    # Nettoyer les données
    df = df.dropna(subset=[text_col])
    df = df[df[text_col].str.strip() != '']
    
    # Échantillonnage si trop de données
    if len(df) > 10000:
        print(f'📉 Échantillonnage: {len(df)} → 10000 lignes')
        df = df.sample(n=10000, random_state=42)
    
    # Sélectionner les colonnes importantes
    cols_to_keep = [text_col] + available_tox
    if 'id' in df.columns:
        cols_to_keep = ['id'] + cols_to_keep
    
    df_clean = df[cols_to_keep].copy()
    
    # Renommer la colonne de texte si nécessaire
    if text_col != 'comment_text':
        df_clean = df_clean.rename(columns={text_col: 'comment_text'})
    
    # Sauvegarder
    df_clean.to_csv('$TRAINING_FILE', index=False)
    print(f'✅ Dataset nettoyé sauvegardé: $TRAINING_FILE')
    print(f'📊 Lignes finales: {len(df_clean)}')
    print(f'📊 Colonnes finales: {list(df_clean.columns)}')
    
except Exception as e:
    print(f'❌ Erreur: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Préparation des données terminée avec succès!"
    echo "📄 Fichier prêt: $TRAINING_FILE"
else
    echo "❌ Erreur lors de la préparation des données"
    exit 1
fi