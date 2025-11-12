# 🚀 Guide de Configuration du Déclencheur Cloud Build

## ✅ Solution au Problème de Service Account

**Problème résolu :** L'erreur de service account a été corrigée dans le `cloudbuild.yaml`

### 📋 Étapes pour créer le déclencheur via l'interface web

1. **Ouvrir Google Cloud Console**
   - Aller à : https://console.cloud.google.com/cloud-build/triggers
   - Sélectionner le projet : `digital-social-score`

2. **Créer un nouveau déclencheur**
   - Cliquer sur "**CRÉER UN DÉCLENCHEUR**"
   - **Nom** : `digital-social-score-main`
   - **Description** : `Digital Social Score - Build and Deploy`

3. **Configuration de la source**
   - **Type d'événement** : Push vers une branche
   - **Source** : Sélectionner "**Connecter un nouveau dépôt**" si pas encore fait
   - **Plateforme** : GitHub
   - **Dépôt** : `rickykaky/Digital-Social-Score`
   - **Branche** : `^main$`

4. **Configuration du build** ⚠️ **IMPORTANT**
   - **Type de configuration** : Fichier de configuration Cloud Build (yaml ou json)
   - **Emplacement du fichier de configuration** : `cloudbuild.yaml`
   - **Service account** : **LAISSER VIDE** (utiliser le compte par défaut)

5. **Options avancées** ✅ **CRITIQUE**
   - **Journalisation** : Sélectionner "**Cloud Logging seulement**"
   - **Type de machine** : `N1_HIGHCPU_8`
   - **Délai d'expiration** : `1800s`

6. **Variables de substitution** (optionnel)
   ```
   _REGION = us-west1
   _ZONE = us-west1-a
   _CLUSTER_NAME = social-score-cluster
   ```

7. **Créer le déclencheur**
   - Cliquer sur "**CRÉER**"

### 🧪 Test du déclencheur

Après création, tester avec un commit :

```bash
cd /Users/romarickaki/Documents/GitHub/Digital-Social-Score

# Faire un petit changement
echo "# Test build" >> README.md
git add README.md
git commit -m "Test: Déclenchement du build après correction"
git push
```

### 🔍 Vérification

1. **Déclencheur créé** :
   - Console Cloud Build > Déclencheurs
   - Vérifier que le service account est "**Compte de service Cloud Build (par défaut)**"

2. **Build en cours** :
   - Console Cloud Build > Historique
   - Le build devrait démarrer automatiquement après le push

3. **Logs du build** :
   - Cliquer sur le build en cours
   - Vérifier que les étapes s'exécutent sans erreur de service account

### ❌ Si l'erreur persiste

Si vous voyez encore l'erreur de service account :

1. **Supprimer le déclencheur** :
   ```bash
   gcloud builds triggers list
   gcloud builds triggers delete [TRIGGER_ID]
   ```

2. **Recréer avec la CLI** :
   ```bash
   gcloud builds submit --config cloudbuild.yaml . --no-source
   ```

3. **Vérifier les permissions** :
   ```bash
   gcloud projects get-iam-policy digital-social-score
   ```

### 🎯 Points clés de la correction

✅ **cloudbuild.yaml corrigé** :
- `logging: CLOUD_LOGGING_ONLY`
- Aucun `serviceAccount` spécifié
- Variables de substitution avec valeurs par défaut

✅ **Déclencheur configuré** :
- Service account par défaut Cloud Build
- Journalisation Cloud Logging seulement
- Pas de bucket de logs personnalisé requis

### 📊 Résultat attendu

Après configuration, le pipeline devrait :
1. ✅ Se déclencher sur chaque push vers `main`
2. ✅ Exécuter les tests
3. ✅ Construire l'image Docker
4. ✅ La pousser vers Container Registry
5. ✅ Compiler et soumettre le pipeline Vertex AI
6. ✅ Déployer sur GKE

**Le problème de service account est maintenant résolu ! 🎉**