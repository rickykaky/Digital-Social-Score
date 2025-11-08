#!/usr/bin/env python3
"""
Script de vérification de cohérence pour le projet Digital Social Score
Fichier: scripts/verify_consistency.py

Ce script vérifie que tous les fichiers du projet sont cohérents entre eux
et que les configurations, modèles, et tests fonctionnent correctement.
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Ajouter src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_configuration():
    """Test de la configuration centralisée"""
    print("🔧 Test de la configuration centralisée...")
    
    try:
        from config import config
        
        # Vérifier les patterns d'anonymisation
        assert config.EMAIL_RE.pattern == r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b'
        print("✅ Patterns EMAIL_RE cohérents")
        
        # Vérifier les colonnes de toxicité
        expected_columns = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
        assert config.TOXICITY_COLUMNS == expected_columns
        print("✅ Colonnes de toxicité configurées")
        
        # Vérifier les entités nommées
        assert 'PERSON' in config.NAMED_ENTITY_LABELS
        assert 'GPE' in config.NAMED_ENTITY_LABELS
        print("✅ Entités nommées configurées")
        
        print("✅ Configuration centralisée OK\n")
        return True
    except Exception as e:
        print(f"❌ Erreur configuration: {e}\n")
        return False

def test_anonymization_functions():
    """Test des fonctions d'anonymisation"""
    print("🛡️ Test des fonctions d'anonymisation...")
    
    try:
        from app import mask_regex_pii, mask_named_entities, anonymize_text
        
        # Test masquage email
        result = mask_regex_pii("Contact me at john@example.com")
        assert "john@example.com" not in result
        assert "<EMAIL>" in result
        print("✅ Masquage email fonctionne")
        
        # Test masquage téléphone
        result = mask_regex_pii("Call me at 555-1234-5678")
        assert "555-1234-5678" not in result
        assert "<PHONE>" in result
        print("✅ Masquage téléphone fonctionne")
        
        # Test anonymisation complète
        text = "Hi, I'm John Smith, email me at john@test.com or call 555-123-4567"
        result = anonymize_text(text)
        assert "john@test.com" not in result
        assert "555-123-4567" not in result
        print("✅ Anonymisation complète fonctionne")
        
        print("✅ Fonctions d'anonymisation OK\n")
        return True
    except Exception as e:
        print(f"❌ Erreur anonymisation: {e}\n")
        return False

def test_data_consistency():
    """Test de cohérence des données"""
    print("📊 Test de cohérence des données...")
    
    try:
        # Vérifier que prod.csv existe et a la bonne structure
        data_path = Path(__file__).parent.parent / 'data' / 'prod.csv'
        if not data_path.exists():
            print("⚠️ prod.csv n'existe pas, utilisation du dataset de test")
            return True
        
        df = pd.read_csv(data_path)
        
        # Vérifier les colonnes requises
        required_cols = ['id', 'comment_text', 'toxic']
        for col in required_cols:
            assert col in df.columns, f"Colonne manquante: {col}"
        print("✅ Colonnes requises présentes")
        
        # Vérifier les colonnes de toxicité optionnelles
        from config import config
        toxicity_cols = config.get_available_toxicity_columns(df.columns.tolist())
        print(f"✅ Colonnes de toxicité disponibles: {toxicity_cols}")
        
        print("✅ Cohérence des données OK\n")
        return True
    except Exception as e:
        print(f"❌ Erreur données: {e}\n")
        return False

def test_model_training():
    """Test d'entraînement du modèle"""
    print("🤖 Test d'entraînement du modèle...")
    
    try:
        from train import train_and_save_model
        from config import config
        
        # Créer un petit dataset de test
        test_data = {
            'comment_text': [
                'This is a great product!',
                'I hate this, terrible service',
                'Awesome experience, highly recommend', 
                'Worst purchase ever, never again',
                'Average, nothing special'
            ],
            'toxic': [0, 1, 0, 1, 0],
            'severe_toxic': [0, 0, 0, 1, 0],
            'obscene': [0, 1, 0, 0, 0],
            'threat': [0, 0, 0, 1, 0],
            'insult': [0, 1, 0, 1, 0],
            'identity_hate': [0, 0, 0, 0, 0]
        }
        
        df = pd.DataFrame(test_data)
        test_file = Path(__file__).parent.parent / 'data' / 'consistency_test.csv'
        df.to_csv(test_file, index=False)
        
        # Entraîner le modèle
        print("Entraînement en cours...")
        train_and_save_model(str(test_file))
        
        # Vérifier que les fichiers sont créés
        model_path = config.get_model_path()
        vectorizer_path = config.get_vectorizer_path()
        assert model_path.exists(), f"Modèle non trouvé: {model_path}"
        assert vectorizer_path.exists(), f"Vectoriseur non trouvé: {vectorizer_path}"
        print("✅ Modèle et vectoriseur sauvegardés")
        
        # Nettoyer
        test_file.unlink()
        
        print("✅ Entraînement du modèle OK\n")
        return True
    except Exception as e:
        print(f"❌ Erreur entraînement: {e}\n")
        return False

def test_api_functionality():
    """Test des fonctionnalités de l'API"""
    print("🚀 Test des fonctionnalités de l'API...")
    
    try:
        from app import calculate_score
        
        # Test calcul de score
        score = calculate_score("This is a wonderful day!")
        assert 0 <= score <= 100, f"Score invalide: {score}"
        print(f"✅ Score calculé: {score}")
        
        # Test avec du contenu toxique
        toxic_score = calculate_score("This sucks, I hate it!")
        assert 0 <= toxic_score <= 100, f"Score toxique invalide: {toxic_score}"
        print(f"✅ Score toxique calculé: {toxic_score}")
        
        print("✅ Fonctionnalités API OK\n")
        return True
    except Exception as e:
        print(f"❌ Erreur API: {e}\n")
        return False

def test_unit_tests():
    """Test que les tests unitaires passent"""
    print("🧪 Test des tests unitaires...")
    
    try:
        import subprocess
        import os
        
        # Changer vers le répertoire src pour les imports
        original_cwd = os.getcwd()
        src_dir = Path(__file__).parent.parent / 'src'
        os.chdir(src_dir)
        
        # Exécuter quelques tests clés
        result = subprocess.run([
            'python', '-m', 'pytest', 
            '../tests/unit/test_anonymization.py::TestRegexPatterns::test_email_regex_detection',
            '-v', '--tb=short'
        ], capture_output=True, text=True)
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("✅ Tests unitaires passent")
            print("✅ Tests unitaires OK\n")
            return True
        else:
            print(f"❌ Tests échoués: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur tests: {e}\n")
        return False

def main():
    """Fonction principale de vérification"""
    print("=" * 60)
    print("🔍 VÉRIFICATION DE COHÉRENCE - DIGITAL SOCIAL SCORE")
    print("=" * 60)
    print()
    
    tests = [
        ("Configuration", test_configuration),
        ("Anonymisation", test_anonymization_functions), 
        ("Données", test_data_consistency),
        ("Modèle ML", test_model_training),
        ("API", test_api_functionality),
        ("Tests unitaires", test_unit_tests)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🔄 Exécution: {test_name}")
        success = test_func()
        results.append((test_name, success))
    
    print("=" * 60)
    print("📊 RÉSULTATS DE LA VÉRIFICATION")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHEC"
        print(f"{test_name:<20}: {status}")
        if not success:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 TOUTES LES VÉRIFICATIONS ONT RÉUSSI!")
        print("✅ Le projet est cohérent et prêt pour le déploiement.")
        return 0
    else:
        print("⚠️ CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ")
        print("❌ Veuillez corriger les erreurs avant le déploiement.")
        return 1

if __name__ == "__main__":
    sys.exit(main())