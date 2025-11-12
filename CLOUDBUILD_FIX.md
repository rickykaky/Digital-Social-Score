# Configuration Cloud Build - Digital Social Score

## 🔧 Solution pour l'erreur de Service Account

### Problème rencontré :
```
if 'build.service_account' is specified, the build must either 
(a) specify 'build.logs_bucket', 
(b) use the REGIONAL_USER_OWNED_BUCKET build.options.default_logs_bucket_behavior option, 
or (c) use either CLOUD_LOGGING_ONLY / NONE logging options
```

### ✅ Solutions implémentées :

#### 1. Configuration du cloudbuild.yaml
- ✅ Option `logging: CLOUD_LOGGING_ONLY` ajoutée
- ✅ Aucun `serviceAccount` spécifié dans le fichier
- ✅ Utilisation du service account par défaut de Cloud Build

#### 2. Configuration du déclencheur Cloud Build

**Si vous configurez via l'interface Google Cloud :**

1. **Console Google Cloud** → Cloud Build → Déclencheurs
2. **Créer/Modifier le déclencheur** 
3. **Section "Configuration avancée"** :
   - **Service Account** : Laisser vide ou utiliser "Compte de service Cloud Build par défaut"
   - **Logging** : Sélectionner "Cloud Logging seulement"

**Si vous configurez via gcloud CLI :**

```bash
gcloud builds triggers create github \
  --repo-name="Digital-Social-Score" \
  --repo-owner="rickykaky" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --description="Digital Social Score - Main Branch" \
  --include-logs-with-status \
  --region="us-west1"
  # IMPORTANT: Ne pas spécifier --service-account
```

#### 3. Alternative avec Bucket de logs personnalisé

Si vous devez absolument utiliser un service account personnalisé, ajoutez ceci au cloudbuild.yaml :

```yaml
options:
  logging: CLOUD_LOGGING_ONLY
  logsBucket: 'gs://your-project-cloudbuild-logs'
  machineType: 'N1_HIGHCPU_8'

serviceAccount: 'projects/your-project/serviceAccounts/your-sa@your-project.iam.gserviceaccount.com'
```

### 🚀 Commandes de déploiement

#### Test local du build :
```bash
gcloud builds submit --config cloudbuild.yaml .
```

#### Création du déclencheur :
```bash
# Supprimer l'ancien déclencheur s'il existe
gcloud builds triggers delete [TRIGGER_NAME] --region=us-west1

# Créer le nouveau déclencheur
gcloud builds triggers create github \
  --repo-name="Digital-Social-Score" \
  --repo-owner="rickykaky" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --description="Digital Social Score - Build and Deploy" \
  --region="us-west1"
```

### 📋 Vérifications

1. **Vérifier le déclencheur** :
```bash
gcloud builds triggers list --region=us-west1
```

2. **Vérifier les permissions** :
```bash
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

3. **Test d'un build manuel** :
```bash
gcloud builds submit --config cloudbuild.yaml --region=us-west1 .
```

### 🔍 Diagnostic

Si l'erreur persiste, vérifiez :

1. **Pas de service account dans le déclencheur UI**
2. **cloudbuild.yaml contient `logging: CLOUD_LOGGING_ONLY`**  
3. **Pas de section `serviceAccount:` dans cloudbuild.yaml**
4. **Permissions du compte de service Cloud Build par défaut**

Le service account par défaut est : 
`[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`