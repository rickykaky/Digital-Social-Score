"""
Toxicity Detection Model

Detects toxic content (insults, racism, harassment, hate speech)
and assigns a toxicity score from 0 to 100.
"""

from typing import Dict, List, Tuple
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
import numpy as np


class ToxicityClassifier:
    """
    Classifies text toxicity across multiple dimensions:
    - Toxicity (general)
    - Insults
    - Obscenity
    - Identity hate
    - Threats
    - Harassment
    """
    
    def __init__(
        self, 
        model_name: str = "facebook/roberta-hate-speech-dynabench-r4-target",
        device: str = None
    ):
        """
        Initialize the toxicity classifier.
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"Loading toxicity model '{model_name}' on device '{self.device}'...")
        
        try:
            # Load pre-trained model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline for easier inference
            self.classifier = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                top_k=None
            )
            
            print("Model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to a simpler, more reliable model
            print("Falling back to distilbert-base-uncased-finetuned-sst-2-english")
            self.tokenizer = AutoTokenizer.from_pretrained(
                "distilbert-base-uncased-finetuned-sst-2-english"
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "distilbert-base-uncased-finetuned-sst-2-english"
            )
            self.model.to(self.device)
            self.model.eval()
            self.classifier = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
        
        # Toxicity keywords for rule-based enhancement
        self.toxic_keywords = {
            "insults": ["idiot", "stupid", "moron", "dumb", "fool"],
            "hate_speech": ["hate", "racist", "bigot"],
            "threats": ["kill", "hurt", "attack", "threaten"],
            "harassment": ["stalk", "harass", "bully"],
            "obscenity": ["damn", "hell"]  # Mild examples only
        }
    
    def predict(self, text: str) -> Dict[str, float]:
        """
        Predict toxicity score for a given text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Dictionary with toxicity scores and details
        """
        if not text or not text.strip():
            return self._empty_prediction()
        
        try:
            # Get model prediction
            results = self.classifier(text[:512])  # Limit to 512 tokens
            
            # Process results based on model output
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], list):
                    # Multi-label classification
                    predictions = results[0]
                else:
                    # Single prediction
                    predictions = results
            else:
                predictions = results
            
            # Calculate toxicity score
            toxicity_score = self._calculate_toxicity_score(predictions, text)
            
            # Get detailed category scores
            category_scores = self._analyze_categories(text)
            
            # Combine scores
            final_score = self._combine_scores(toxicity_score, category_scores)
            
            return {
                "toxicity_score": round(final_score, 2),
                "is_toxic": final_score > 50.0,
                "confidence": self._calculate_confidence(predictions),
                "categories": category_scores,
                "severity": self._get_severity_level(final_score)
            }
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            # Fallback to rule-based scoring
            return self._fallback_prediction(text)
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Predict toxicity scores for multiple texts.
        
        Args:
            texts: List of text strings to analyze
        
        Returns:
            List of prediction dictionaries
        """
        return [self.predict(text) for text in texts]
    
    def _calculate_toxicity_score(self, predictions, text: str) -> float:
        """Calculate base toxicity score from model predictions."""
        if not predictions:
            return 0.0
        
        # Handle different prediction formats
        if isinstance(predictions, list):
            for pred in predictions:
                if isinstance(pred, dict):
                    label = pred.get("label", "").lower()
                    score = pred.get("score", 0.0)
                    
                    # Check for toxic/negative labels
                    if any(word in label for word in ["hate", "toxic", "negative", "offensive"]):
                        return score * 100
                    elif any(word in label for word in ["positive", "neutral", "nothate"]):
                        return (1 - score) * 100
        
        # Default: return moderate score if uncertain
        return 50.0
    
    def _analyze_categories(self, text: str) -> Dict[str, float]:
        """Analyze specific toxicity categories using keyword matching."""
        text_lower = text.lower()
        categories = {}
        
        for category, keywords in self.toxic_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 20.0  # Add 20 points per keyword match
            
            categories[category] = min(score, 100.0)  # Cap at 100
        
        return categories
    
    def _combine_scores(self, base_score: float, category_scores: Dict[str, float]) -> float:
        """Combine base score with category scores."""
        max_category_score = max(category_scores.values()) if category_scores else 0.0
        
        # Weight: 70% base score, 30% category score
        combined = (base_score * 0.7) + (max_category_score * 0.3)
        
        return min(combined, 100.0)  # Ensure score is between 0-100
    
    def _calculate_confidence(self, predictions) -> float:
        """Calculate confidence level of the prediction."""
        if not predictions:
            return 0.0
        
        if isinstance(predictions, list) and len(predictions) > 0:
            if isinstance(predictions[0], dict):
                return round(predictions[0].get("score", 0.0), 2)
        
        return 0.75  # Default confidence
    
    def _get_severity_level(self, score: float) -> str:
        """Map toxicity score to severity level."""
        if score < 20:
            return "none"
        elif score < 40:
            return "low"
        elif score < 60:
            return "medium"
        elif score < 80:
            return "high"
        else:
            return "critical"
    
    def _empty_prediction(self) -> Dict[str, float]:
        """Return prediction for empty text."""
        return {
            "toxicity_score": 0.0,
            "is_toxic": False,
            "confidence": 1.0,
            "categories": {},
            "severity": "none"
        }
    
    def _fallback_prediction(self, text: str) -> Dict[str, float]:
        """Fallback to rule-based prediction if model fails."""
        category_scores = self._analyze_categories(text)
        max_score = max(category_scores.values()) if category_scores else 0.0
        
        return {
            "toxicity_score": round(max_score, 2),
            "is_toxic": max_score > 50.0,
            "confidence": 0.5,
            "categories": category_scores,
            "severity": self._get_severity_level(max_score)
        }


# Global classifier instance (lazy loaded)
_classifier_instance = None


def get_classifier() -> ToxicityClassifier:
    """Get or create the global classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = ToxicityClassifier()
    return _classifier_instance


def analyze_toxicity(text: str) -> Dict[str, float]:
    """
    Convenience function to analyze text toxicity.
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary with toxicity analysis results
    """
    classifier = get_classifier()
    return classifier.predict(text)
