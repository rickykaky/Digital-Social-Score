# 🚀 Intégration Pipeline Vertex AI dans Cloud Build

## 📋 Vue d'ensemble de l'architecture

```
Cloud Build Trigger (git push)
    ↓
Étape 0: Pipeline Kubeflow (submit_pipeline.py)
    - Compile pipeline.py → digital_score_pipeline.yaml
    - Soumet à Vertex AI Pipelines via submit_pipeline.py
    ↓
Étape 1: Tests et Dépendances
    ↓
Étape 2: Build Docker
    ↓
Étape 3: Push Artifact Registry
    ↓
Étape 4: Déploiement GKE
```

---

## 📂 Fichiers impliqués

### 1. **`pipeline.py`** (Définition du pipeline)
   - Contient les 3 composants KFP : `prepare_data_op`, `train_model_op`, `evaluate_model_op`
   - Définit la fonction principale `digital_score_pipeline()`

### 2. **`submit_pipeline.py`** (Soumission à Vertex AI)
   - Utilise `aiplatform.PipelineJob()` pour soumettre le pipeline
   - Deux fonctions principales :
     - `run_vertex_pipeline()` : soumet un pipeline déjà compilé
     - `submit_pipeline_from_local()` : compile puis soumet
   - Accepte des arguments CLI pour flexibilité

### 3. **`cloudbuild.yaml`** (Orchestration)
   - **Étape 0** : Appelle `submit_pipeline.py` pour compiler et soumettre
   - **Étapes 1-4** : Procédure standard (tests, Docker, GKE)

---

## 🔧 Configuration requise

### 1. **Variables d'environnement Cloud Build**

Dans Cloud Build, définir :
```bash
PROJECT_ID         # Ton ID GCP
PIPELINE_REGION    # Région (default: us-west1)
BUCKET_NAME        # ${PROJECT_ID}-digital-social-score
```

### 2. **Permissions Service Account**

La service account Cloud Build doit avoir :
```
Vertex AI Administrator
Storage Admin (pour bucket GCS)
Kubernetes Engine Developer
```

### 3. **Bucket GCS pour artefacts**

```bash
gsutil mb gs://${PROJECT_ID}-digital-social-score
gsutil mb gs://${PROJECT_ID}-digital-social-score/pipeline-templates
gsutil mb gs://${PROJECT_ID}-digital-social-score/pipeline-root
```

### 4. **Dépendances Python**

`requirements.txt` doit inclure :
```
kfp==2.0.0
google-cloud-aiplatform>=1.26.0
pandas
scikit-learn
nltk
joblib
```

---

## 🚀 Utilisation

### **Déclenchement automatique (git push)**

```bash
git push origin main
```

Cloud Build exécutera automatiquement :
1. Compilation du pipeline
2. Soumission à Vertex AI
3. Build et déploiement

### **Exécution manuelle du pipeline**

```bash
# Mode 1: Soumettre un pipeline déjà compilé
python src/submit_pipeline.py \
  --project my-project \
  --region us-west1 \
  --template gs://my-project-digital-social-score/pipeline-templates/digital_score_pipeline.yaml

# Mode 2: Compiler puis soumettre
python src/submit_pipeline.py \
  --project my-project \
  --region us-west1 \
  --compile
```

### **Via gcloud (alternative)**

```bash
gcloud ai pipelines runs submit \
  --region=us-west1 \
  --pipeline-root=gs://my-project-digital-social-score/pipeline-root \
  --display-name='Digital-Social-Score-Pipeline' \
  --yaml-pipeline-spec=gs://my-project-digital-social-score/pipeline-templates/digital_score_pipeline.yaml
```

---

## 📊 Flux du pipeline Vertex AI

```
[raw train.csv] 
    ↓
[Étape 1: prepare_data_op]
    - Nettoyage du texte
    - NLTK (tokenisation, stopwords, lemmatisation)
    ↓
[clean.csv]
    ↓
[Étape 2: train_model_op]
    - TF-IDF vectorisation
    - LogisticRegression
    ↓
[model.joblib + vectorizer.joblib]
    ↓
[Étape 3: evaluate_model_op]
    - Calcul accuracy, precision, recall, F1
    ↓
[Métriques + Logs]
```

---

## 🔍 Suivi et Monitoring

### **Console Vertex AI**
```
https://console.cloud.google.com/vertex-ai/pipelines/runs?project=YOUR_PROJECT_ID
```

### **Logs Cloud Build**
```
https://console.cloud.google.com/cloud-build/builds?project=YOUR_PROJECT_ID
```

### **Artefacts dans GCS**
```bash
gsutil ls gs://${PROJECT_ID}-digital-social-score/pipeline-root/
```

---

## ⚠️ Troubleshooting

### **Erreur: "kfp.v2 not found"**
```bash
pip install kfp==2.0.0
```

### **Erreur: "Permission denied"**
Vérifier que la service account Cloud Build a les permissions :
```bash
gcloud projects get-iam-policy ${PROJECT_ID} \
  --flatten="bindings[].members" \
  --filter="bindings.members:*@cloudbuild.gserviceaccount.com"
```

### **Erreur: "Bucket not found"**
Créer le bucket :
```bash
gsutil mb gs://${PROJECT_ID}-digital-social-score
```

### **Pipeline timeout**
Augmenter le timeout dans `cloudbuild.yaml` :
```yaml
timeout: '3600s'  # 1 heure
```

---

## 📚 Ressources

- [Kubeflow Pipelines v2 Documentation](https://www.kubeflow.org/docs/components/pipelines/v2/)
- [Vertex AI Pipelines Guide](https://cloud.google.com/vertex-ai/docs/pipelines/introduction)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)

---

## ✅ Checklist Déploiement

- [ ] `pipeline.py` créé avec 3 composants
- [ ] `submit_pipeline.py` créé
- [ ] `cloudbuild.yaml` mis à jour avec Étape 0
- [ ] `requirements.txt` inclut kfp, google-cloud-aiplatform
- [ ] Bucket GCS créé
- [ ] Service account avec permissions Vertex AI
- [ ] Secrets GCP configurés (si nécessaire)
- [ ] Test manuel : `python submit_pipeline.py --compile`
- [ ] Git push pour déclencher Cloud Build

---

**Prêt ? 🚀 Envoie un `git push` pour lancer le pipeline complet !**
