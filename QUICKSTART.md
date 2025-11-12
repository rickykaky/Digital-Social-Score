# ⚡ Digital Social Score - Guide de Démarrage Rapide

> 🎯 **Objectif** : Faire fonctionner votre API de détection de toxicité ML en moins de 10 minutes

## 📋 Prérequis (5 min)

### **Installations Requises**
```bash
# Python 3.11+
python --version

# Docker
docker --version

# Google Cloud SDK
gcloud --version

# kubectl (optionnel pour local)
kubectl version --client
```

### **Compte GCP**
1. Créer un projet GCP : `digital-social-score`
2. Activer les APIs requises :
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

---

## 🚀 Installation Express (3 min)

### **1. Clone et Setup**
```bash
# Cloner le projet
git clone https://github.com/rickykaky/Digital-Social-Score.git
cd Digital-Social-Score

# Installer les dépendances
pip install -r requirements.txt
```

### **2. Configuration**
```bash
# Authentification GCP
gcloud auth login
gcloud config set project digital-social-score

# Variables d'environnement
export PROJECT_ID=digital-social-score
export REGION=us-west1
```

### **3. Entraîner le Modèle**
```bash
# Entraînement local (1-2 minutes)
python src/train.py
```

✅ **Résultat attendu** : `✅ Modèle sauvegardé avec 92% accuracy`

---

## 🎯 Test Local (2 min)

### **Lancer l'API**
```bash
# Démarrer le serveur FastAPI
python src/main.py
```

### **Tester l'API**
```bash
# Dans un autre terminal
# Test de santé
curl http://localhost:8000/health

# Test de détection de toxicité
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Ce message est-il toxique?"}'
```

✅ **Résultat attendu** :
```json
{
  "text": "Ce message est-il toxique?",
  "is_toxic": false,
  "confidence": 0.95,
  "scores": {
    "toxic": 0.05,
    "severe_toxic": 0.01,
    "obscene": 0.02,
    "threat": 0.01,
    "insult": 0.03,
    "identity_hate": 0.01
  }
}
```

---

## ☁️ Déploiement Cloud (Optionnel)

### **Déploiement Automatique via GitHub**
1. **Fork** le repository sur votre compte GitHub
2. **Push** vers la branche `main` → Déploiement automatique !
3. **Monitor** : [GitHub Actions](https://github.com/YOUR_USERNAME/Digital-Social-Score/actions)

### **Déploiement Manuel sur GCP**
```bash
# Build et déploiement
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_REGION=us-west1,_ZONE=us-west1-a

# Vérifier le déploiement
kubectl get pods -n production
```

---

## 🤖 Déploiement Conditionnel ML

### **Comment ça marche ?**
Le système **déploie automatiquement** une nouvelle version uniquement si :
- ✅ **Accuracy ≥ 85%**
- ✅ **Tests passent**
- ✅ **Build réussi**

### **Pipeline Automatique**
```
📊 Push Code → 🤖 Train Model → 📈 Check 85% → 🚀 Deploy Auto
```

### **Monitoring**
- **GitHub Actions** : Tests et simulation
- **Cloud Build** : Build de production
- **Vertex AI** : Pipeline ML conditionnel
- **GKE** : API en production

---

## 🔧 Configuration Avancée

### **Variables d'Environnement**
Créer un fichier `.env` :
```bash
# Projet
GCP_PROJECT_ID=digital-social-score
VERTEX_AI_REGION=us-west1

# ML Config
MODEL_ACCURACY_THRESHOLD=0.85
ENABLE_ANONYMIZATION=true

# API Config
API_HOST=0.0.0.0
API_PORT=8000
```

### **Personnaliser le Modèle**
Modifier `src/config.py` pour ajuster :
- Seuil de toxicité
- Features NLTK
- Hyperparamètres ML

---

## 🆘 Résolution Rapide

### **❌ Erreur "Model not found"**
```bash
# Solution
python src/train.py
```

### **❌ API ne démarre pas**
```bash
# Vérifier les dépendances
pip install -r requirements.txt
python -c "import nltk; print('NLTK OK')"
```

### **❌ Tests échouent**
```bash
# Relancer les tests
python -m pytest tests/ -v
```

### **❌ Déploiement GCP échoue**
```bash
# Vérifier l'authentification
gcloud auth list
gcloud config get-value project
```

---

## 📊 Commandes Utiles

### **Développement**
```bash
# Tests unitaires
pytest tests/

# Formatage du code
black src/
isort src/

# Linting
flake8 src/
```

### **Monitoring**
```bash
# Logs locaux
tail -f logs/app.log

# Logs GKE
kubectl logs -f deployment/social-score-api -n production

# Status des builds
gcloud builds list --limit=5
```

### **Base de Données (si applicable)**
```bash
# Backup du modèle
cp src/models/model.joblib backup/model_$(date +%Y%m%d).joblib

# Restaurer un modèle
cp backup/model_YYYYMMDD.joblib src/models/model.joblib
```

---

## 🎉 Vous êtes Prêt !

Votre **API de détection de toxicité ML** est maintenant :
- ✅ **Fonctionnelle localement**
- ✅ **Deployable automatiquement**
- ✅ **Monitored en temps réel**
- ✅ **Avec déploiement conditionnel** (accuracy ≥ 85%)

### **Prochaines Étapes**
1. 🔧 **Personnaliser** le modèle selon vos besoins
2. 🚀 **Déployer en production** via GitHub Actions
3. 📊 **Monitorer** les performances
4. 🔄 **Itérer** sur le modèle pour améliorer l'accuracy

### **Support**
- 📖 [Documentation complète](README.md)
- 🐛 [Signaler un bug](https://github.com/rickykaky/Digital-Social-Score/issues)
- 💬 [Discussions](https://github.com/rickykaky/Digital-Social-Score/discussions)

---

**🎯 Temps total estimé : 10 minutes | Système ML de production prêt !** 🚀