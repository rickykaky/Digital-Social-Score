"""
Fixtures pytest partagées pour tous les tests
Fichier: tests/conftest.py
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock

import numpy as np
import pandas as pd
import pytest

# ============================================================================
# FIXTURES DONNÉES
# ============================================================================


@pytest.fixture
def sample_comments_df():
    """Fixture: DataFrame avec exemples de commentaires"""
    return pd.DataFrame(
        {
            "id": ["1", "2", "3", "4", "5"],
            "comment_text": [
                "This is a great product!",
                "I hate this, terrible service",
                "Awesome experience, highly recommend",
                "Worst purchase ever, never again",
                "Average, nothing special",
            ],
            "toxic": [0, 1, 0, 1, 0],
        }
    )


@pytest.fixture
def sample_pii_comments():
    """Fixture: Commentaires contenant des données personnelles"""
    return pd.DataFrame(
        {
            "comment_text": [
                "My name is John Smith and I live at 123 Main Street",
                "Call me at 555-1234 or email john@example.com",
                "My credit card is 1234-5678-9012-3456",
                "I was born on 15/03/1990",
            ]
        }
    )


@pytest.fixture
def sample_empty_comments():
    """Fixture: Commentaires vides ou invalides"""
    return pd.DataFrame({"comment_text": ["", "   ", None, "valid comment"]})


@pytest.fixture
def sample_large_comments():
    """Fixture: Commentaires de grande taille"""
    long_text = "A" * 5000 + " This is the end."
    return pd.DataFrame({"comment_text": [long_text] * 10, "toxic": [0] * 10})


# ============================================================================
# FIXTURES MODÈLE
# ============================================================================


@pytest.fixture
def mock_vectorizer():
    """Fixture: Vectoriseur mock (TF-IDF)"""
    mock = MagicMock()
    mock.get_feature_names_out.return_value = np.array(
        ["feature1", "feature2", "feature3"]
    )
    mock.transform.return_value = np.array([[0.5, 0.3, 0.2], [0.4, 0.4, 0.2]])
    return mock


@pytest.fixture
def mock_model():
    """Fixture: Modèle mock (LogisticRegression)"""
    mock = MagicMock()
    mock.predict.return_value = np.array([0, 1, 0])
    mock.predict_proba.return_value = np.array([[0.8, 0.2], [0.3, 0.7], [0.9, 0.1]])
    mock.score.return_value = 0.85
    return mock


@pytest.fixture
def model_artifacts(tmp_path):
    """Fixture: Répertoire avec artefacts du modèle"""
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression

    # Créer un petit modèle d'entraînement
    X_sample = np.random.rand(10, 5)
    y_sample = np.array([0, 1] * 5)

    model = LogisticRegression()
    model.fit(X_sample, y_sample)

    vectorizer = TfidfVectorizer()
    vectorizer.fit(["comment 1", "comment 2", "comment 3"])

    # Sauvegarder
    model_path = tmp_path / "model.joblib"
    vectorizer_path = tmp_path / "vectorizer.joblib"

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    return {
        "model_path": model_path,
        "vectorizer_path": vectorizer_path,
        "model": model,
        "vectorizer": vectorizer,
    }


# ============================================================================
# FIXTURES FICHIERS
# ============================================================================


@pytest.fixture
def temp_csv(tmp_path):
    """Fixture: Fichier CSV temporaire"""
    csv_path = tmp_path / "test_data.csv"
    df = pd.DataFrame({"comment_text": ["test 1", "test 2"], "toxic": [0, 1]})
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def temp_model_files(tmp_path):
    """Fixture: Répertoire temporaire pour modèles"""
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    return model_dir


# ============================================================================
# FIXTURES API
# ============================================================================


@pytest.fixture
def api_client():
    """Fixture: Client HTTP pour tester l'API"""
    from fastapi.testclient import TestClient

    from src.app import app

    return TestClient(app)


@pytest.fixture
def sample_api_payload():
    """Fixture: Payload standard pour API"""
    return {"text": "This is a test comment for the API."}


# ============================================================================
# FIXTURES CONFIGURATION
# ============================================================================


@pytest.fixture(autouse=True)
def reset_env():
    """Reset les variables d'environnement avant chaque test"""
    import os

    old_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def test_config():
    """Fixture: Configuration de test"""
    from src.config import TestingConfig

    return TestingConfig()


# ============================================================================
# FIXTURES LOGGING
# ============================================================================


@pytest.fixture
def caplog_setup(caplog):
    """Configure le logging pour les tests"""
    import logging

    caplog.set_level(logging.DEBUG)
    return caplog


# ============================================================================
# FIXTURES GCS (Mock)
# ============================================================================


@pytest.fixture
def mock_gcs_client():
    """Fixture: Client GCS mock"""
    mock = MagicMock()
    mock.bucket.return_value.blob.return_value.download_as_bytes.return_value = (
        b"mock data"
    )
    return mock


@pytest.fixture
def mock_vertex_ai():
    """Fixture: Vertex AI mock"""
    mock = MagicMock()
    mock.init.return_value = None
    mock.PipelineJob.return_value.submit.return_value = None
    return mock


# ============================================================================
# MARKERS (Marqueurs de catégories de tests)
# ============================================================================


def pytest_configure(config):
    """Enregistre les markers personnalisés"""
    config.addinivalue_line("markers", "unit: tests unitaires")
    config.addinivalue_line("markers", "integration: tests d'intégration")
    config.addinivalue_line("markers", "slow: tests lents")
    config.addinivalue_line("markers", "ml: tests machine learning")
    config.addinivalue_line("markers", "api: tests API")
    config.addinivalue_line("markers", "pipeline: tests pipeline")


# ============================================================================
# HOOKS PYTEST
# ============================================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook pour capturer les résultats des tests"""
    outcome = yield
    rep = outcome.get_result()

    # Loguer les tests échoués
    if rep.failed:
        print(f"\n❌ ÉCHEC: {item.name}")
    elif rep.passed:
        print(f"✅ SUCCÈS: {item.name}")
