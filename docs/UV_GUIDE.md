# 🚀 Guide uv - Package Manager Ultra-Rapide

## 🎯 **Pourquoi uv ?**

**uv** est le nouveau package manager Python développé par Astral (créateurs de Ruff). Il révolutionne la gestion des dépendances Python.

### 📊 **Performance**
```
Benchmark d'installation typique (requirements.txt avec 30+ packages):

pip install        : 📊▓▓▓▓▓▓▓▓▓▓ 120s
uv pip install     : 🚀▓ 8s        (15x plus rapide)

Cache hit (déjà téléchargé):
pip install        : 📊▓▓▓▓ 45s
uv pip install     : ⚡ 1.5s       (30x plus rapide)
```

## 🛠️ **Usage dans le Projet**

### 1. **Dockerfile (Performance Docker)**
```dockerfile
# Installation ultra-rapide dans Docker
RUN pip install uv
RUN uv pip install --system --no-cache -r requirements.txt
```

### 2. **Cloud Build (CI/CD Rapide)**
```yaml
- |
  pip install uv
  uv pip install --system -r requirements.txt
  uv pip install --system -r requirements-test.txt
```

### 3. **GitHub Actions (Tests Plus Rapides)**
```yaml
- name: Install uv
  run: pip install uv
- name: Install deps
  run: uv pip install --system -r requirements.txt
```

### 4. **Développement Local**
```bash
# Installation d'uv
pip install uv

# Utilisation comme pip (compatible 100%)
uv pip install -r requirements.txt
uv pip install pandas numpy
uv pip list
uv pip freeze > requirements.txt
```

## 🎯 **Commandes uv Essentielles**

### Installation de Packages
```bash
# Compatible avec pip
uv pip install package_name
uv pip install -r requirements.txt
uv pip install --system -r requirements.txt  # Pour Docker/CI

# Plus rapide pour plusieurs packages
uv pip install pandas numpy scikit-learn
```

### Gestion d'Environnement
```bash
# Créer un environnement virtuel
uv venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installation dans l'environnement
uv pip install -r requirements.txt
```

### Avec pyproject.toml (Moderne)
```bash
# Synchroniser les dépendances
uv sync

# Ajouter une dépendance
uv add pandas

# Supprimer une dépendance
uv remove pandas

# Mettre à jour le lock file
uv lock
```

## 📦 **Migration depuis pip**

### 1. **Remplacement Direct (Compatible 100%)**
```bash
# Avant (pip)
pip install -r requirements.txt

# Après (uv) 
uv pip install -r requirements.txt
```

### 2. **Migration Moderne (pyproject.toml)**
```bash
# 1. Créer pyproject.toml (voir exemple dans le projet)
# 2. Migration automatique
uv init  # Génère la structure
uv add $(cat requirements.txt)  # Import des dépendances
```

## 🔧 **Configuration Avancée**

### Cache Personnalisé
```bash
# Définir le répertoire de cache
export UV_CACHE_DIR=/path/to/cache
uv pip install -r requirements.txt
```

### Parallélisme
```bash
# Contrôler le nombre de téléchargements simultanés
uv pip install -r requirements.txt --concurrent-downloads 10
```

### Index Personnalisé
```bash
# Utiliser un index PyPI privé
uv pip install -r requirements.txt --index-url https://private-pypi.com/simple
```

## 🐛 **Résolution de Problèmes**

### Problèmes Courants
```bash
# 1. Conflit avec pip dans Docker
RUN pip install uv && uv pip install --system -r requirements.txt

# 2. Permissions dans CI/CD
uv pip install --system -r requirements.txt

# 3. Cache corrompu
uv cache clean
```

### Debug et Informations
```bash
# Informations sur uv
uv --version
uv pip --help

# Cache info
uv cache dir
uv cache clean

# Mode verbose
uv pip install -r requirements.txt -v
```

## 📊 **Intégration dans votre Workflow**

### Workflow Recommandé
```bash
1. Développement Local
   uv venv && source venv/bin/activate
   uv pip install -r requirements.txt
   
2. Tests en Local
   uv pip install -r requirements-test.txt
   pytest tests/
   
3. Build Docker
   docker build .  # Utilise uv automatiquement
   
4. CI/CD
   # GitHub Actions et Cloud Build utilisent uv
   # 10x plus rapide qu'avant
```

## ⚡ **Bénéfices Immédiats**

### Pour le Développement
- ✅ **Installation locale 10x plus rapide**
- ✅ **Cache intelligent partagé**
- ✅ **Résolution de conflits améliorée**

### Pour CI/CD
- ✅ **Builds Docker 5-10x plus rapides**
- ✅ **Tests GitHub Actions plus rapides**
- ✅ **Économies de coût Cloud Build**

### Pour l'Équipe
- ✅ **Moins d'attente sur les installations**
- ✅ **Feedback plus rapide sur les PR**
- ✅ **Expérience développeur améliorée**

## 🎉 **Résultat**

Avec **uv**, votre pipeline de développement devient :
- **10-100x plus rapide** pour les installations
- **Plus fiable** (meilleure résolution de dépendances)
- **Moins coûteux** (builds Cloud plus rapides)
- **Plus moderne** (compatible avec les standards Python récents)

**uv transforme littéralement votre expérience Python ! 🚀**