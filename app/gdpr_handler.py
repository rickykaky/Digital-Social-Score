"""
GDPR compliance handler.
Ensures no personal data is stored in clear text.
"""
import hashlib
import logging

logger = logging.getLogger(__name__)


class GDPRHandler:
    """
    Handles GDPR-compliant data processing.
    Anonymizes text data to prevent storing personal information.
    """
    
    def __init__(self):
        """Initialize GDPR handler."""
        logger.info("GDPR handler initialized")
    
    def anonymize_text(self, text: str) -> str:
        """
        Anonymize text by creating a SHA-256 hash.
        This ensures GDPR compliance by not storing the original text.
        
        Args:
            text: Original text
            
        Returns:
            SHA-256 hash of the text (hexadecimal string)
        """
        # Create hash of text for anonymization
        text_bytes = text.encode('utf-8')
        hash_object = hashlib.sha256(text_bytes)
        return hash_object.hexdigest()
    
    def should_store_data(self) -> bool:
        """
        Determine if data should be stored.
        For GDPR compliance, we don't store any analyzed text.
        
        Returns:
            False - never store analyzed text
        """
        return False
