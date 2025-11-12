#!/usr/bin/env python3
"""
Script de test pour vérifier la logique de résolution des chemins
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire src au Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import config

def test_path_resolution():
    """Test la résolution des chemins dans différents contextes"""
    print("=== TEST DE RÉSOLUTION DES CHEMINS ===")
    print()
    
    # Informations sur l'environnement
    print("📍 ENVIRONNEMENT ACTUEL:")
    print(f"   - Répertoire courant: {Path.cwd()}")
    print(f"   - Script path: {Path(__file__).resolve()}")
    print(f"   - GITHUB_WORKSPACE: {os.environ.get('GITHUB_WORKSPACE', 'Non défini')}")
    print(f"   - CI: {os.environ.get('CI', 'Non défini')}")
    print()
    
    # Configuration calculée
    print("🔧 CONFIGURATION CALCULÉE:")
    print(f"   - BASE_DIR: {config.BASE_DIR}")
    print(f"   - MODELS_DIR: {config.MODELS_DIR}")
    print(f"   - DATA_DIR: {config.DATA_DIR}")
    print()
    
    # Chemins des modèles
    print("📦 CHEMINS DES MODÈLES:")
    model_path = config.get_model_path()
    vectorizer_path = config.get_vectorizer_path()
    print(f"   - model_path: {model_path}")
    print(f"   - vectorizer_path: {vectorizer_path}")
    print(f"   - Le dossier models existe: {model_path.parent.exists()}")
    print()
    
    # Vérification des fichiers existants
    print("🔍 VÉRIFICATION DES MODÈLES EXISTANTS:")
    
    # Chemins possibles où chercher
    possible_paths = [
        config.BASE_DIR / "models",
        config.BASE_DIR / "src" / "models", 
        Path.cwd() / "models",
        Path.cwd() / "src" / "models",
    ]
    
    for path in possible_paths:
        print(f"   - {path}: {path.exists()}")
        if path.exists():
            files = list(path.glob("*.pkl"))
            print(f"     Fichiers .pkl: {[f.name for f in files]}")
    
    print()
    print("=== FIN DU TEST ===")

if __name__ == "__main__":
    test_path_resolution()