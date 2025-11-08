# 📚 GUIDE GLOBAL - Où Trouver Quoi

## 🎯 Vous êtes Nouveau ? Commencez Ici !

```
1. Lire : DEPLOYMENT_READY.txt (ce répertoire racine)
   ↓
2. Lire : deployment/README.md
   ↓
3. Exécuter : deployment/scripts/pre_deployment_check.py
   ↓
4. Lire : deployment/DEPLOYMENT_COMPLETE_CHECKLIST.md
   ↓
5. Déployer : deployment/scripts/deploy.sh
```

---

## 📂 Arborescence Complète du Projet

```
Digital-Social-Score/
│
├── 📄 DEPLOYMENT_READY.txt  ← 🌟 LISEZ CECI EN PREMIER !
│
├── 📄 README.md  (du projet global)
│
├── 🔍 .github/
│   └── workflows/
│       └── tests.yml  (GitHub Actions CI/CD)
│
├── 🏗️  src/
│   ├── app.py  (FastAPI application)
│   ├── config.py  (Configuration 3 environnements)
│   ├── cloudbuild.yaml  (Cloud Build pipeline - 5 stages)
│   ├── pipeline/  (KFP v2 pipeline)
│   ├── ml/  (Machine learning code)
│   └── utils/  (Utilities)
│
├── 📊 tests/
│   ├── conftest.py  (20+ pytest fixtures)
│   ├── TEST_TEMPLATE.py  (Template avec best practices)
│   ├── unit/  (60+ unit tests)
│   ├── integration/  (50+ integration tests)
│   ├── pipeline/  (30+ pipeline tests)
│   └── ml/  (40+ ML tests)
│
├── 📈 deployment/  ← 🎉 INFRASTRUCTURE DE DÉPLOIEMENT
│   ├── 📋 README.md  ← 🌟 INDEX PRINCIPAL
│   ├── ✅ DEPLOYMENT_COMPLETE_CHECKLIST.md
│   ├── 🎯 K8S_DEPLOYMENT_GUIDE.md
│   ├── 🔄 CICD_COMPLETE_GUIDE.md
│   ├── 📦 DELIVERY_SUMMARY.md
│   │
│   ├── k8s/
│   │   ├── social-score-deployment.yaml  (Manifeste K8s)
│   │   └── ingress.yaml  (Ingress + SSL)
│   │
│   └── scripts/
│       ├── deploy.sh  (🤖 Déploiement automatisé)
│       └── pre_deployment_check.py  (✅ 15 vérifications)
│
├── 📄 requirements.txt
├── 📄 requirements-test.txt
├── 📄 Dockerfile
├── 📄 docker-compose.yml
└── 📄 Makefile  (Build commands)
```

---

## 🗂️ Guide par Rôle

### 👨‍💻 Développeurs

**Vous voulez** : Contribuer au code

**Allez à** :
1. README.md (du projet)
2. src/app.py (voir l'API)
3. tests/TEST_TEMPLATE.py (comment écrire les tests)
4. .github/workflows/tests.yml (CI/CD automatique)

**Workflow** :
1. Feature branch
2. Développer + tester
3. PR
4. GitHub Actions teste automatiquement
5. Merge
6. Cloud Build déploie

---

### 🔧 DevOps / Cloud Engineers

**Vous voulez** : Déployer et gérer l'infrastructure

**Allez à** :
1. 👉 **DEPLOYMENT_READY.txt** (vue globale rapide)
2. deployment/README.md (index principal)
3. deployment/DEPLOYMENT_COMPLETE_CHECKLIST.md (procédures)
4. deployment/K8S_DEPLOYMENT_GUIDE.md (détails techniques)
5. deployment/CICD_COMPLETE_GUIDE.md (pipeline CI/CD)

**Étapes** :
1. Lire DEPLOYMENT_COMPLETE_CHECKLIST.md
2. Exécuter : python3 deployment/scripts/pre_deployment_check.py
3. Configurer GCP (suivre guide)
4. Configurer Cloud Build (suivre guide)
5. Déployer : ./deployment/scripts/deploy.sh

---

### 🔍 SRE / Operations

**Vous voulez** : Monitorer et maintenir le système

**Allez à** :
1. deployment/K8S_DEPLOYMENT_GUIDE.md (section 6 - monitoring)
2. deployment/CICD_COMPLETE_GUIDE.md (section 6 - monitoring)
3. src/config.py (env variables)
4. Dockerfile (dépendances)

**Responsabilités** :
- Configurer Cloud Logging
- Configurer Cloud Monitoring
- Mettre en place les alertes
- Surveiller les performances
- Gérer les incidents

---

### 📊 ML Engineers

**Vous voulez** : Entraîner et déployer les modèles

**Allez à** :
1. src/pipeline/ (pipeline KFP v2)
2. src/ml/ (code ML)
3. tests/ml/ (tests ML)
4. src/cloudbuild.yaml (pipeline stages)

**Workflow** :
1. Développer pipeline KFP
2. Tests locaux
3. Cloud Build compile et soumet à Vertex AI
4. Pipeline s'exécute sur Vertex AI

---

## 📋 Documentation par Sujet

### 🚀 Déploiement

**Je veux déployer pour la première fois** :
→ deployment/README.md
→ deployment/DEPLOYMENT_COMPLETE_CHECKLIST.md

**Je veux comprendre Kubernetes** :
→ deployment/K8S_DEPLOYMENT_GUIDE.md

**Je veux comprendre CI/CD** :
→ deployment/CICD_COMPLETE_GUIDE.md

---

### 🔄 Pipeline CI/CD

**Je veux configurer Cloud Build** :
→ deployment/CICD_COMPLETE_GUIDE.md (section 3)

**Je veux configurer GitHub** :
→ deployment/CICD_COMPLETE_GUIDE.md (section 4)

**Je veux comprendre le workflow** :
→ deployment/CICD_COMPLETE_GUIDE.md (section 5)

---

### 📊 Testing

**Je veux écrire des tests** :
→ tests/TEST_TEMPLATE.py (template avec exemples)

**Je veux exécuter les tests** :
```bash
pytest tests/ -v  # Tous les tests
pytest tests/unit/ -v  # Unit tests seulement
make test  # Via Makefile
```

---

### 🔍 Troubleshooting

**Il y a un problème** :
1. Exécuter : `python3 deployment/scripts/pre_deployment_check.py`
2. Vérifier les logs : `kubectl logs -l app=social-score-api`
3. Lire : deployment/K8S_DEPLOYMENT_GUIDE.md (section 8)

**Erreur Cloud Build** :
→ deployment/CICD_COMPLETE_GUIDE.md (section 8)

**Erreur Kubernetes** :
→ deployment/K8S_DEPLOYMENT_GUIDE.md (section 8)

---

## 🎓 Procédures Rapides

### Déployer (5 min)

```bash
# Vérifier les prérequis
python3 deployment/scripts/pre_deployment_check.py \
  --project YOUR_PROJECT --cluster YOUR_CLUSTER

# Déployer
./deployment/scripts/deploy.sh \
  --project YOUR_PROJECT \
  --cluster social-score-cluster
```

### Vérifier (5 min)

```bash
# Voir les pods
kubectl get pods -l app=social-score-api

# Voir les logs
kubectl logs -l app=social-score-api -f

# Vérifier le service
kubectl get svc social-score-service
```

### Tester (10 min)

```bash
# Exécuter tous les tests
pytest tests/ -v

# Exécuter les tests d'une catégorie
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/pipeline/ -v
pytest tests/ml/ -v

# Voir la couverture
pytest tests/ --cov=src --cov-report=html
```

### Rollback (2 min)

```bash
# Voir l'historique
kubectl rollout history deployment/social-score-deployment

# Rollback à la version précédente
kubectl rollout undo deployment/social-score-deployment

# Vérifier
kubectl rollout status deployment/social-score-deployment
```

---

## 📞 Ressources Utiles

### Documentation Officielle
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [GitHub Actions](https://docs.github.com/en/actions)

### Guides Internes
- deployment/README.md
- deployment/K8S_DEPLOYMENT_GUIDE.md
- deployment/CICD_COMPLETE_GUIDE.md
- deployment/DEPLOYMENT_COMPLETE_CHECKLIST.md

### Scripts Utiles
```bash
# Déployer
./deployment/scripts/deploy.sh

# Vérifier les prérequis
python3 deployment/scripts/pre_deployment_check.py

# Tester
make test

# Coverage
make coverage

# Lint
make lint

# Tout (CI)
make ci
```

---

## ✅ Checklist Installation Initiale

- [ ] J'ai lu DEPLOYMENT_READY.txt
- [ ] J'ai lu deployment/README.md
- [ ] J'ai exécuté pre_deployment_check.py
- [ ] J'ai configuré GCP resources
- [ ] J'ai configuré Cloud Build triggers
- [ ] J'ai exécuté deploy.sh
- [ ] J'ai vérifié que les pods tournent
- [ ] J'ai testé l'API
- [ ] J'ai configuré le monitoring

---

## 🎉 Résumé

**Infrastructure déployable** : ✅
**Documentation** : ✅
**Scripts automatisés** : ✅
**Tests** : ✅
**CI/CD** : ✅

**Prêt pour production** : ✅

---

## 📝 Notes

- Tous les chemins sont relatifs à la racine du projet
- Les scripts supposent que vous êtes dans le répertoire racine
- Les variables d'environnement doivent être adaptées à votre projet
- Les permissions GCP doivent être configurées correctement

---

## 🆘 Questions Fréquentes

**Q: Par où commencer ?**
A: Lisez DEPLOYMENT_READY.txt, puis deployment/README.md

**Q: Comment déployer ?**
A: Exécutez deployment/scripts/deploy.sh (après configuration)

**Q: Comment tester ?**
A: pytest tests/ -v (ou make test)

**Q: Il y a une erreur, comment fixer ?**
A: Exécutez pre_deployment_check.py d'abord

**Q: Comment monitorer ?**
A: Voir deployment/K8S_DEPLOYMENT_GUIDE.md (section 6)

---

**Status** : ✅ Prêt
**Date** : 2024
**Version** : 1.0
