import multiprocessing

# Le port par défaut de Cloud Run est 8080
bind = "0.0.0.0:8080"

# Définir le nombre de workers
# Nous utilisons 2 workers pour un vCPU pour optimiser l'utilisation.
workers = 2

# Type de worker (recommandé pour FastAPI)
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout pour les requêtes longues (utile pour les modèles ML)
timeout = 120

# Log de niveau et envoi à stdout/stderr pour Cloud Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
