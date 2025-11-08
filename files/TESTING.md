# Testing Framework - Digital Social Score

## 📋 Vue d'ensemble

Ce projet utilise **pytest** comme framework de test avec une structure organisée pour supporter tests unitaires, intégration, pipeline, et ML.

## 🏗️ Structure des Tests

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures partagées
├── pytest.ini                     # Configuration pytest (au niveau racine)
├── unit/                          # Tests unitaires
│   ├── __init__.py
│   ├── test_anonymization.py      # Tests regex + NER
│   ├── test_preprocessing.py      # Tests NLTK
│   └── test_model.py              # Tests modèle
├── integration/                   # Tests d'intégration
│   ├── __init__.py
│   └── test_api_endpoints.py      # Tests FastAPI
├── pipeline/                      # Tests pipeline KFP
│   ├── __init__.py
│   └── test_pipeline_components.py
├── ml/                            # Tests machine learning
│   ├── __init__.py
│   └── test_evaluator.py          # Tests métriques
└── fixtures/                      # Données de test
    ├── __init__.py
    └── sample_data.csv
```

## 🔧 Fixtures Disponibles

Les fixtures sont définies dans `conftest.py` :

### Données
- `sample_comments_df()`: DataFrame avec 5 commentaires (toxic/non-toxic)
- `sample_pii_comments()`: Commentaires avec PII (emails, téléphones, etc.)
- `sample_empty_comments()`: Commentaires vides/invalides
- `sample_large_comments()`: Textes de 5000+ caractères

### Modèle
- `mock_vectorizer()`: TF-IDF vectorizer mock
- `mock_model()`: LogisticRegression mock
- `model_artifacts()`: Modèle et vectorizer réels sérialisés

### Fichiers
- `temp_csv()`: Fichier CSV temporaire
- `temp_model_files()`: Répertoire temporaire pour modèles

### API
- `api_client()`: Client HTTP TestClient
- `sample_api_payload()`: Payload standard

## 📝 Markers de Tests

Les tests sont catégorisés avec des markers pytest :

```bash
# Exécuter uniquement les tests unitaires
pytest -m unit

# Tests d'intégration
pytest -m integration

# Tests ML
pytest -m ml

# Tests API
pytest -m api

# Tests pipeline
pytest -m pipeline

# Tests lents (performance)
pytest -m slow

# Smoke tests (rapides)
pytest -m smoke

# Exclure les tests lents
pytest -m "not slow"
```

## 🚀 Utilisation

### Installation des dépendances de test

```bash
pip install -r requirements-test.txt
```

### Exécuter tous les tests

```bash
pytest
# ou
make test
```

### Exécuter par catégorie

```bash
# Tests unitaires
make test-unit

# Tests d'intégration
make test-integration

# Tests pipeline
make test-pipeline

# Tests ML
make test-ml

# Tests API
make test-api

# Smoke tests (rapides)
make test-smoke

# Mode watch (réexécute à chaque changement)
make test-watch
```

### Rapport de couverture

```bash
# Générer un rapport de couverture
make coverage

# Rapport HTML
make coverage-html
```

Ouvre automatiquement le rapport dans `htmlcov/index.html`.

### Lint et Quality

```bash
# Formater le code
make format

# Vérifier le format (sans modifier)
make format-check

# Linter
make lint

# Vérification de type
make type-check

# Sécurité
make security
```

## 📊 Structure des Tests Unitaires

### `tests/unit/test_anonymization.py`

Teste les patterns regex et les fonctions d'anonymisation :

```python
class TestRegexPatterns:
    # Détection d'emails
    def test_email_regex_detection(self)
    
    # Détection de téléphones
    def test_phone_regex_detection(self)
    
    # Détection de cartes de crédit
    def test_credit_card_regex_detection(self)

class TestAnonymizationFunctions:
    # Tests du masquage
    def test_mask_regex_pii_replaces_emails(self)
    def test_mask_regex_pii_replaces_phone(self)
    # ... etc

class TestEdgeCases:
    # Cas limites
    def test_very_long_text(self)
    def test_special_characters_in_text(self)
    def test_unicode_characters(self)
```

## 🧪 Tests d'Intégration API

### `tests/integration/test_api_endpoints.py`

Teste les endpoints FastAPI :

```python
class TestAPIHealthCheck:
    def test_health_endpoint_exists(self)
    def test_health_endpoint_format(self)

class TestAnonymizeEndpoint:
    def test_anonymize_endpoint_with_valid_payload(self)
    def test_anonymize_endpoint_masks_email(self)
    # ... etc

class TestScoreEndpoint:
    def test_score_endpoint_with_valid_payload(self)
    def test_score_endpoint_returns_valid_score_range(self)

class TestCORSHeaders:
    def test_cors_headers_present(self)

class TestRequestValidation:
    def test_payload_with_extra_fields(self)
    def test_payload_with_wrong_type(self)
    def test_very_long_text(self)
```

## 🔄 Tests Pipeline

### `tests/pipeline/test_pipeline_components.py`

Teste les composants KFP :

```python
class TestPrepareDataComponent:
    def test_prepare_data_component_input_validation(self)
    def test_prepare_data_component_with_missing_data(self)
    def test_prepare_data_component_nltk_processing(self)

class TestTrainModelComponent:
    def test_train_model_component_vectorizer_initialization(self)
    def test_train_model_component_produces_valid_model(self)
    def test_train_model_component_produces_predictions(self)

class TestEvaluateModelComponent:
    def test_evaluate_model_accuracy(self)
    def test_evaluate_model_precision_recall_f1(self)
    def test_evaluate_model_confusion_matrix(self)

class TestComponentIntegration:
    def test_prepare_to_train_data_flow(self)
    def test_train_to_evaluate_model_flow(self)
```

## 📋 Configuration pytest.ini

Le fichier `pytest.ini` configure :

- **testpaths**: Répertoire `tests/`
- **Nommage**: `test_*.py` et `*_test.py`
- **Markers**: unit, integration, slow, ml, api, pipeline
- **Coverage**: Rapports par défaut
- **Logs**: Fichier `tests/logs/pytest.log`

## ⚡ Commandes Rapides

```bash
# Installer toutes les dépendances
make install-all

# Exécuter les tests + coverage + lint
make ci

# Pre-commit: format + lint + unit tests
make pre-commit

# Nettoyer les artefacts
make clean

# Aide
make help
```

## 🔍 Debugging Tests

### Exécuter un test spécifique en verbeux

```bash
pytest tests/unit/test_anonymization.py::TestRegexPatterns::test_email_regex_detection -vv
```

### Arrêter à la première erreur

```bash
pytest -x
```

### Passer des arguments pytest

```bash
pytest -v --tb=long --capture=no
```

### Voir les prints dans les tests

```bash
pytest -s
```

## 📌 Bonnes Pratiques

1. **Nommer les tests clairement** : `test_<fonctionnalité>_<cas>`
2. **Utiliser des fixtures** : Éviter la duplication, utiliser `conftest.py`
3. **Tests indépendants** : Chaque test doit être autonome
4. **Tester les cas limites** : Empty, None, très grands, caractères spéciaux
5. **Mocking externe** : Mocker les appels GCS, Vertex AI
6. **Markers** : Tagguer correctement chaque test

## 🚨 Troubleshooting

### ImportError: No module named 'pytest'

```bash
pip install -r requirements-test.txt
```

### Tests échouent avec "fixture not found"

Vérifier que `conftest.py` est dans le répertoire `tests/`.

### Coverage report empty

```bash
pytest --cov=src --cov-report=term-missing
```

### Tests trop lents

```bash
# Exclure les tests lents
pytest -m "not slow"
```

## 📚 Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [TestClient FastAPI](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [Sklearn Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)

## 🎯 Métriques de Qualité

Objectifs minimaux pour le merge :

- ✅ Tous les tests passent
- ✅ Coverage > 80%
- ✅ Pas de warnings pylint
- ✅ Code formaté (black)
- ✅ Pas d'erreurs mypy (type checking)
