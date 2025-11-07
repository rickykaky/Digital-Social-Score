# Guide Complet du Pipeline CI/CD - Social Score API

## Table des matières

1. [Vue d'ensemble du Pipeline](#vue-densemble-du-pipeline)
2. [Architecture CI/CD](#architecture-cicd)
3. [Configuration Cloud Build](#configuration-cloud-build)
4. [Configuration GitHub](#configuration-github)
5. [Processus de Déploiement](#processus-de-déploiement)
6. [Monitoring et Alertes](#monitoring-et-alertes)
7. [Rollback et Récupération](#rollback-et-récupération)
8. [Best Practices](#best-practices)

---

## Vue d'ensemble du Pipeline

Le pipeline CI/CD automatisé pour Social Score API couvre :

```
Code Push (GitHub)
       ↓
Cloud Build Trigger
       ↓
┌─────────────────────────────────────────┐
│         Pipeline Stages                 │
├─────────────────────────────────────────┤
│ 1. Tests (pytest)                       │
│ 2. Code Quality (lint, format, type)    │
│ 3. Pipeline Compilation (KFP v2)        │
│ 4. Docker Build & Push                  │
│ 5. GKE Deployment                       │
│ 6. Verification & Monitoring            │
└─────────────────────────────────────────┘
       ↓
GKE Cluster Update
       ↓
Verification & Health Checks
       ↓
Production Ready
```

---

## Architecture CI/CD

### Components

```
┌────────────────────────────────────────────────────────────────┐
│                      GitHub Repository                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Branches:                                               │  │
│  │  - main          (production)                            │  │
│  │  - develop       (staging)                               │  │
│  │  - feature/*     (development)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                    │
│                           ▼                                    │
│                    GitHub Actions                              │
│                   (Local CI Checks)                            │
│                   - Unit Tests                                 │
│                   - Lint & Format                              │
│                   - Type Checks                                │
│                   - Security Scan                              │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│              Google Cloud Build                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Triggers:                                               │  │
│  │  - Push to main   → Deploy to production                 │  │
│  │  - Push to develop → Deploy to staging                   │  │
│  │  - Tag release-* → Create release build                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Steps:                                                  │  │
│  │  1. Run pytest (tests/)                                  │  │
│  │  2. Compile KFP pipeline                                 │  │
│  │  3. Build Docker image                                   │  │
│  │  4. Push to Artifact Registry                            │  │
│  │  5. Deploy to GKE                                        │  │
│  │  6. Verify rollout                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│              Google Cloud Infrastructure                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Artifact Registry                                       │  │
│  │  social-score-api:latest                                 │  │
│  │  social-score-api:v1.2.3                                 │  │
│  │  social-score-api:prod-abc123                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  GKE Cluster (Production)                                │  │
│  │  Deployments → Services → Ingress → Load Balancer        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Vertex AI Pipelines                                     │  │
│  │  - ML model training                                     │  │
│  │  - Data preparation                                      │  │
│  │  - Model evaluation                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cloud Storage (GCS)                                     │  │
│  │  - Pipeline templates                                    │  │
│  │  - Build artifacts                                       │  │
│  │  - Logs                                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│         Monitoring & Alertes                                   │
│  - Cloud Logging                                               │
│  - Cloud Monitoring                                            │
│  - Prometheus / Grafana                                        │
│  - Cloud Trace                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Configuration Cloud Build

### 1. Connexion GitHub et Triggers

```bash
# Connecter GitHub à Cloud Build
gcloud builds connect --repository-name=Digital-Social-Score \
  --repository-owner=<your-github-username> \
  --region=us

# Lister les triggers
gcloud builds triggers list

# Créer un trigger pour la branche main
gcloud builds triggers create github \
  --name="social-score-main-deploy" \
  --repo-name=Digital-Social-Score \
  --repo-owner=<your-github-username> \
  --branch-pattern="^main$" \
  --build-config=src/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=production

# Créer un trigger pour la branche develop
gcloud builds triggers create github \
  --name="social-score-develop-deploy" \
  --repo-name=Digital-Social-Score \
  --repo-owner=<your-github-username> \
  --branch-pattern="^develop$" \
  --build-config=src/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=staging
```

### 2. Structure du cloudbuild.yaml

```yaml
# Substitutions globales (variables)
substitutions:
  _REGION: 'us-west1'
  _AR_REPO: 'social-score-repo'
  _IMAGE_NAME: 'social-score-api'
  _CLUSTER_NAME: 'social-score-cluster'
  _CLUSTER_ZONE: 'us-west1-a'
  _ENVIRONMENT: 'production'
  _PIPELINE_REGION: 'us-central1'

options:
  machineType: 'N1_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
  
timeout: '1800s'

steps:
  # Stage 0: Tests
  - name: 'python:3.11'
    id: 'run-tests'
    args:
      - sh
      - -c
      - |
        set -e
        echo "Installing test dependencies..."
        pip install -q -r requirements-test.txt
        
        echo "Downloading NLTK data..."
        python -m nltk.downloader -d /usr/share/nltk_data punkt stopwords wordnet averaged_perceptron_tagger
        
        echo "Running tests..."
        pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
        
        echo "Tests passed successfully!"
  
  # Stage 1: Pipeline Compilation
  - name: 'gcr.io/cloud-builders/gke-deploy'
    id: 'compile-pipeline'
    waitFor: ['run-tests']
    args:
      - sh
      - -c
      - |
        set -e
        echo "Installing KFP SDK..."
        pip install -q kfp
        
        echo "Compiling KFP pipeline..."
        python src/pipeline/main.py
        
        echo "Creating GCS bucket if needed..."
        BUCKET_NAME="social-score-${PROJECT_ID}"
        gsutil mb gs://${BUCKET_NAME}/ 2>/dev/null || echo "Bucket already exists"
        
        echo "Uploading pipeline template to GCS..."
        gsutil cp src/pipeline/pipeline_template.yaml gs://${BUCKET_NAME}/templates/
        
        echo "Submitting to Vertex AI..."
        gcloud ai pipelines create --project=${PROJECT_ID} \
          --region=${_PIPELINE_REGION} \
          --template=gs://${BUCKET_NAME}/templates/pipeline_template.yaml

  # Stage 2: Docker Build
  - name: 'gcr.io/cloud-builders/docker'
    id: 'build-image'
    waitFor: ['compile-pipeline']
    args:
      - build
      - -t
      - ${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO}/${_IMAGE_NAME}:latest
      - -t
      - ${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO}/${_IMAGE_NAME}:${COMMIT_SHA}
      - -f
      - Dockerfile
      - .

  # Stage 3: Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    id: 'push-image'
    waitFor: ['build-image']
    args:
      - push
      - ${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO}/${_IMAGE_NAME}

  # Stage 4: Deploy to GKE
  - name: 'gcr.io/cloud-builders/gke-deploy'
    id: 'deploy-gke'
    waitFor: ['push-image']
    args:
      - run
      - --filename=deployment/k8s/
      - --image=${_IMAGE_NAME}=${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO}/${_IMAGE_NAME}:${COMMIT_SHA}
      - --location=${_CLUSTER_ZONE}
      - --cluster=${_CLUSTER_NAME}

  # Stage 5: Verification
  - name: 'gcr.io/cloud-builders/kubectl'
    id: 'verify-deployment'
    waitFor: ['deploy-gke']
    env:
      - 'CLOUDSDK_COMPUTE_ZONE=${_CLUSTER_ZONE}'
      - 'CLOUDSDK_CONTAINER_CLUSTER=${_CLUSTER_NAME}'
    args:
      - rollout
      - status
      - deployment/social-score-deployment

artifacts:
  objects:
    location: gs://social-score-${PROJECT_ID}/builds/${COMMIT_SHA}
    paths:
      - 'htmlcov/**'
      - '.coverage'
```

### 3. Configurer les variables de substitution

```bash
# Mettre à jour les substitutions
gcloud builds update social-score-main-deploy \
  --substitutions _REGION=us-west1,_CLUSTER_ZONE=us-west1-a,_ENVIRONMENT=production

# Vérifier les substitutions
gcloud builds describe social-score-main-deploy --format='value(substitutions)'
```

---

## Configuration GitHub

### 1. Workflow GitHub Actions

Voir `.github/workflows/tests.yml` pour les tests locaux :

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: pytest tests/ -v --cov=src
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 2. Branch Protection Rules

Dans les paramètres GitHub :

```
Settings → Branches → Add rule

Branch name pattern: main
- Require status checks to pass
- Require code reviews before merging (2 reviews)
- Dismiss stale pull request approvals
- Require branches to be up to date

Branch name pattern: develop
- Require status checks to pass
- Require 1 code review before merging
```

### 3. Secrets GitHub

Configurer dans Settings → Secrets and variables → Actions :

```
GCP_PROJECT_ID = your-project-id
GCP_SERVICE_ACCOUNT_KEY = <base64-encoded-key>
CODECOV_TOKEN = <token>
DOCKER_REGISTRY = us-west1-docker.pkg.dev
```

---

## Processus de Déploiement

### Workflow de déploiement

```
1. Developer commits and pushes
   ↓
2. GitHub Actions runs tests
   ├─ Pass? → Continue
   └─ Fail? → Block merge

3. Create Pull Request
   ├─ Require 2 reviews (main) or 1 review (develop)
   └─ Required status checks must pass

4. Merge to branch
   ├─ If main → Production deployment
   └─ If develop → Staging deployment

5. Cloud Build triggered
   ├─ Tests (fail fast)
   ├─ Pipeline compilation
   ├─ Docker build
   ├─ Push to registry
   └─ Deploy to GKE

6. Verification checks
   ├─ Rollout status
   ├─ Health checks
   ├─ Integration tests
   └─ Monitoring alerts

7. Production monitoring
   └─ Logs, metrics, alerts
```

### Steps pour déployer

#### 1. Feature Branch Workflow

```bash
# Créer une branche feature
git checkout -b feature/new-anonymization-method

# Développer et tester localement
pytest tests/ -v

# Commit et push
git add .
git commit -m "feat: improve anonymization algorithm"
git push origin feature/new-anonymization-method

# Créer une Pull Request sur GitHub
# → GitHub Actions exécute les tests
# → Demander 2 reviews (main) ou 1 review (develop)
```

#### 2. Merge et Déploiement

```bash
# Merger sur develop (pour staging)
git checkout develop
git pull origin develop
git merge --no-ff feature/new-anonymization-method
git push origin develop

# Cloud Build se déclenche automatiquement
# Déploiement sur staging (GKE cluster de staging)

# Après tests en staging, créer une PR main
git checkout main
git pull origin main
git merge --no-ff develop
git push origin main

# Cloud Build se déclenche
# Déploiement en production
```

#### 3. Utiliser les tags pour les releases

```bash
# Créer un tag de release
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3

# Cloud Build peut créer un trigger pour les tags
# gcloud builds triggers create github \
#   --name="social-score-release" \
#   --repo-name=Digital-Social-Score \
#   --tag-pattern="^v[0-9]+\.[0-9]+\.[0-9]+$" \
#   --build-config=src/cloudbuild.yaml
```

---

## Monitoring et Alertes

### 1. Cloud Logging

```bash
# Voir les logs de build
gcloud builds log BUILD_ID

# Filtrer les logs
gcloud logging read "resource.type=cloud_build" --limit 50

# Logs d'un build spécifique
gcloud builds log BUILD_ID --stream

# Exporter les logs
gcloud logging read "resource.type=cloud_build" > build_logs.json
```

### 2. Cloud Monitoring

```bash
# Créer une alerte pour les déploiements échoués
gcloud alpha monitoring policies create \
  --display-name="Cloud Build Failure" \
  --condition="BUILD_FAILURE" \
  --notification-channels=[CHANNEL_ID]

# Créer une alerte pour les erreurs API
gcloud alpha monitoring policies create \
  --display-name="API Error Rate High" \
  --condition="error_rate > 5%" \
  --notification-channels=[CHANNEL_ID]

# Lister les politiques
gcloud alpha monitoring policies list
```

### 3. Dashboards

```bash
# Créer un dashboard JSON
cat > dashboard.json <<EOF
{
  "displayName": "Social Score API",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Deployment Status",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=cloud_build AND metric.type=cloudbuild.googleapis.com/build/status"
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF

# Créer le dashboard
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

### 4. Cloud Trace

```bash
# Activer Cloud Trace dans l'application
# (voir src/app.py pour l'instrumentation)

# Voir les traces
gcloud trace list --limit 10
```

---

## Rollback et Récupération

### 1. Rollback de déploiement

```bash
# Voir l'historique de déploiement
kubectl rollout history deployment/social-score-deployment

# Rollback à la version précédente
kubectl rollout undo deployment/social-score-deployment

# Rollback à une version spécifique
kubectl rollout undo deployment/social-score-deployment --to-revision=2

# Attendre le rollback
kubectl rollout status deployment/social-score-deployment
```

### 2. Rollback de Cloud Build

```bash
# Voir les derniers builds
gcloud builds list --limit 10

# Retriggerer un build précédent
gcloud builds resubmit BUILD_ID

# Après avoir resubmis, vérifier le statut
gcloud builds log BUILD_ID --stream
```

### 3. Disaster Recovery

```bash
# Sauvegarder la configuration actuelle
kubectl get all -o yaml > backup-$(date +%Y%m%d).yaml

# Restaurer
kubectl apply -f backup-*.yaml

# Mettre en place Velero pour backup automatique
helm repo add velero https://charts.velero.io
helm install velero velero/velero \
  --namespace velero --create-namespace \
  --set configuration.backupStorageLocation.bucket=social-score-backups \
  --set configuration.backupStorageLocation.provider=gcp
```

---

## Best Practices

### 1. Versioning

```bash
# Utiliser semantic versioning
# v<MAJOR>.<MINOR>.<PATCH>
# v1.2.3

# Tag les images Docker
docker tag social-score-api:latest us-west1-docker.pkg.dev/PROJECT_ID/social-score-repo/social-score-api:v1.2.3

# Mettre à jour la version dans le code
# src/config.py: __version__ = "1.2.3"
```

### 2. Testing Strategy

```
- Unit tests: tous les changements de code
- Integration tests: avant chaque PR
- Load tests: avant les déploiements en prod
- Smoke tests: après chaque déploiement
- End-to-end tests: tests utilisateur
```

### 3. Deployment Strategy

```
- Bleu-vert: 2 versions complètes, switch du traffic
- Canary: 5% du traffic sur nouvelle version
- Rolling update: graduel remplacement des pods
```

```bash
# Rolling update (par défaut dans le manifeste)
kubectl patch deployment social-score-deployment \
  -p '{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxSurge":1,"maxUnavailable":0}}}}'

# Blue-Green (manual)
# 1. Deploy nouvelle version (v2)
# 2. Changer le service selector
# 3. Monitor
# 4. Supprimer l'ancienne version
```

### 4. Monitoring Checklist

```
Before Deployment:
□ Tests passed locally
□ GitHub Actions passed
□ Code review approved
□ Security scan passed
□ No breaking changes

During Deployment:
□ Cloud Build logs
□ GKE rollout status
□ Health checks passing
□ No error spikes in logs
□ Response times normal

After Deployment:
□ Verify API endpoints
□ Check database connections
□ Monitor error rates
□ Watch resource usage
□ Set up alerting
□ Document changes
```

### 5. Secrets Management

```bash
# Utiliser Google Secret Manager
gcloud secrets create db-password --data-file=- <<< "your-password"

# Accéder depuis Cloud Build
steps:
  - name: 'cloud-builders/gke-deploy'
    env:
      - 'DB_PASSWORD=/workspace/secrets/db-password'
    secretEnv: ['DB_PASSWORD']

# Créer une secretVersion
gcloud secrets versions add db-password --data-file=-

# Configurer les permissions
gcloud secrets add-iam-policy-binding db-password \
  --member=serviceAccount:SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### 6. Documentation

```
Maintenir dans le repo:
- DEPLOYMENT_GUIDE.md (ce fichier)
- K8S_DEPLOYMENT_GUIDE.md
- CLOUDBUILD_IMPROVEMENTS.md
- Runbooks pour incidents
- Change log (CHANGELOG.md)
```

---

## Commandes Utiles

```bash
# Voir les builds en cours
gcloud builds list --running

# Voir les détails d'un build
gcloud builds describe BUILD_ID

# Logs en temps réel
gcloud builds log BUILD_ID --stream

# Failover et retry
gcloud builds cancel BUILD_ID
gcloud builds resubmit BUILD_ID

# Vérifier le déploiement
kubectl get deployment social-score-deployment -o wide
kubectl describe deployment social-score-deployment

# Voir les événements
kubectl get events --sort-by='.lastTimestamp' | tail -20

# Nettoyer les anciennes images
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/social-score-repo/social-score-api
gcloud artifacts docker images delete ${REGION}-docker.pkg.dev/${PROJECT_ID}/social-score-repo/social-score-api:OLD_TAG
```

---

## Ressources supplémentaires

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [GKE Deployment Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
- [GitFlow Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
