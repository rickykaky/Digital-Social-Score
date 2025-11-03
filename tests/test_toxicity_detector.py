"""
Unit tests for the toxicity detector module.
"""
import pytest
from app.toxicity_detector import ToxicityDetector


@pytest.fixture
def detector():
    """Create a toxicity detector instance."""
    return ToxicityDetector()


def test_detector_initialization(detector):
    """Test that detector initializes properly."""
    assert detector is not None
    assert detector.model_loaded is True


def test_analyze_returns_dict(detector):
    """Test that analyze returns proper structure."""
    result = detector.analyze("Test text")
    assert isinstance(result, dict)
    assert "score" in result
    assert "toxic" in result
    assert "categories" in result


def test_score_range(detector):
    """Test that score is within valid range."""
    result = detector.analyze("Hello world")
    assert 0 <= result["score"] <= 100


def test_toxic_boolean(detector):
    """Test that toxic field is boolean."""
    result = detector.analyze("Test message")
    assert isinstance(result["toxic"], bool)


def test_categories_structure(detector):
    """Test categories structure."""
    result = detector.analyze("Test message")
    assert isinstance(result["categories"], dict)
    
    expected_categories = ['insults', 'racism', 'harassment', 'hate_speech']
    for category in expected_categories:
        assert category in result["categories"]
        assert 0 <= result["categories"][category] <= 100


def test_detect_insult_keywords(detector):
    """Test detection of insult keywords."""
    result = detector.analyze("You are an idiot")
    # Should detect insult category
    assert result["categories"]["insults"] > 0


def test_detect_harassment_keywords(detector):
    """Test detection of harassment keywords."""
    result = detector.analyze("I will harass you")
    # Should detect harassment category
    assert result["categories"]["harassment"] > 0


def test_detect_hate_speech_keywords(detector):
    """Test detection of hate speech keywords."""
    result = detector.analyze("I hate this so much")
    # Should detect hate speech category
    assert result["categories"]["hate_speech"] > 0


def test_non_toxic_text_low_score(detector):
    """Test that clearly non-toxic text has low score."""
    result = detector.analyze("Have a wonderful day! Thank you for your help.")
    # Should have relatively low toxicity
    assert result["score"] < 70


def test_multilingual_support(detector):
    """Test French language support."""
    result = detector.analyze("Tu es un imbécile")
    # Should detect some toxicity
    assert result["categories"]["insults"] > 0
