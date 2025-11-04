# Digital Social Score API

**De l'analyse de texte à l'infrastructure Cloud sécurisée, scalable et conforme**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Vue d'ensemble

L'API Digital Social Score est une solution RGPD-compliant pour la détection automatique de toxicité dans les textes. Elle attribue un score de 0 à 100 indiquant le niveau de toxicité détecté (injures, racisme, harcèlement, propos haineux).

### Caractéristiques principales

✅ **Détection de toxicité multi-catégories** : Injures, harcèlement, discours haineux, menaces, obscénité  
✅ **Conformité RGPD** : Anonymisation automatique des données personnelles  
✅ **Score précis** : Attribution d'un score de 0 à 100  
✅ **Scalabilité** : Architecture cloud-native avec auto-scaling  
✅ **Observabilité** : Métriques Prometheus, logs structurés, health checks  
✅ **Documentation complète** : OpenAPI/Swagger, guides d'utilisation  

## 🚀 Démarrage rapide

### Prérequis

- Python 3.11+
- pip ou conda
- (Optionnel) Docker et Docker Compose

### Installation locale

1. **Cloner le dépôt**
```bash
git clone https://github.com/rickykaky/Digital-Social-Score.git
cd Digital-Social-Score
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Télécharger le modèle spaCy**
```bash
python -m spacy download en_core_web_sm
```

5. **Lancer l'API**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Accéder à la documentation**
- API: http://localhost:8000
- Documentation Swagger: http://localhost:8000/docs
- Documentation ReDoc: http://localhost:8000/redoc

### Installation avec Docker

```bash
# Construire et lancer les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Voir les logs
docker-compose logs -f api
```

## 📖 Utilisation

### Exemple d'analyse simple

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ceci est un commentaire de test.",
    "anonymize": true
  }'
```

### Exemple Python

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "text": "Votre texte à analyser",
        "anonymize": True,
        "anonymization_method": "mask"
    }
)

result = response.json()
print(f"Score de toxicité: {result['toxicity_score']}")
print(f"Est toxique: {result['is_toxic']}")
print(f"Sévérité: {result['severity']}")
```

### Analyse par batch

```python
response = requests.post(
    "http://localhost:8000/analyze/batch",
    json={
        "texts": [
            "Premier commentaire",
            "Deuxième commentaire",
            "Troisième commentaire"
        ],
        "anonymize": True
    }
)

results = response.json()["results"]
for i, result in enumerate(results):
    print(f"Texte {i+1}: Score {result['toxicity_score']}")
```

## 🏗️ Architecture

### Structure du projet

```
Digital-Social-Score/
├── src/
│   ├── api/              # API FastAPI
│   │   └── main.py       # Points d'entrée de l'API
│   ├── models/           # Modèles ML
│   │   └── toxicity_classifier.py
│   └── utils/            # Utilitaires
│       ├── anonymizer.py # Anonymisation RGPD
│       └── data_processor.py
├── tests/                # Tests unitaires
├── data/                 # Données (non versionnées)
│   ├── raw/             # Données brutes
│   ├── processed/       # Données traitées
│   └── anonymized/      # Données anonymisées
├── docs/                # Documentation
│   ├── ARCHITECTURE.md  # Architecture Cloud
│   └── API_DOCUMENTATION.md
├── k8s/                 # Manifests Kubernetes
├── monitoring/          # Configuration monitoring
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── config.py           # Configuration
```

### Composants principaux

1. **API Layer** (FastAPI)
   - Endpoints REST
   - Validation des requêtes
   - Gestion des erreurs

2. **Module d'anonymisation** (spaCy NER)
   - Détection de PII
   - 3 méthodes : mask, pseudonymize, remove
   - Conformité RGPD

3. **Modèle de détection** (Transformers)
   - Modèle : RoBERTa fine-tuné
   - Catégories : toxicité, injures, harcèlement, etc.
   - Score 0-100

4. **Monitoring** (Prometheus + Grafana)
   - Métriques temps réel
   - Alertes
   - Dashboards

## 📊 Étape 1 : Exploration et Anonymisation des Données

### Objectifs

✅ Identifier et traiter les données personnelles  
✅ Mettre en œuvre l'anonymisation et la pseudonymisation  
✅ Comparer données originales et anonymisées  
✅ Documenter le registre de traitement des données  

### Traitement d'un dataset

```python
from src.utils.data_processor import DataProcessor

# Initialiser le processeur
processor = DataProcessor(data_dir="./data")

# Charger un dataset (CSV, JSON, TXT)
df = processor.load_dataset("./data/raw/toxic_comments.csv")

# Explorer le dataset
stats = processor.explore_dataset(df)
print(stats)

# Anonymiser le dataset
df_anonymized, metadata = processor.anonymize_dataset(
    df, 
    text_column='text',
    method='mask'
)

# Sauvegarder les résultats
processor.save_dataset(df_anonymized, "anonymized_comments.csv")

# Comparer original vs anonymisé
comparison = processor.compare_datasets(df, df_anonymized)

# Générer le registre RGPD
processor.generate_data_processing_registry(comparison)
```

### Exemple de traitement

```bash
# Exécuter le script de démonstration
python src/utils/data_processor.py
```

Cela crée :
- `data/raw/sample_original.csv` - Dataset original
- `data/anonymized/sample_anonymized.csv` - Dataset anonymisé
- `data/processed/data_processing_registry.json` - Registre RGPD

### Méthodes d'anonymisation

| Méthode | Description | Exemple |
|---------|-------------|---------|
| **mask** | Remplace par `[TYPE_ENTITE]` | `John Smith` → `[PERSON]` |
| **pseudonymize** | Remplace par identifiant hashé | `John Smith` → `[PERSON_a3f5b8c2]` |
| **remove** | Supprime complètement | `John Smith` → `` |

### Entités détectées

- 👤 **PERSON** : Noms de personnes
- 📧 **EMAIL** : Adresses email
- 📞 **PHONE** : Numéros de téléphone
- 🏢 **ORG** : Organisations
- 📍 **GPE/LOC** : Lieux géographiques
- 📅 **DATE/TIME** : Dates et heures
- 🌐 **IP_ADDRESS** : Adresses IP

## 🔒 Conformité RGPD

### Mesures de protection

1. **Minimisation des données** : Seul le texte est traité
2. **Anonymisation automatique** : PII supprimé avant traitement ML
3. **Pas de stockage** : Aucune donnée conservée après traitement
4. **Logs sécurisés** : Pas de PII dans les logs
5. **Registre de traitement** : Documentation complète

### Vérifier la conformité

```bash
curl http://localhost:8000/gdpr/compliance
```

## 📈 Monitoring et Observabilité

### Métriques Prometheus

```bash
# Accéder aux métriques
curl http://localhost:8000/metrics
```

Métriques disponibles :
- `api_requests_total` : Nombre total de requêtes
- `api_request_duration_seconds` : Durée des requêtes
- `toxicity_score` : Distribution des scores

### Dashboards Grafana

Accéder à Grafana : http://localhost:3000 (admin/admin)

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-asyncio httpx

# Exécuter tous les tests
pytest

# Tests avec couverture
pytest --cov=src tests/

# Tests spécifiques
pytest tests/test_anonymizer.py
pytest tests/test_api.py
```

## 🚢 Déploiement

### Docker

```bash
# Construction
docker build -t digital-social-score:latest .

# Exécution
docker run -p 8000:8000 digital-social-score:latest
```

### Kubernetes

```bash
# Déployer sur K8s
kubectl apply -f k8s/deployment.yaml

# Vérifier le statut
kubectl get pods
kubectl get services

# Scaler
kubectl scale deployment digital-social-score-api --replicas=5
```

### Cloud Providers

Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) pour :
- AWS (ECS/EKS)
- Google Cloud Platform (GKE)
- Azure (AKS)

## 📚 Documentation complète

- [Architecture Cloud](docs/ARCHITECTURE.md) - Schémas et justifications
- [Documentation API](docs/API_DOCUMENTATION.md) - Guide complet des endpoints
- [API Interactive](http://localhost:8000/docs) - Swagger UI

## 🛠️ Configuration

Variables d'environnement (fichier `.env`) :

```bash
# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Modèles
TOXICITY_MODEL=facebook/roberta-hate-speech-dynabench-r4-target
SPACY_MODEL=en_core_web_sm

# RGPD
ANONYMIZE_BY_DEFAULT=true
DEFAULT_ANONYMIZATION_METHOD=mask

# Sécurité
MAX_TEXT_LENGTH=5000
RATE_LIMIT_REQUESTS=100
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

Digital Social Score Team

## 🆘 Support

- 📧 Email: support@digitalsocialscore.com
- 🐛 Issues: [GitHub Issues](https://github.com/rickykaky/Digital-Social-Score/issues)
- 📖 Documentation: [docs/](docs/)

## 🎯 Roadmap

- [ ] Support multilingue (FR, ES, DE)
- [ ] Amélioration du modèle avec fine-tuning
- [ ] Interface web de démonstration
- [ ] API Gateway avec authentification OAuth
- [ ] Déploiement serverless (AWS Lambda)
- [ ] Webhooks pour notifications
- [ ] Analytics dashboard

---

**⚠️ Note** : Cette API est fournie à des fins éducatives et de démonstration. Pour une utilisation en production, veuillez mettre en place des mesures de sécurité supplémentaires (authentification, rate limiting strict, monitoring avancé, etc.).
