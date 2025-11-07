# 🚀 Cloud Build Pipeline - Améliorations

## Résumé des Modifications

Votre `cloudbuild.yaml` a été amélioré pour être **production-ready** avec une meilleure gestion des erreurs, des variables globales, et une architecture robuste.

---

## 📋 Structure Améliorée

### Avant → Après

```
AVANT:
❌ Pas de variables globales
❌ Dépendances manquantes
❌ Pas de gestion d'erreurs
❌ Ordre d'exécution incorrect
❌ Pas de timeout
❌ Pas de vérifications

APRÈS:
✅ Variables globales (substitutions)
✅ Tests en premier (Étape 0)
✅ Pipeline KFP (Étape 1)
✅ Docker build (Étape 2)
✅ Docker push (Étape 3)
✅ Déploiement GKE (Étape 4)
✅ Vérification finale (Étape 5)
✅ Gestion d'erreurs complète
✅ Timeout et logging
✅ Dépendances explicites
```

---

## 🔄 Flux d'Exécution Corrigé

```
┌─────────────────────────────────┐
│ ÉTAPE 0 : TESTS (python:3.11)   │
│ - Install requirements.txt       │
│ - Install requirements-test.txt  │
│ - Download NLTK data            │
│ - Run pytest tests/             │
└──────────────┬──────────────────┘
               │
               ↓
┌─────────────────────────────────┐
│ ÉTAPE 1 : COMPILE PIPELINE (SDK)│
│ - Créer bucket GCS              │
│ - Compiler KFP v2               │
│ - Soumettre à Vertex AI         │
│ - Stocker template YAML         │
└──────────────┬──────────────────┘
               │
               ↓
┌─────────────────────────────────┐
│ ÉTAPE 2 : BUILD DOCKER (docker) │
│ - Build image                   │
│ - Tag COMMIT_SHA + latest       │
└──────────────┬──────────────────┘
               │
               ↓
┌─────────────────────────────────┐
│ ÉTAPE 3 : PUSH À AR (docker)    │
│ - Push to Artifact Registry     │
└──────────────┬──────────────────┘
               │
               ↓
┌─────────────────────────────────┐
│ ÉTAPE 4 : DEPLOY GKE (SDK)      │
│ - Get credentials               │
│ - Update deployment             │
│ - Rollout status                │
└──────────────┬──────────────────┘
               │
               ↓
┌─────────────────────────────────┐
│ ÉTAPE 5 : VERIFY (SDK)          │
│ - Afficher le résumé            │
│ - Liens vers ressources         │
└─────────────────────────────────┘
```

---

## ✨ Améliorations Clés

### 1. **Variables Globales (Substitutions)**
```yaml
substitutions:
  _REGION: 'us-west1'
  _AR_REPO: 'social-score-repo'
  _IMAGE_NAME: 'social-score-api'
  _CLUSTER_NAME: 'social-score-cluster'
  _CLUSTER_ZONE: 'us-west1-a'
  _DEPLOYMENT_NAME: 'social-score-deployment'
  _PIPELINE_REGION: 'us-central1'
```
**Avantages:**
- ✅ Plus facile à maintenir
- ✅ Centralisé
- ✅ Peut être surchargé via CLI
- ✅ Pas de duplication

### 2. **Tests en Première Étape**
```yaml
- name: 'python:3.11'
  id: 'run-tests'
```
**Avantages:**
- ✅ Valide le code avant le build Docker
- ✅ Économise du temps (fail-fast)
- ✅ Tests complets avec pytest
- ✅ Télécharge les données NLTK

### 3. **Gestion Correcte du Pipeline KFP**
```bash
# Créer le bucket s'il n'existe pas
gsutil mb -l ${PIPELINE_REGION} gs://${BUCKET_NAME}

# Compiler le pipeline
python -c "from kfp.v2 import compiler..."

# Stocker le template pour réutilisation
gsutil cp digital_score_pipeline.yaml gs://${BUCKET_NAME}/...

# Soumettre à Vertex AI
python submit_pipeline.py ...
```

### 4. **Gestion d'Erreurs Robuste**
```bash
set -e  # Exit on error
set -o pipefail  # Detect errors in pipes

# Vérifications explicites
if [ ! -f digital_score_pipeline.yaml ]; then
  echo "❌ Erreur: fichier manquant"
  exit 1
fi

# Try/catch Python
try:
    compiler.Compiler().compile(...)
except Exception as e:
    print(f'❌ Erreur: {e}')
    exit(1)
```

### 5. **Dépendances Explicites**
```yaml
waitFor: ['run-tests']           # Étape 1 attend Étape 0
waitFor: ['compile-pipeline']    # Étape 2 attend Étape 1
waitFor: ['push-image']          # Étape 4 attend Étape 3
```

### 6. **Options de Configuration Globale**
```yaml
options:
  machineType: 'N1_HIGHCPU_8'    # Machine plus puissante
  logging: CLOUD_LOGGING_ONLY    # Logs structurés

timeout: '1800s'  # 30 minutes max
```

### 7. **Artefacts de Sortie**
```yaml
artifacts:
  objects:
    location: 'gs://${PROJECT_ID}-cloud-build-logs'
    paths:
      - 'test-results.xml'
      - 'src/digital_score_pipeline.yaml'
```

---

## 🔧 Comment Utiliser

### Configuration Initiale

1. **Adapter les variables à votre projet:**
```bash
# Dans Cloud Build UI ou via CLI
gcloud builds submit \
  --substitutions=_REGION="us-west1",_CLUSTER_NAME="my-cluster" \
  --config=src/cloudbuild.yaml .
```

2. **Créer les ressources GCP (si non existantes):**
```bash
# Artifact Registry
gcloud artifacts repositories create social-score-repo \
  --repository-format=docker \
  --location=us-west1

# GKE Cluster (si nécessaire)
gcloud container clusters create social-score-cluster \
  --zone us-west1-a \
  --num-nodes 3
```

### Déclencher le Pipeline

**Via GitHub (recommandé):**
1. Push vers `main` ou `develop`
2. Cloud Build s'exécute automatiquement

**Via CLI:**
```bash
gcloud builds submit --config src/cloudbuild.yaml .
```

**Via Cloud Build UI:**
1. Aller à Cloud Build → Triggers
2. Créer un trigger GitHub
3. Sélectionner ce fichier comme configuration

---

## 📊 Flux de Données

```
Git Push
   ↓
Cloud Build Trigger
   ↓
ÉTAPE 0: Tests
   ├─ Installe dépendances
   ├─ Télécharge NLTK data
   └─ Exécute pytest
   ↓
ÉTAPE 1: Pipeline KFP
   ├─ Crée bucket GCS
   ├─ Compile pipeline YAML
   ├─ Stocke template
   └─ Soumet à Vertex AI
   ↓
ÉTAPE 2: Docker Build
   ├─ Construit image
   └─ Tags COMMIT_SHA + latest
   ↓
ÉTAPE 3: Push AR
   └─ Pousse vers Artifact Registry
   ↓
ÉTAPE 4: Deploy GKE
   ├─ Configure kubectl
   ├─ Met à jour déploiement
   └─ Attend rolling update
   ↓
ÉTAPE 5: Verify
   └─ Affiche résumé et liens
```

---

## ✅ Checklist de Configuration

- [ ] Variables `substitutions` adaptées au projet
- [ ] Cluster GKE existe et est accessible
- [ ] Artifact Registry créé dans la région `_REGION`
- [ ] Service Account Cloud Build a les bonnes permissions
- [ ] Deployment Kubernetes créé (ou écrire une manifeste)
- [ ] GCS bucket créé pour les logs
- [ ] Trigger GitHub/Cloud Build configuré

---

## 🚨 Permissions Requises

Service Account Cloud Build doit avoir:
```yaml
roles:
  - roles/container.developer       # GKE access
  - roles/artifactregistry.writer   # AR push
  - roles/aiplatform.editor         # Vertex AI
  - roles/storage.admin             # GCS buckets
  - roles/logging.logWriter         # Cloud Logging
  - roles/cloudkms.cryptoKeyDecrypter  # Secrets (optionnel)
```

---

## 📈 Monitoring & Logging

### Voir les builds en cours
```bash
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)') -f
```

### Voir les artifacts
```bash
gcloud builds log BUILD_ID --stream
gsutil ls gs://PROJECT_ID-cloud-build-logs/
```

### Logs Kubernetes
```bash
kubectl logs -f deployment/social-score-deployment
kubectl describe pod PODNAME
```

---

## 🔧 Dépannage

| Erreur | Cause | Solution |
|--------|-------|----------|
| `pytest: command not found` | Dépendances test manquantes | `pip install -r requirements-test.txt` |
| `digital_score_pipeline.yaml not found` | Pipeline pas compilé | Vérifier `pipeline.py` dans `src/` |
| `Artifact not found` | Image push échoué | Vérifier credentials AR |
| `kubectl: command not found` | GKE credentials absent | `gcloud container clusters get-credentials` |
| `Deployment not found` | Déploiement n'existe pas | Créer la manifeste Kubernetes |

---

## 📚 Ressources

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Build YAML Schema](https://cloud.google.com/build/docs/build-config-file-schema)
- [Kubeflow Pipelines v2](https://www.kubeflow.org/docs/components/pipelines/)
- [Vertex AI Pipelines](https://cloud.google.com/vertex-ai/docs/pipelines)
- [GKE Deployment Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)

---

## 🎉 Résultat Final

Après chaque push:

1. ✅ Code testé automatiquement
2. ✅ Pipeline ML compilé et soumis
3. ✅ Image Docker construite et publiée
4. ✅ Application déployée sur GKE
5. ✅ Logs et artifacts conservés

**Pipeline production-ready! 🚀**
