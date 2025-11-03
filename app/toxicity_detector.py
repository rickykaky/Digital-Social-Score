"""
Toxicity detection module using transformer models.
Detects various types of toxic content: insults, racism, harassment, hate speech.
"""
import logging
from typing import Dict
from transformers import pipeline
import re

logger = logging.getLogger(__name__)


class ToxicityDetector:
    """
    Detects toxicity in text using a pre-trained transformer model.
    """
    
    # Threshold for considering text as toxic
    TOXICITY_THRESHOLD = 0.5
    
    # Keywords for different toxicity categories (multilingual support)
    CATEGORY_KEYWORDS = {
        'insults': [
            r'\b(idiot|stupid|dumb|moron|imbécile|con|crétin)\b',
        ],
        'racism': [
            r'\b(race|racial|racist|raciste|discrimination)\b',
        ],
        'harassment': [
            r'\b(harass|harcèlement|threat|menace|intimidat)\b',
        ],
        'hate_speech': [
            r'\b(hate|haine|kill|mort|violent)\b',
        ]
    }
    
    def __init__(self):
        """Initialize the toxicity detector with a pre-trained model."""
        logger.info("Loading toxicity detection model...")
        try:
            # Using a lightweight multilingual sentiment model as a proxy for toxicity
            # In production, use a dedicated toxicity model like unitary/toxic-bert
            self.classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                top_k=None
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def _detect_categories(self, text: str) -> Dict[str, float]:
        """
        Detect specific toxicity categories using keyword matching.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with category scores
        """
        text_lower = text.lower()
        categories = {}
        
        for category, patterns in self.CATEGORY_KEYWORDS.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score = 1.0
                    break
            categories[category] = score
        
        return categories
    
    def _calculate_base_toxicity(self, text: str) -> float:
        """
        Calculate base toxicity score using the classifier.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Toxicity score between 0 and 1
        """
        try:
            # Get sentiment prediction
            results = self.classifier(text[:512])[0]  # Limit text length
            
            # Convert sentiment to toxicity (negative sentiment = higher toxicity)
            for result in results:
                if result['label'] == 'NEGATIVE':
                    return result['score']
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in toxicity calculation: {e}")
            return 0.0
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze text for toxicity and return detailed results.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing:
                - score: Toxicity score (0-100)
                - toxic: Boolean indicating if text is toxic
                - categories: Dictionary of specific toxicity categories
        """
        # Calculate base toxicity
        base_toxicity = self._calculate_base_toxicity(text)
        
        # Detect specific categories
        categories = self._detect_categories(text)
        
        # Combine scores (weighted average)
        category_score = sum(categories.values()) / len(categories) if categories else 0
        combined_score = (base_toxicity * 0.6) + (category_score * 0.4)
        
        # Convert to 0-100 scale
        final_score = round(combined_score * 100, 2)
        
        # Determine if toxic
        is_toxic = final_score >= (self.TOXICITY_THRESHOLD * 100)
        
        return {
            'score': final_score,
            'toxic': is_toxic,
            'categories': {k: round(v * 100, 2) for k, v in categories.items()}
        }
