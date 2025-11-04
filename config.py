"""
Configuration settings for Digital Social Score API
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    
    # Model Settings
    TOXICITY_MODEL: str = os.getenv(
        "TOXICITY_MODEL",
        "facebook/roberta-hate-speech-dynabench-r4-target"
    )
    SPACY_MODEL: str = os.getenv("SPACY_MODEL", "en_core_web_sm")
    DEVICE: Optional[str] = os.getenv("DEVICE", None)  # None for auto-detect
    
    # GDPR Settings
    ANONYMIZE_BY_DEFAULT: bool = os.getenv("ANONYMIZE_BY_DEFAULT", "true").lower() == "true"
    DEFAULT_ANONYMIZATION_METHOD: str = os.getenv("DEFAULT_ANONYMIZATION_METHOD", "mask")
    
    # Data Settings
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR: str = os.path.join(DATA_DIR, "processed")
    ANONYMIZED_DATA_DIR: str = os.path.join(DATA_DIR, "anonymized")
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
    
    # Security Settings
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))


settings = Settings()
