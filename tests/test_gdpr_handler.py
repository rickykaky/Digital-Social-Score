"""
Unit tests for GDPR handler.
"""
import pytest
from app.gdpr_handler import GDPRHandler


@pytest.fixture
def handler():
    """Create a GDPR handler instance."""
    return GDPRHandler()


def test_handler_initialization(handler):
    """Test that handler initializes properly."""
    assert handler is not None


def test_anonymize_text_returns_hash(handler):
    """Test that anonymize_text returns a hash."""
    text = "This is a test message"
    result = handler.anonymize_text(text)
    
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 produces 64 character hex string


def test_anonymize_same_text_same_hash(handler):
    """Test that same text produces same hash."""
    text = "Test message"
    hash1 = handler.anonymize_text(text)
    hash2 = handler.anonymize_text(text)
    
    assert hash1 == hash2


def test_anonymize_different_text_different_hash(handler):
    """Test that different texts produce different hashes."""
    text1 = "First message"
    text2 = "Second message"
    
    hash1 = handler.anonymize_text(text1)
    hash2 = handler.anonymize_text(text2)
    
    assert hash1 != hash2


def test_should_store_data_returns_false(handler):
    """Test that GDPR handler never allows storing data."""
    assert handler.should_store_data() is False


def test_anonymize_empty_string(handler):
    """Test anonymization of empty string."""
    result = handler.anonymize_text("")
    assert isinstance(result, str)
    assert len(result) == 64


def test_anonymize_unicode_text(handler):
    """Test anonymization with unicode characters."""
    text = "Hello 世界 🌍"
    result = handler.anonymize_text(text)
    assert isinstance(result, str)
    assert len(result) == 64


def test_anonymize_special_characters(handler):
    """Test anonymization with special characters."""
    text = "Test!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
    result = handler.anonymize_text(text)
    assert isinstance(result, str)
    assert len(result) == 64
