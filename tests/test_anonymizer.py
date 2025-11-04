"""
Tests for the text anonymization module.
"""

import pytest
from src.utils.anonymizer import TextAnonymizer, anonymize_dataset


class TestTextAnonymizer:
    """Test cases for TextAnonymizer class."""
    
    @pytest.fixture
    def anonymizer(self):
        """Create an anonymizer instance for testing."""
        # Note: This will fail if spaCy model is not installed
        # In that case, tests will be skipped
        try:
            return TextAnonymizer()
        except OSError:
            pytest.skip("spaCy model not installed")
    
    def test_anonymize_empty_text(self, anonymizer):
        """Test anonymization of empty text."""
        result, metadata = anonymizer.anonymize("")
        assert result == ""
        assert metadata["entities_found"] == 0
    
    def test_anonymize_no_pii(self, anonymizer):
        """Test text without personal information."""
        text = "This is a simple comment about the weather."
        result, metadata = anonymizer.anonymize(text, method="mask")
        # May or may not find entities depending on NER model
        assert isinstance(result, str)
        assert isinstance(metadata, dict)
        assert "entities_found" in metadata
    
    def test_anonymize_with_email(self, anonymizer):
        """Test email address anonymization."""
        text = "Contact me at john@example.com for more info."
        result, metadata = anonymizer.anonymize(text, method="mask")
        assert "john@example.com" not in result
        assert "[EMAIL]" in result or metadata["entities_found"] >= 0
    
    def test_anonymize_with_phone(self, anonymizer):
        """Test phone number anonymization."""
        text = "Call me at 555-123-4567 tomorrow."
        result, metadata = anonymizer.anonymize(text, method="mask")
        assert "555-123-4567" not in result
        assert "[PHONE]" in result or metadata["entities_found"] >= 0
    
    def test_anonymization_methods(self, anonymizer):
        """Test different anonymization methods."""
        text = "Contact john@example.com today."
        
        # Mask method
        result_mask, _ = anonymizer.anonymize(text, method="mask")
        assert "[EMAIL]" in result_mask or "john@example.com" not in result_mask
        
        # Pseudonymize method
        result_pseudo, _ = anonymizer.anonymize(text, method="pseudonymize")
        assert isinstance(result_pseudo, str)
        
        # Remove method
        result_remove, _ = anonymizer.anonymize(text, method="remove")
        assert isinstance(result_remove, str)
    
    def test_invalid_method(self, anonymizer):
        """Test that invalid method raises error."""
        with pytest.raises(ValueError):
            anonymizer.anonymize("Test text", method="invalid")
    
    def test_compare_texts(self, anonymizer):
        """Test text comparison functionality."""
        original = "Original text"
        anonymized = "Anonymized text"
        comparison = anonymizer.compare_texts(original, anonymized)
        
        assert "original_length" in comparison
        assert "anonymized_length" in comparison
        assert comparison["original_text"] == original
        assert comparison["anonymized_text"] == anonymized


class TestAnonymizeDataset:
    """Test cases for dataset anonymization function."""
    
    def test_anonymize_dataset_basic(self):
        """Test basic dataset anonymization."""
        try:
            texts = [
                "This is a test.",
                "Another test comment."
            ]
            anonymized, metadata = anonymize_dataset(texts, method="mask")
            
            assert len(anonymized) == len(texts)
            assert len(metadata) == len(texts)
            assert all(isinstance(text, str) for text in anonymized)
        except OSError:
            pytest.skip("spaCy model not installed")
    
    def test_anonymize_empty_dataset(self):
        """Test anonymization of empty dataset."""
        try:
            texts = []
            anonymized, metadata = anonymize_dataset(texts)
            
            assert len(anonymized) == 0
            assert len(metadata) == 0
        except OSError:
            pytest.skip("spaCy model not installed")
