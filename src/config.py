"""Configuration de base pour le projet Digital Social Score"""

import os
from pathlib import Path
from enum import Enum


class Environment(str, Enum):
    """Environnements supportés"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Config:
    """Configuration de base - commune à tous les environnements"""
    
    # Informations du projet
    PROJECT_NAME = "digital-social-score"
    VERSION = "1.0.0"
    DESCRIPTION = "API de détection de toxicité et score social conforme RGPD"
    
    # Chemins
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    SRC_DIR = BASE_DIR / "src"
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    TESTS_DIR = BASE_DIR / "tests"
    
    # Environnement
    ENV = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    
    # Model Configuration
    MODEL_TYPE = "logistic_regression"
    VECTORIZER_TYPE = "tfidf"
    MAX_FEATURES = 5000
    MIN_DF = 5
    MAX_DF = 0.8
    
    # NLP Configuration
    ENABLE_ANONYMIZATION = True
    ENABLE_LEMMATIZATION = True
    ENABLE_STOPWORDS_REMOVAL = True
    
    # GCS Configuration
    GCS_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", f"{GCS_PROJECT_ID}-digital-social-score")
    GCS_PIPELINE_BUCKET = os.getenv("GCS_PIPELINE_BUCKET", f"gs://{GCS_BUCKET_NAME}")
    
    # Vertex AI Configuration
    VERTEX_AI_REGION = os.getenv("VERTEX_AI_REGION", "us-central1")
    VERTEX_AI_PIPELINE_ROOT = f"gs://{GCS_BUCKET_NAME}/pipeline-root"
    
    # Database Configuration (optionnel)
    DATABASE_URL = os.getenv("DATABASE_URL", None)
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security
    ENABLE_CORS = True
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Feature Flags
    USE_CACHE = True
    CACHE_TTL = 3600  # 1 heure
    
    # Performance
    MAX_TEXT_LENGTH = 10000
    REQUEST_TIMEOUT = 30
    
    @classmethod
    def get_model_path(cls) -> Path:
        """Retourne le chemin du modèle"""
        return cls.MODELS_DIR / "model.joblib"
    
    @classmethod
    def get_vectorizer_path(cls) -> Path:
        """Retourne le chemin du vectoriseur"""
        return cls.MODELS_DIR / "vectorizer.joblib"
    
    @classmethod
    def get_log_file(cls, name: str = "app.log") -> Path:
        """Retourne le chemin d'un fichier log"""
        cls.LOGS_DIR.mkdir(exist_ok=True, parents=True)
        return cls.LOGS_DIR / name


class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    USE_CACHE = False


class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ENABLE_CORS = False
    SECRET_KEY = os.getenv("SECRET_KEY")  # DOIT être défini
    
    if not SECRET_KEY:
        raise ValueError("❌ SECRET_KEY doit être défini en production")


class TestingConfig(Config):
    """Configuration pour les tests"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = "sqlite:///:memory:"
    USE_CACHE = False
    ENABLE_CORS = True
    CORS_ORIGINS = ["*"]


def get_config(env: str = None) -> Config:
    """Factory pour obtenir la bonne configuration"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        Environment.DEVELOPMENT.value: DevelopmentConfig,
        Environment.PRODUCTION.value: ProductionConfig,
        Environment.TESTING.value: TestingConfig,
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    return config_class()


# Configuration active
config = get_config()
