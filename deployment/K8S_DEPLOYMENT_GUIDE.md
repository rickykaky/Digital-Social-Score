# Guide de Déploiement Kubernetes - Social Score API

## Table des matières

1. [Architecture de Déploiement](#architecture-de-déploiement)
2. [Prérequis](#prérequis)
3. [Configuration GCP](#configuration-gcp)
4. [Déploiement Manuel](#déploiement-manuel)
5. [Déploiement Automatisé](#déploiement-automatisé)
6. [Vérification et Monitoring](#vérification-et-monitoring)
7. [Rollback et Troubleshooting](#rollback-et-troubleshooting)
8. [Considérations de Production](#considérations-de-production)

---

## Architecture de Déploiement

```
┌─────────────────────────────────────────────────────────────┐
│                    GCP Project                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              GKE Cluster (us-west1-a)               │   │
│  │                                                       │   │
│  │  ┌────────────────────────────────────────────────┐ │   │
│  │  │        Load Balancer / Ingress                 │ │   │
│  │  │  (social-score-service:80)                     │ │   │
│  │  └────────────────────────────────────────────────┘ │   │
│  │                       │                              │   │
│  │                       ▼                              │   │
│  │  ┌────────────────────────────────────────────────┐ │   │
│  │  │         HPA (3-10 replicas)                    │ │   │
│  │  │  ┌──────┐  ┌──────┐  ┌──────┐                 │ │   │
│  │  │  │ Pod1 │  │ Pod2 │  │ Pod3 │ ... (Max 10)   │ │   │
│  │  │  └──────┘  └──────┘  └──────┘                 │ │   │
│  │  └────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │  ┌────────────────────────────────────────────────┐ │   │
│  │  │    ConfigMap (social-score-config)            │ │   │
│  │  │    ServiceAccount (social-score-sa)          │ │   │
│  │  │    PDB (Pod Disruption Budget)                │ │   │
│  │  └────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │      Artifact Registry (social-score-repo)          │   │
│  │  Image: social-score-api:latest                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Cloud Storage (GCS)                         │   │
│  │  - Pipeline templates                                │   │
│  │  - Logs                                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Prérequis

### Logiciels requis

```bash
# macOS (via Homebrew)
brew install google-cloud-sdk
brew install kubectl
brew install helm

# Ou manuellement
curl https://sdk.cloud.google.com | bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
```

### Authentification GCP

```bash
# Configurer gcloud
gcloud auth login
gcloud config set project PROJECT_ID

# Configurer Docker authentication (Artifact Registry)
gcloud auth configure-docker us-west1-docker.pkg.dev

# Vérifier les credentials
gcloud auth list
gcloud config list
```

### Permissions requises

L'account utilisé doit avoir les rôles suivants :

```
- Kubernetes Engine > Kubernetes Engine Developer
- Kubernetes Engine > Service Accounts User
- Container Registry > Service Agent
- Artifact Registry > Repository Administrator
- Vertex AI > Pipelines User
- Cloud Build > Editor
- GCS > Storage Object Admin
```

Attribuer les rôles :

```bash
PROJECT_ID="your-project-id"
SERVICE_ACCOUNT_EMAIL="your-service-account@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/artifactregistry.repoAdmin"
```

---

## Configuration GCP

### 1. Créer le cluster GKE

```bash
PROJECT_ID="your-project-id"
CLUSTER_NAME="social-score-cluster"
ZONE="us-west1-a"
REGION="us-west1"

# Créer le cluster
gcloud container clusters create $CLUSTER_NAME \
  --zone $ZONE \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --enable-stackdriver-kubernetes \
  --addons HttpLoadBalancing,HttpsLoadBalancing \
  --enable-ip-alias \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-vertical-pod-autoscaling \
  --enable-network-policy

# Obtenir les credentials
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE

# Vérifier la connexion
kubectl cluster-info
kubectl get nodes
```

### 2. Créer le dépôt Artifact Registry

```bash
REPO="social-score-repo"

gcloud artifacts repositories create $REPO \
  --repository-format=docker \
  --location=$REGION \
  --description="Repository for Social Score API"

# Lister les dépôts
gcloud artifacts repositories list

# Configurer Docker
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### 3. Créer le bucket GCS

```bash
BUCKET_NAME="social-score-${PROJECT_ID}"

gsutil mb gs://${BUCKET_NAME}/

# Configurer les permissions
gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_EMAIL}:objectAdmin \
  gs://${BUCKET_NAME}/
```

### 4. Créer l'adresse IP statique

```bash
gcloud compute addresses create social-score-ip \
  --global \
  --region=$REGION
```

---

## Déploiement Manuel

### Étape 1 : Vérifier les fichiers de déploiement

```bash
# Lister les fichiers de déploiement
ls -la deployment/k8s/

# Vérifier la syntaxe YAML
kubectl apply -f deployment/k8s/ --dry-run=client
```

### Étape 2 : Remplacer les variables

```bash
# Dans social-score-deployment.yaml, remplacer:
# - PROJECT_ID par votre ID de projet
# - social-score-cluster par votre cluster
# - us-west1-a par votre zone
sed -i '' 's/PROJECT_ID/your-project-id/g' deployment/k8s/social-score-deployment.yaml

# Dans ingress.yaml, remplacer:
# - social-score.example.com par votre domaine
# - social-score-ip par votre adresse IP
sed -i '' 's/social-score.example.com/your-domain.com/g' deployment/k8s/ingress.yaml
```

### Étape 3 : Appliquer les manifestes

```bash
# Créer le namespace (si utilisé)
kubectl create namespace production

# Appliquer les manifestes
kubectl apply -f deployment/k8s/social-score-deployment.yaml
kubectl apply -f deployment/k8s/ingress.yaml

# Vérifier le déploiement
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress
```

### Étape 4 : Vérifier le statut

```bash
# Vérifier les pods
kubectl get pods -l app=social-score-api -o wide

# Attendre le rollout
kubectl rollout status deployment/social-score-deployment

# Voir les logs
kubectl logs -l app=social-score-api -f

# Vérifier les événements
kubectl get events --sort-by='.lastTimestamp'
```

---

## Déploiement Automatisé

### Utiliser le script deploy.sh

```bash
# Rendre le script exécutable
chmod +x deployment/scripts/deploy.sh

# Afficher l'aide
./deployment/scripts/deploy.sh --help

# Déploiement complet
./deployment/scripts/deploy.sh \
  --project your-project-id \
  --cluster social-score-cluster \
  --zone us-west1-a \
  --region us-west1 \
  --image social-score-api \
  --tag latest

# Mode dry-run
./deployment/scripts/deploy.sh \
  --project your-project-id \
  --cluster social-score-cluster \
  --dry-run
```

### Options du script

```
-p, --project       ID du projet GCP (requis)
-c, --cluster       Nom du cluster GKE (requis)
-z, --zone          Zone du cluster (défaut: us-west1-a)
-r, --region        Région du dépôt (défaut: us-west1)
-i, --image         Nom de l'image (défaut: social-score-api)
-t, --tag           Tag de l'image (défaut: latest)
-n, --namespace     Namespace K8s (défaut: default)
-d, --dry-run       Mode simulation
-v, --verbose       Mode verbose
-h, --help          Afficher l'aide
```

---

## Vérification et Monitoring

### Vérifier le déploiement

```bash
# État général
kubectl get all -l app=social-score-api

# Détails du déploiement
kubectl describe deployment social-score-deployment

# Détails des pods
kubectl describe pods -l app=social-score-api

# Ressources utilisées
kubectl top nodes
kubectl top pods -l app=social-score-api

# Vérifier les health checks
kubectl get endpoints social-score-service
```

### Accéder à l'API

```bash
# Port-forward
kubectl port-forward svc/social-score-service 8000:80

# Tester l'API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{"text": "Mon email est test@example.com"}'

# Depuis l'extérieur (après Ingress setup)
curl https://social-score.example.com/health
```

### Consulter les logs

```bash
# Logs d'un pod
kubectl logs <pod-name>

# Logs en temps réel
kubectl logs -f <pod-name>

# Logs de tous les pods
kubectl logs -l app=social-score-api -f

# Logs précédents (crash)
kubectl logs <pod-name> --previous

# Logs structurés
kubectl logs <pod-name> -c social-score-api --timestamps=true
```

### Monitoring avec Prometheus/Grafana

```bash
# Installer Prometheus (optionnel)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Vérifier les métriques
kubectl port-forward svc/prometheus-operated 9090:9090

# Acceder aux métriques
curl http://localhost:9090/api/v1/targets
curl http://localhost:9090/api/v1/query?query=http_requests_total
```

---

## Rollback et Troubleshooting

### Rollback de déploiement

```bash
# Voir l'historique
kubectl rollout history deployment/social-score-deployment

# Voir les détails d'une révision
kubectl rollout history deployment/social-score-deployment --revision=2

# Rollback à la version précédente
kubectl rollout undo deployment/social-score-deployment

# Rollback à une version spécifique
kubectl rollout undo deployment/social-score-deployment --to-revision=2

# Vérifier le statut du rollback
kubectl rollout status deployment/social-score-deployment
```

### Diagnostiquer les problèmes

```bash
# Pods dans l'erreur
kubectl get pods -l app=social-score-api --field-selector=status.phase=Failed

# Voir l'erreur exacte
kubectl describe pod <pod-name>

# Executer une commande dans le pod
kubectl exec -it <pod-name> -- /bin/bash

# Vérifier les volumes
kubectl get pv,pvc

# Vérifier les services de réseau
kubectl get networkpolicy

# Voir tous les événements
kubectl get events --all-namespaces --sort-by='.lastTimestamp'

# Tester la connectivité
kubectl run -it --rm debug --image=busybox -- sh
# Dans le pod: wget -O- http://social-score-service
```

### Problèmes courants

#### Pods en CrashLoopBackOff

```bash
# Vérifier les logs
kubectl logs <pod-name> --previous

# Vérifier la configuration
kubectl get pod <pod-name> -o yaml | grep -A 10 "env:"

# Vérifier les ressources
kubectl describe node

# Augmenter les ressources
kubectl set resources deployment social-score-deployment \
  --requests=cpu=200m,memory=512Mi \
  --limits=cpu=1000m,memory=1Gi
```

#### Image not found

```bash
# Vérifier l'image
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/social-score-repo

# Vérifier les credentials
kubectl get secrets
kubectl describe secret $(kubectl get secrets | grep default | awk '{print $1}')

# Créer un secret pour Docker
kubectl create secret docker-registry gcr-json-key \
  --docker-server=${REGION}-docker.pkg.dev \
  --docker-username=_json_key \
  --docker-password="$(cat ~/key.json)"
```

#### Service not accessible

```bash
# Vérifier le service
kubectl get svc social-score-service
kubectl describe svc social-score-service

# Vérifier les endpoints
kubectl get endpoints social-score-service

# Tester la connectivité
kubectl run -it --rm debug --image=busybox -- wget -O- http://social-score-service

# Vérifier le NetworkPolicy
kubectl get networkpolicy
```

---

## Considérations de Production

### Sécurité

```bash
# 1. Pod Security Policy
kubectl label namespace default pod-security.kubernetes.io/enforce=restricted

# 2. Network Policy
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: social-score-netpol
spec:
  podSelector:
    matchLabels:
      app: social-score-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
  egress:
  - to:
    - podSelector:
        matchLabels:
          role: database
EOF

# 3. RBAC
kubectl create rolebinding social-score-rb \
  --clusterrole=edit \
  --serviceaccount=default:social-score-sa \
  --namespace=default
```

### Backup et Disaster Recovery

```bash
# Sauvegarder les manifestes
kubectl get all -o yaml > backup-$(date +%Y%m%d).yaml

# Restaurer
kubectl apply -f backup-*.yaml

# Utiliser velero pour backup automatique
helm repo add velero https://charts.velero.io
helm install velero velero/velero \
  --namespace velero --create-namespace \
  --values velero-values.yaml
```

### Logging et Monitoring

```bash
# Google Cloud Logging
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=default" \
  --limit 50

# Stackdriver pour GKE
kubectl port-forward -n kube-system svc/stackdriver-metrics-agent 8888:8888

# Configurer les alertes
gcloud alpha monitoring policies create \
  --display-name="Social Score API High Error Rate" \
  --condition-display-name="Error Rate > 5%"
```

### Performance Tuning

```bash
# Augmenter les limites de ressources
kubectl set resources deployment social-score-deployment \
  --requests=cpu=250m,memory=512Mi \
  --limits=cpu=1000m,memory=1Gi

# Configurer l'auto-scaling
kubectl patch hpa social-score-hpa -p '{"spec":{"maxReplicas":20}}'

# Vérifier les métriques HPA
kubectl get hpa social-score-hpa
kubectl describe hpa social-score-hpa
```

---

## Commandes Utiles

```bash
# Raccourcis utiles
alias k='kubectl'
alias kg='kubectl get'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deploy'

# Voir tout
k get all -l app=social-score-api

# Redémarrer le déploiement
k rollout restart deployment/social-score-deployment

# Augmenter les replicas
k scale deployment social-score-deployment --replicas=5

# Mettre en place une mise à jour (Rolling update)
k set image deployment/social-score-deployment \
  social-score-api=us-west1-docker.pkg.dev/PROJECT_ID/social-score-repo/social-score-api:v2

# Supprimer tout
k delete all -l app=social-score-api
```

---

## Ressources Supplémentaires

- [Documentation Kubernetes](https://kubernetes.io/docs/)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Troubleshooting Guide](https://kubernetes.io/docs/tasks/debug-application-cluster/)
