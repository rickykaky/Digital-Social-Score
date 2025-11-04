"""
Data Anonymization Module for GDPR Compliance

This module implements Named Entity Recognition (NER) based anonymization
to protect personal data in text samples before processing.
"""

import hashlib
import re
from typing import Dict, List, Tuple
import spacy
from spacy.tokens import Doc


class TextAnonymizer:
    """
    Handles text anonymization using spaCy NER to detect and anonymize
    personal information (names, locations, organizations, dates, etc.)
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the anonymizer with a spaCy model.
        
        Args:
            model_name: Name of the spaCy model to use for NER
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # If model not found, provide instructions
            raise OSError(
                f"spaCy model '{model_name}' not found. "
                f"Please install it with: python -m spacy download {model_name}"
            )
        
        # Entity types to anonymize for GDPR compliance
        self.sensitive_entities = {
            "PERSON",      # Names of people
            "GPE",         # Geopolitical entities (cities, countries)
            "LOC",         # Non-GPE locations
            "ORG",         # Organizations
            "DATE",        # Dates
            "TIME",        # Times
            "EMAIL",       # Email addresses (custom)
            "PHONE",       # Phone numbers (custom)
        }
        
        # Regex patterns for additional PII detection
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b(?:\+?\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b')
        self.ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        
    def anonymize(self, text: str, method: str = "mask") -> Tuple[str, Dict]:
        """
        Anonymize personal information in the text.
        
        Args:
            text: Input text to anonymize
            method: Anonymization method - "mask", "pseudonymize", or "remove"
        
        Returns:
            Tuple of (anonymized_text, metadata_dict)
        """
        if not text or not text.strip():
            return text, {"entities_found": 0, "entities": []}
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Track entities found
        entities_found = []
        anonymized_text = text
        
        # First pass: Handle regex-detected PII
        anonymized_text, regex_entities = self._anonymize_regex_patterns(
            anonymized_text, method
        )
        entities_found.extend(regex_entities)
        
        # Second pass: Handle NER-detected entities
        # Process in reverse order to maintain string indices
        entities_to_process = [
            (ent.start_char, ent.end_char, ent.text, ent.label_)
            for ent in doc.ents
            if ent.label_ in self.sensitive_entities
        ]
        
        for start, end, entity_text, entity_type in reversed(entities_to_process):
            replacement = self._get_replacement(entity_text, entity_type, method)
            anonymized_text = (
                anonymized_text[:start] + replacement + anonymized_text[end:]
            )
            entities_found.append({
                "text": entity_text,
                "type": entity_type,
                "start": start,
                "end": end,
                "replacement": replacement
            })
        
        metadata = {
            "entities_found": len(entities_found),
            "entities": entities_found,
            "anonymization_method": method
        }
        
        return anonymized_text, metadata
    
    def _anonymize_regex_patterns(self, text: str, method: str) -> Tuple[str, List[Dict]]:
        """Anonymize PII detected by regex patterns."""
        entities = []
        
        # Email addresses
        for match in self.email_pattern.finditer(text):
            entities.append({
                "text": match.group(),
                "type": "EMAIL",
                "start": match.start(),
                "end": match.end(),
                "replacement": self._get_replacement(match.group(), "EMAIL", method)
            })
        
        # Phone numbers
        for match in self.phone_pattern.finditer(text):
            entities.append({
                "text": match.group(),
                "type": "PHONE",
                "start": match.start(),
                "end": match.end(),
                "replacement": self._get_replacement(match.group(), "PHONE", method)
            })
        
        # IP addresses
        for match in self.ip_pattern.finditer(text):
            entities.append({
                "text": match.group(),
                "type": "IP_ADDRESS",
                "start": match.start(),
                "end": match.end(),
                "replacement": self._get_replacement(match.group(), "IP_ADDRESS", method)
            })
        
        # Apply replacements in reverse order
        result_text = text
        for entity in reversed(entities):
            result_text = (
                result_text[:entity["start"]] + 
                entity["replacement"] + 
                result_text[entity["end"]:]
            )
        
        return result_text, entities
    
    def _get_replacement(self, entity_text: str, entity_type: str, method: str) -> str:
        """
        Generate replacement text based on anonymization method.
        
        Args:
            entity_text: Original entity text
            entity_type: Type of entity (PERSON, EMAIL, etc.)
            method: Anonymization method
        
        Returns:
            Replacement string
        """
        if method == "mask":
            return f"[{entity_type}]"
        elif method == "pseudonymize":
            # Create consistent pseudonym using hash
            hash_value = hashlib.sha256(entity_text.encode()).hexdigest()[:8]
            return f"[{entity_type}_{hash_value}]"
        elif method == "remove":
            return ""
        else:
            raise ValueError(f"Unknown anonymization method: {method}")
    
    def compare_texts(self, original: str, anonymized: str) -> Dict:
        """
        Compare original and anonymized texts and provide analysis.
        
        Args:
            original: Original text
            anonymized: Anonymized text
        
        Returns:
            Dictionary with comparison statistics
        """
        return {
            "original_length": len(original),
            "anonymized_length": len(anonymized),
            "characters_changed": sum(
                1 for a, b in zip(original, anonymized) if a != b
            ),
            "original_text": original,
            "anonymized_text": anonymized
        }


def anonymize_dataset(texts: List[str], method: str = "mask") -> Tuple[List[str], List[Dict]]:
    """
    Anonymize a list of texts.
    
    Args:
        texts: List of text strings to anonymize
        method: Anonymization method to use
    
    Returns:
        Tuple of (anonymized_texts, metadata_list)
    """
    anonymizer = TextAnonymizer()
    anonymized_texts = []
    metadata_list = []
    
    for text in texts:
        anon_text, metadata = anonymizer.anonymize(text, method)
        anonymized_texts.append(anon_text)
        metadata_list.append(metadata)
    
    return anonymized_texts, metadata_list
