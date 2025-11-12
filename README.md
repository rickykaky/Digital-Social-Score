# 🤖 Digital Social Score - API de Détection de Toxicité ML

[![CI/CD Pipeline](https://github.com/rickykaky/Digital-Social-Score/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/rickykaky/Digital-Social-Score/actions)
[![Cloud Build](https://img.shields.io/badge/Cloud%20Build-Active-green)](https://console.cloud.google.com/cloud-build/builds)
[![ML Pipeline](https://img.shields.io/badge/Vertex%20AI-Pipeline%20Active-blue)](https://console.cloud.google.com/vertex-ai/pipelines)

> **API intelligente de modération de contenu** avec pipeline ML automatisé et déploiement conditionnel basé sur les performances du modèle.

## 🎯 Vue d'Ensemble

**Digital Social Score** est une solution complète de **détection de toxicité** utilisant le machine learning pour analyser et modérer automatiquement le contenu textuel. Le système déploie automatiquement de nouvelles versions **uniquement lorsque l'accuracy du modèle atteint 85%** ou plus.

### ✨ Fonctionnalités Principales

- 🧠 **ML Pipeline Automatisé** - Entraînement et déploiement conditionnels avec Vertex AI
- 🛡️ **Détection de Toxicité** - Classification avancée avec NLTK + Régression Logistique
- 🔒 **Conformité RGPD** - Anonymisation automatique des données personnelles
- ⚡ **API REST Haute Performance** - FastAPI avec cache Redis et monitoring
- 🚀 **CI/CD Avancé** - GitHub Actions + Cloud Build avec déploiement conditionnel
- 📊 **Monitoring Temps Réel** - Métriques de performance et alertes automatiques

---

## 🏗️ Architecture du Système

### **Pipeline ML Conditionnel**
```
📊 Données → 🤖 Entraînement → 📈 Évaluation → 🎯 Seuil 85% → 🚀 Déploiement Auto
```

### **Infrastructure Cloud**
```
┌─ GitHub Actions ─┐    ┌─── Cloud Build ───┐    ┌── Vertex AI ──┐    ┌─── GKE ───┐
│ • Tests Auto     │───▶│ • Build Docker    │───▶│ • ML Pipeline │───▶│ • API Prod │
│ • NLTK Training  │    │ • Cache uv        │    │ • Evaluation  │    │ • Auto-Scale│
│ • Simulation     │    │ • Multi-stage     │    │ • Conditional │    │ • Monitoring│
└──────────────────┘    └───────────────────┘    └───────────────┘    └───────────┘
```

### **Stack Technologique**
- **Backend**: FastAPI + Python 3.11
- **ML/NLP**: NLTK, Scikit-learn, TF-IDF
- **Infrastructure**: Google Cloud Platform (GKE, Vertex AI, Cloud Build)
- **CI/CD**: GitHub Actions, Cloud Build, Container Registry
- **Cache**: Redis, uv package caching
- **Monitoring**: Prometheus, Grafana, Cloud Logging

---

## ⚡ Démarrage Rapide

### **Prérequis**
- Python 3.11+
- Docker & Docker Compose
- Google Cloud SDK (gcloud)
- kubectl
- Compte GCP avec les APIs activées

### **Installation Locale**
```bash
# Cloner le repository
git clone https://github.com/rickykaky/Digital-Social-Score.git
cd Digital-Social-Score

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# Entraîner le modèle localement
python src/train.py

# Lancer l'API
python src/main.py
```

### **Test de l'API**
```bash
# Test de santé
curl http://localhost:8000/health

# Analyse de toxicité
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Votre texte à analyser"}'
```

---

## 🚀 Déploiement en Production

### **Configuration GCP**
```bash
# Authentification
gcloud auth login
gcloud config set project digital-social-score

# Configurer les variables d'environnement
export PROJECT_ID=digital-social-score
export REGION=us-west1
export ZONE=us-west1-a
export CLUSTER_NAME=social-score-cluster
```

### **Déploiement Automatique**
Le système se déploie automatiquement via GitHub Actions et Cloud Build :

1. **Push sur `main`** → GitHub Actions démarre
2. **Tests & Entraînement** → Validation du code et du modèle
3. **Cloud Build** → Construction et déploiement standard
4. **Vertex AI Pipeline** → Évaluation ML et déploiement conditionnel
5. **Si accuracy ≥ 85%** → Nouvelle image Docker déployée automatiquement

### **Déploiement Manuel**
```bash
# Build et déploiement manuel
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_REGION=us-west1,_ZONE=us-west1-a,_CLUSTER_NAME=social-score-cluster

# Vérifier le déploiement
kubectl get pods -n production
kubectl get services -n production
```

---

## 🤖 Pipeline ML et Déploiement Conditionnel

### **Fonctionnement du Déploiement Conditionnel**

Le système utilise un **pipeline Vertex AI** qui :

1. 📊 **Évalue automatiquement** les performances du modèle
2. 🎯 **Compare l'accuracy** au seuil de 85%
3. 🚀 **Déclenche le déploiement** si le seuil est atteint
4. 🐳 **Construit une nouvelle image Docker** avec le modèle performant
5. 📤 **Pousse vers Artifact Registry** automatiquement
6. 🔄 **Met à jour le déploiement GKE** sans intervention manuelle

### **Architecture du Pipeline**
```python
# Pipeline Kubeflow (simplifié)
@dsl.pipeline(name="digital-score-conditional-deployment")
def conditional_deployment_pipeline():
    # Entraînement et évaluation
    evaluation = evaluate_model_op()
    
    # Déploiement conditionnel
    with dsl.If(evaluation.outputs['accuracy'] >= 0.85):
        build_and_deploy_docker_op()  # Déploiement automatique
```

### **Avantages du Système**
- ✅ **Qualité Garantie** - Seuls les modèles performants sont déployés
- ✅ **Zéro Downtime** - Déploiements rolling sans interruption
- ✅ **Traçabilité Complète** - Logs et métriques de chaque déploiement
- ✅ **Rollback Automatique** - Retour à la version précédente en cas d'échec

---

## 🔧 Configuration et Variables d'Environnement

### **Variables Principales**
```bash
# Projet et Région
GCP_PROJECT_ID=digital-social-score
VERTEX_AI_REGION=us-west1

# Configuration ML
MODEL_ACCURACY_THRESHOLD=0.85
ENABLE_ANONYMIZATION=true
ENABLE_LEMMATIZATION=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Cache et Performance
REDIS_URL=redis://redis:6379
ENABLE_CACHING=true
CACHE_TTL=3600
```

### **Configuration du Cache uv**
Le système utilise **uv** pour un cache ultra-rapide des dépendances :
```dockerfile
# Cache optimisé dans Dockerfile
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-dev
```

---

## 📊 Monitoring et Observabilité

### **Métriques Disponibles**
- 📈 **Performance API** - Latence, throughput, taux d'erreur
- 🤖 **Métriques ML** - Accuracy, precision, recall, F1-score
- 🔄 **Pipeline CI/CD** - Temps de build, taux de succès des déploiements
- 🚀 **Infrastructure** - CPU, mémoire, réseau des pods GKE

### **Dashboards**
- **Grafana** : `https://monitoring.digital-social-score.com`
- **GCP Console** : Cloud Monitoring pour l'infrastructure
- **Vertex AI** : Monitoring des pipelines ML

### **Alertes Automatiques**
- 🚨 **Accuracy < 80%** → Alerte modèle dégradé
- 🚨 **API Latence > 2s** → Alerte performance
- 🚨 **Build Failed** → Alerte CI/CD

---

## 🛠️ Développement et Contribution

### **Structure du Projet**
```
Digital-Social-Score/
├── src/
│   ├── main.py              # Point d'entrée API
│   ├── train.py             # Entraînement ML
│   ├── config.py            # Configuration centralisée
│   └── pipeline/            # Pipeline Vertex AI
├── tests/                   # Tests automatisés
├── deployment/              # Manifestes Kubernetes
├── .github/workflows/       # GitHub Actions
├── cloudbuild.yaml         # Cloud Build configuration
└── Dockerfile              # Image de production
```

### **Tests**
```bash
# Tests unitaires
pytest tests/

# Tests d'intégration
python -m pytest tests/integration/

# Tests de performance
python tests/load_tests.py
```

### **Standards de Code**
- **Formatage** : Black, isort
- **Linting** : Flake8, pylint
- **Type Checking** : mypy
- **Documentation** : Docstrings obligatoires

---

## 🔒 Sécurité et Conformité

### **Conformité RGPD**
- ✅ **Anonymisation automatique** des données personnelles
- ✅ **Pseudonymisation** des identifiants
- ✅ **Chiffrement** des données en transit et au repos
- ✅ **Logs d'audit** complets et traçables

### **Sécurité Infrastructure**
- 🔐 **IAM** - Gestion des accès granulaire
- 🛡️ **Network Policies** - Isolation des pods Kubernetes
- 🔒 **Secrets Management** - Google Secret Manager
- 📋 **Vulnerability Scanning** - Images Docker scannées automatiquement

---

## 📚 Documentation Avancée

### **APIs et Endpoints**
- **POST /analyze** - Analyse de toxicité de texte
- **GET /health** - Vérification de santé du service
- **GET /metrics** - Métriques Prometheus
- **POST /batch-analyze** - Analyse en lot

### **Modèle ML**
- **Algorithme** : Régression Logistique avec TF-IDF
- **Features** : Vectorisation TF-IDF + features linguistiques NLTK
- **Performance** : 85%+ accuracy sur dataset de validation
- **Mise à jour** : Automatique via pipeline Vertex AI

### **Optimisations**
- **Cache Redis** : Résultats mis en cache pour 1 heure
- **Scaling Automatique** : HPA Kubernetes basé sur CPU/Mémoire
- **Connection Pooling** : Pool de connexions optimisé
- **Batch Processing** : Support des analyses en lot

---

## 🆘 Support et Dépannage

### **Problèmes Fréquents**

**❌ Erreur "Model not found"**
```bash
# Solution : Réentraîner le modèle
python src/train.py
```

**❌ Pipeline Vertex AI échoue**
```bash
# Vérifier les permissions IAM
gcloud projects get-iam-policy digital-social-score
```

**❌ Déploiement GKE bloqué**
```bash
# Vérifier le cluster
kubectl get pods -n production
kubectl describe pod <pod-name>
```

### **Logs et Debug**
```bash
# Logs de l'API
kubectl logs -f deployment/social-score-api -n production

# Logs Cloud Build
gcloud builds list --limit=10

# Logs Vertex AI
gcloud ai pipelines runs list --region=us-west1
```

---

## 📄 Licence et Contact

- **Licence** : MIT License
- **Auteur** : Digital Social Score Team
- **Repository** : [GitHub](https://github.com/rickykaky/Digital-Social-Score)
- **Issues** : [GitHub Issues](https://github.com/rickykaky/Digital-Social-Score/issues)

---

## 🚀 Roadmap

### **Version 2.0** (Q1 2025)
- [ ] Support multi-langues (EN, ES, DE)
- [ ] Modèles Deep Learning (BERT, RoBERTa)
- [ ] API GraphQL
- [ ] Dashboard temps réel

### **Version 2.1** (Q2 2025)
- [ ] Détection de sentiment avancée
- [ ] Integration avec des CMS (WordPress, Drupal)
- [ ] Auto-scaling basé sur la charge ML

---

*Système ML de production avec déploiement conditionnel automatique - Qualité garantie à 85%+ accuracy* 🎯
