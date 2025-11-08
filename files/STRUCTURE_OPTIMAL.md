# 📂 Structure Optimale du Projet Digital Social Score - MLOps

## 🎯 Objectif
Structure conforme aux standards MLOps avec séparation claire entre :
- Code métier
- Pipeline d'entraînement
- API/Serveur
- Tests unitaires
- Tests de validation
- Configuration Cloud

---

## 📁 Structure complète recommandée

```
Digital-Social-Score/
│
├── 📄 README.md                          # Documentation principale
├── 📄 CONTRIBUTING.md                    # Guides contribution
├── 📄 setup.py                           # Installation du package
├── 📄 pyproject.toml                     # Config projet (Python 3.11+)
├── 📋 requirements.txt                   # Dépendances production
├── 📋 requirements-dev.txt               # Dépendances développement
├── 📋 requirements-test.txt              # Dépendances tests
│
├── 📁 src/                               # Code source
│   │
│   ├── 📁 digital_social_score/          # Package principal
│   │   ├── __init__.py
│   │   │
│   │   ├── 📁 core/                      # Logique métier
│   │   │   ├── __init__.py
│   │   │   ├── anonymization.py          # Masquage des données personnelles
│   │   │   ├── preprocessing.py          # Nettoyage NLTK
│   │   │   ├── vectorization.py          # TF-IDF vectorisation
│   │   │   └── model.py                  # Logique du modèle
│   │   │
│   │   ├── 📁 ml/                        # Entraînement & Évaluation
│   │   │   ├── __init__.py
│   │   │   ├── trainer.py                # Entraînement du modèle
│   │   │   ├── evaluator.py              # Métriques & Évaluation
│   │   │   └── hyperparameters.py        # Config hyperparamètres
│   │   │
│   │   ├── 📁 pipeline/                  # Pipeline Vertex AI / KFP
│   │   │   ├── __init__.py
│   │   │   ├── components.py             # Composants KFP (prepare, train, eval)
│   │   │   ├── pipeline.py               # Pipeline principal
│   │   │   └── config.py                 # Config pipeline
│   │   │
│   │   ├── 📁 api/                       # API FastAPI
│   │   │   ├── __init__.py
│   │   │   ├── app.py                    # Application FastAPI
│   │   │   ├── schemas.py                # Pydantic models
│   │   │   ├── endpoints.py              # Routes API
│   │   │   └── middleware.py             # CORS, auth, logging
│   │   │
│   │   ├── 📁 utils/                     # Utilitaires
│   │   │   ├── __init__.py
│   │   │   ├── logger.py                 # Logging configuré
│   │   │   ├── gcs.py                    # Interactions GCS
│   │   │   ├── config.py                 # Variables d'environnement
│   │   │   └── metrics.py                # Calculs de métriques
│   │   │
│   │   └── 📁 data/                      # Gestion des données
│   │       ├── __init__.py
│   │       ├── loader.py                 # Chargement des données
│   │       ├── validation.py             # Validation des données
│   │       └── versioning.py             # Version contrôle des données
│   │
│   ├── 📄 train.py                       # Script d'entraînement local
│   ├── 📄 submit_pipeline.py             # Soumission Vertex AI
│   ├── 📄 app.py                         # API (wrapper)
│   │
│   └── 📁 config/                        # Fichiers de configuration
│       ├── __init__.py
│       ├── base.py                       # Config de base
│       ├── development.py                # Config développement
│       ├── production.py                 # Config production
│       └── testing.py                    # Config tests
│
│
├── 📁 tests/                             # Suite de tests
│   ├── __init__.py
│   ├── conftest.py                       # Fixtures pytest
│   │
│   ├── 📁 unit/                          # Tests unitaires
│   │   ├── __init__.py
│   │   ├── test_core_anonymization.py
│   │   ├── test_core_preprocessing.py
│   │   ├── test_core_vectorization.py
│   │   ├── test_core_model.py
│   │   └── test_utils.py
│   │
│   ├── 📁 integration/                   # Tests d'intégration
│   │   ├── __init__.py
│   │   ├── test_pipeline_flow.py         # Flux complet
│   │   ├── test_api_endpoints.py         # Endpoints API
│   │   └── test_data_validation.py       # Validation données
│   │
│   ├── 📁 pipeline/                      # Tests du pipeline KFP
│   │   ├── __init__.py
│   │   ├── test_pipeline_components.py   # Composants individuels
│   │   ├── test_pipeline_submission.py   # Soumission à Vertex AI
│   │   └── test_pipeline_outputs.py      # Validation outputs
│   │
│   ├── 📁 ml/                            # Tests ML/Modèle
│   │   ├── __init__.py
│   │   ├── test_trainer.py               # Entraînement
│   │   ├── test_evaluator.py             # Évaluation
│   │   └── test_model_metrics.py         # Métriques
│   │
│   └── 📁 fixtures/                      # Données de test
│       ├── sample_data.csv
│       ├── sample_comments.json
│       └── mock_models/
│
│
├── 📁 notebooks/                         # Jupyter notebooks (optionnel)
│   ├── 01_eda.ipynb                      # Exploratory Data Analysis
│   ├── 02_preprocessing.ipynb
│   ├── 03_model_development.ipynb
│   └── 04_validation.ipynb
│
│
├── 📁 deployment/                        # Fichiers Kubernetes & Cloud
│   ├── 📁 k8s/
│   │   ├── deployment.yaml               # Déploiement GKE
│   │   ├── service.yaml                  # Service Kubernetes
│   │   └── hpa.yaml                      # Auto-scaling horizontal
│   │
│   ├── 📁 docker/
│   │   ├── Dockerfile                    # Image API
│   │   ├── Dockerfile.pipeline           # Image pipeline (optionnel)
│   │   └── .dockerignore
│   │
│   └── cloudbuild.yaml                   # CI/CD Cloud Build
│
│
├── 📁 scripts/                           # Scripts utilitaires
│   ├── setup_gcs.sh                      # Setup bucket GCS
│   ├── setup_gke.sh                      # Setup cluster GKE
│   ├── run_local_tests.sh                # Exécuter tests localement
│   ├── run_pipeline_local.sh             # Exécuter pipeline localement
│   └── generate_reports.py               # Générer rapports de tests
│
│
├── 📁 docs/                              # Documentation complète
│   ├── ARCHITECTURE.md                   # Architecture système
│   ├── PIPELINE_SETUP.md                 # Setup pipeline MLOps
│   ├── API_REFERENCE.md                  # Documentation API
│   ├── DEPLOYMENT.md                     # Guide déploiement
│   ├── TESTING_GUIDE.md                  # Guide tests
│   ├── TROUBLESHOOTING.md                # Dépannage
│   └── PERFORMANCE.md                    # Benchmarks & perf
│
│
├── 📁 data/                              # Données (locales)
│   ├── raw/                              # Données brutes
│   │   └── train.csv
│   ├── processed/                        # Données traitées
│   │   └── train_processed.csv
│   ├── test/                             # Données de test
│   │   └── test_samples.csv
│   └── .gitkeep
│
│
├── 📁 models/                            # Modèles sauvegardés
│   ├── model_v1.joblib
│   ├── vectorizer_v1.joblib
│   └── metadata.json
│
│
├── 📁 logs/                              # Logs d'exécution
│   ├── training.log
│   ├── api.log
│   └── pipeline.log
│
│
└── 📁 ci_cd/                             # Configuration CI/CD
    ├── github_actions/                   # GitHub Actions (optionnel)
    │   └── workflows/
    │       ├── test.yml
    │       ├── build.yml
    │       └── deploy.yml
    │
    └── cloud_build/                      # Google Cloud Build
        ├── cloudbuild.yaml
        └── cloudbuild-pipeline.yaml      # Build séparé pour pipeline

```

---

## 🔑 Points clés de cette structure

### ✅ **1. Organisation par domaine (Package src/)**
- `core/` → Logique métier (anonymization, preprocessing)
- `ml/` → Entraînement et évaluation
- `pipeline/` → Pipeline Vertex AI / KFP
- `api/` → Endpoints FastAPI
- `utils/` → Utilitaires réutilisables
- `data/` → Gestion des données

### ✅ **2. Tests organisés par catégorie (tests/)**
- `unit/` → Tests unitaires (fonctions individuelles)
- `integration/` → Tests d'intégration (flux complets)
- `pipeline/` → Tests spécifiques au pipeline KFP
- `ml/` → Tests du modèle et entraînement
- `fixtures/` → Données de test

### ✅ **3. Configuration centralisée**
```
src/config/
├── base.py              # Paramètres communs
├── development.py       # Overrides dev
├── production.py        # Overrides prod
└── testing.py          # Overrides tests
```

### ✅ **4. Déploiement modulaire**
```
deployment/
├── k8s/               # Kubernetes manifests
├── docker/            # Images Docker
└── cloudbuild.yaml    # CI/CD orchestration
```

### ✅ **5. Documentation complète**
```
docs/
├── ARCHITECTURE.md     # Vue d'ensemble
├── PIPELINE_SETUP.md   # MLOps spécifique
├── TESTING_GUIDE.md    # Comment tester
└── DEPLOYMENT.md       # Déploiement
```

---

## 📝 Fichiers importants à créer

### **`src/digital_social_score/__init__.py`**
```python
__version__ = "1.0.0"
__author__ = "Digital Social Score Team"
```

### **`src/config/base.py`**
```python
import os
from pathlib import Path

class Config:
    """Configuration de base"""
    PROJECT_NAME = "digital-social-score"
    VERSION = "1.0.0"
    
    # Chemins
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    
    # ML Config
    MODEL_TYPE = "logistic_regression"
    MAX_FEATURES = 5000
    MIN_DF = 5
    MAX_DF = 0.8
```

### **`tests/conftest.py`** (Fixtures pytest)
```python
import pytest
import pandas as pd

@pytest.fixture
def sample_data():
    """Fixture données de test"""
    return pd.DataFrame({
        'comment_text': ['test comment', 'another comment'],
        'toxic': [0, 1]
    })

@pytest.fixture
def mock_model(tmp_path):
    """Fixture modèle mock"""
    model_path = tmp_path / "model.joblib"
    return model_path
```

### **`requirements-test.txt`**
```
pytest>=7.0.0
pytest-cov>=3.0.0
pytest-xdist>=2.5.0
pytest-mock>=3.6.0
hypothesis>=6.50.0
```

---

## 🚀 Commandes principales

```bash
# Setup
pip install -e .
pip install -r requirements-dev.txt

# Tests
pytest tests/ --cov=src --cov-report=html
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/pipeline/ -v

# Validation
pylint src/
black src/ tests/
isort src/ tests/
mypy src/

# Entraînement local
python src/train.py

# API local
python -m uvicorn src.digital_social_score.api.app:app --reload

# Pipeline local
python src/submit_pipeline.py --compile
```

---

## 🔄 Workflows CI/CD

### **GitHub Actions / Cloud Build**
```
push → tests → build → deploy
        ↓
      lint & format
      ↓
      unit tests
      ↓
      integration tests
      ↓
      pipeline compilation
      ↓
      docker build
      ↓
      artifact registry push
      ↓
      GKE deployment
```

---

## ✨ Avantages de cette structure

| Aspect | Avantage |
|--------|----------|
| **Modularité** | Code facile à tester et réutiliser |
| **Scalabilité** | Croissance facile du projet |
| **Maintenance** | Clair où trouver chaque chose |
| **Tests** | Séparation unit/integration/pipeline |
| **MLOps** | Pipeline, validation, versioning |
| **Deployment** | K8s, Docker, Cloud Build intégrés |
| **Documentation** | Tout est documenté |

---

## 🎯 Migration de l'existant

Pour migrer ta structure actuelle à cette nouvelle structure :

```bash
# 1. Créer la structure
mkdir -p src/digital_social_score/{core,ml,pipeline,api,utils,data,config}
mkdir -p tests/{unit,integration,pipeline,ml,fixtures}
mkdir -p deployment/{k8s,docker}
mkdir -p docs scripts data/raw data/processed

# 2. Déplacer les fichiers
mv src/app.py src/digital_social_score/api/
mv src/pipeline.py src/digital_social_score/pipeline/
mv src/train.py src/digital_social_score/ml/

# 3. Créer les fichiers manquants
touch src/digital_social_score/__init__.py
touch src/digital_social_score/core/__init__.py
touch tests/__init__.py tests/conftest.py
```

---

**À toi de jouer ! 🚀**
