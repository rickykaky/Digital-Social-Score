"""Configuration de base pour le projet Digital Social Score"""

import os
import re
from enum import Enum
from pathlib import Path
from typing import List


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

        # Chemins du projet - Détection automatique du contexte
    @classmethod
    def _get_base_dir(cls) -> Path:
        """Détermine le répertoire de base selon le contexte d'exécution."""
        current_file = Path(__file__).resolve()
        
        # Si on est dans src/, le projet est au parent
        if current_file.parent.name == "src":
            base_dir = current_file.parent.parent
        else:
            # Fallback: chercher le dossier contenant src/
            base_dir = current_file.parent
            while base_dir.parent != base_dir:  # Pas la racine
                if (base_dir / "src").exists():
                    break
                base_dir = base_dir.parent
        
        return base_dir

    BASE_DIR = None  # Sera initialisé plus tard
    
    @classmethod
    def _init_paths(cls):
        """Initialise les chemins après la définition de la classe"""
        if cls.BASE_DIR is None:
            cls.BASE_DIR = cls._get_base_dir()
            cls.SRC_DIR = cls.BASE_DIR / "src"
            cls.DATA_DIR = cls.BASE_DIR / "data"
            cls.MODELS_DIR = cls.SRC_DIR / "models"  # Utiliser src/models pour cohérence
            cls.LOGS_DIR = cls.BASE_DIR / "logs"
            cls.TESTS_DIR = cls.BASE_DIR / "tests"


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
    PROJECT_ID = os.getenv("GCP_PROJECT_ID", "digital-social-score")
    GCS_PROJECT_ID = PROJECT_ID  # Alias pour compatibilité
    GCS_BUCKET_NAME = os.getenv(
        "GCS_BUCKET_NAME", f"{PROJECT_ID}-digital-social-score"
    )
    GCS_PIPELINE_BUCKET = os.getenv("GCS_PIPELINE_BUCKET", f"gs://{GCS_BUCKET_NAME}")

    # Vertex AI Configuration
    VERTEX_AI_PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID", PROJECT_ID)
    VERTEX_AI_REGION = os.getenv("VERTEX_AI_REGION", "us-west1")
    VERTEX_AI_PIPELINE_ROOT = os.getenv(
        "VERTEX_AI_PIPELINE_ROOT", f"gs://{PROJECT_ID}-ml-pipeline/pipeline-root"
    )

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

    # ============================================================================
    # PATTERNS REGEX POUR L'ANONYMISATION PII
    # ============================================================================

    # Email pattern - Détecte emails valides
    EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b", flags=re.IGNORECASE)

    # Phone pattern - Détecte numéros de téléphone internationaux
    PHONE_RE = re.compile(
        r"(?:\+?\d{1,3}[\s.-])?(?:\(?\d{2,4}\)?[\s.-])?[\d\s.-]{6,15}"
    )

    # Credit card pattern - Détecte numéros de carte de crédit
    CREDIT_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

    # Date pattern - Détecte différents formats de dates
    DATE_RE = re.compile(
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
        flags=re.IGNORECASE,
    )

    # Age pattern - Détecte mentions d'âge
    AGE_RE = re.compile(
        r"\b(?:age\s*[:]?\s*\d{1,3}|\d{1,3}\s?(?:years?\sold|yo|y/o|yrs|ans))\b",
        flags=re.IGNORECASE,
    )

    # Address pattern - Détecte adresses postales
    ADDRESS_RE = re.compile(
        r"\b\d{1,5}\s+(?:[\w\s]{1,60}?)\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Square|Sq)\b",
        flags=re.IGNORECASE,
    )

    # ============================================================================
    # CONFIGURATION DES DONNÉES
    # ============================================================================

    # Colonnes de toxicité disponibles dans le dataset
    TOXICITY_COLUMNS: List[str] = [
        "toxic",
        "severe_toxic",
        "obscene",
        "threat",
        "insult",
        "identity_hate",
    ]

    # Entités nommées à anonymiser
    NAMED_ENTITY_LABELS: List[str] = [
        "PERSON",
        "GPE",  # Geopolitical entities (countries, cities, states)
        "LOCATION",
        "ORGANIZATION",
    ]

    # Seuils de score social
    SCORE_THRESHOLDS = {
        "excellent": 80,  # Score >= 80: Excellent comportement
        "good": 60,  # Score >= 60: Bon comportement
        "average": 40,  # Score >= 40: Comportement moyen
        "poor": 20,  # Score >= 20: Comportement problématique
        "toxic": 0,  # Score < 20: Comportement toxique
    }

    # Configuration de l'API
    API_CONFIG = {
        "title": "Digital Social Score API",
        "description": "API pour la détection de toxicité et l'attribution d'un score social, conforme RGPD.",
        "version": "1.0.0",
        "default_port": 8080,
    }

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

    @classmethod
    def get_score_category(cls, score: int) -> str:
        """Retourne la catégorie d'un score social"""
        if score >= cls.SCORE_THRESHOLDS["excellent"]:
            return "excellent"
        elif score >= cls.SCORE_THRESHOLDS["good"]:
            return "good"
        elif score >= cls.SCORE_THRESHOLDS["average"]:
            return "average"
        elif score >= cls.SCORE_THRESHOLDS["poor"]:
            return "poor"
        else:
            return "toxic"

    @classmethod
    def get_available_toxicity_columns(cls, df_columns: List[str]) -> List[str]:
        """Retourne les colonnes de toxicité disponibles dans un DataFrame"""
        return [col for col in cls.TOXICITY_COLUMNS if col in df_columns]


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

    def __init__(self):
        super().__init__()
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
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


# Initialisation des chemins
Config._init_paths()

# Configuration active
config = get_config()
