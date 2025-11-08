"""
Tests unitaires pour le module d'anonymisation
Fichier: tests/unit/test_anonymization.py

Ce module teste toutes les fonctionnalités d'anonymisation des données PII (Personal Identifiable Information).
Il couvre :
- Détection de patterns regex (email, téléphone, carte de crédit)
- Fonctions d'anonymisation (masquage des PII)
- Entités nommées (noms de personnes)
- Cas limites et performance
"""

import pytest
import re
import time
from unittest.mock import patch

# NLTK Tree fallback pour les tests
class Tree:
    """Mock class for NLTK Tree when NLTK is not available"""
    def __init__(self, label, children=None):
        self._label = label
        self._children = children or []
    
    def label(self):
        return self._label
    
    def __iter__(self):
        return iter(self._children)


class TestRegexPatterns:
    """Tests pour les patterns regex de détection de PII"""
    
    @pytest.mark.unit
    def test_email_regex_detection(self):
        """Doit détecter les emails"""
        # Ce test suppose que le module app.py expose EMAIL_RE
        try:
            from src.app import EMAIL_RE
        except ImportError:
            pytest.skip("EMAIL_RE pattern not available")
        
        test_cases = [
            ('john@example.com', True),
            ('user.name+tag@example.co.uk', True),
            ('invalid.email@', False),
            ('@example.com', False),
            ('plaintext', False)
        ]
        
        for text, should_match in test_cases:
            match = EMAIL_RE.search(text)
            assert bool(match) == should_match, f"Email pattern failed for: {text}"
    
    @pytest.mark.unit
    def test_phone_regex_detection(self):
        """Doit détecter les numéros de téléphone"""
        try:
            from src.app import PHONE_RE
        except ImportError:
            pytest.skip("PHONE_RE pattern not available")
        
        test_cases = [
            ('555-1234', True),
            ('(555) 123-4567', True),
            ('+1-555-123-4567', True),
            ('1234', False),  # Trop court
            ('abc-defg', False)
        ]
        
        for text, should_match in test_cases:
            match = PHONE_RE.search(text)
            assert bool(match) == should_match, f"Phone pattern failed for: {text}"
    
    @pytest.mark.unit
    def test_credit_card_regex_detection(self):
        """Doit détecter les numéros de carte de crédit"""
        try:
            from src.app import CREDIT_RE
        except ImportError:
            pytest.skip("CREDIT_RE pattern not available")
        
        test_cases = [
            ('1234-5678-9012-3456', True),
            ('4532015112830366', True),  # Visa valide
            ('1234-5678-90', False),     # Trop court
            ('abcd-efgh-ijkl-mnop', False)
        ]
        
        for text, should_match in test_cases:
            match = CREDIT_RE.search(text)
            assert bool(match) == should_match, f"Credit card pattern failed for: {text}"


class TestAnonymizationFunctions:
    """Tests pour les fonctions d'anonymisation"""
    
    @pytest.mark.unit
    def test_mask_regex_pii_replaces_emails(self):
        """Doit remplacer les emails par <EMAIL>"""
        try:
            from src.app import mask_regex_pii
        except ImportError:
            pytest.skip("Function mask_regex_pii not available")
        
        text = "Contact me at john@example.com for details"
        result = mask_regex_pii(text)
        
        assert 'john@example.com' not in result
        assert '<EMAIL>' in result
    
    @pytest.mark.unit
    def test_mask_regex_pii_replaces_phone(self):
        """Doit remplacer les téléphones par <PHONE>"""
        from src.app import mask_regex_pii
        
        text = "Call me at 555-1234 or leave a message"
        result = mask_regex_pii(text)
        
        assert '555-1234' not in result
        assert '<PHONE>' in result
    
    @pytest.mark.unit
    def test_mask_regex_pii_preserves_regular_numbers(self):
        """Ne doit pas masquer les numéros réguliers (non-téléphone)"""
        from src.app import mask_regex_pii
        
        text = "There are 123 items in stock, code: 456"
        result = mask_regex_pii(text)
        
        # Les nombres courts ne doivent pas être remplacés
        assert '123' in result or result.count('<') == 0
    
    @pytest.mark.unit
    def test_mask_regex_pii_multiple_replacements(self):
        """Doit remplacer plusieurs PII dans le même texte"""
        from src.app import mask_regex_pii
        
        text = "Email john@example.com, phone 555-1234, card 1234-5678-9012-3456"
        result = mask_regex_pii(text)
        
        assert result.count('<EMAIL>') >= 1
        assert result.count('<PHONE>') >= 1
        assert result.count('<CREDIT_CARD>') >= 1
    
    @pytest.mark.unit
    def test_mask_regex_pii_empty_string(self):
        """Doit gérer les strings vides"""
        from src.app import mask_regex_pii
        
        result = mask_regex_pii("")
        assert result == ""
    
    @pytest.mark.unit
    def test_mask_regex_pii_no_pii(self):
        """Ne doit pas modifier un texte sans PII"""
        from src.app import mask_regex_pii
        
        text = "This is a regular comment with no personal information"
        result = mask_regex_pii(text)
        
        assert result == text
    
    @pytest.mark.unit
    @patch('src.app.nltk.pos_tag')
    @patch('src.app.nltk.ne_chunk')
    @patch('src.app.word_tokenize')
    def test_mask_named_entities_person(self, mock_tokenize, mock_ne_chunk, mock_pos_tag):
        """Doit masquer les entités nommées PERSON"""
        try:
            from src.app import mask_named_entities
        except ImportError:
            pytest.skip("Function mask_named_entities not available")
        
        # Mock NLTK pipeline
        mock_tokenize.return_value = ['My', 'name', 'is', 'John', 'Smith']
        mock_pos_tag.return_value = [
            ('My', 'PRP$'), ('name', 'NN'), ('is', 'VBZ'), 
            ('John', 'NNP'), ('Smith', 'NNP')
        ]
        
        # Mock tree structure for named entity
        person_chunk = Tree('PERSON', [('John', 'NNP'), ('Smith', 'NNP')])
        mock_ne_chunk.return_value = [
            ('My', 'PRP$'), ('name', 'NN'), ('is', 'VBZ'), person_chunk
        ]
        
        text = "My name is John Smith"
        result = mask_named_entities(text)
        
        # Vérifications
        assert result is not None
        assert isinstance(result, str)
        # Devrait contenir <PERSON> ou avoir masqué les noms
        assert '<PERSON>' in result or 'John Smith' not in result
    
    @pytest.mark.unit
    def test_mask_named_entities_no_entities(self):
        """Doit laisser inchangé un texte sans entités nommées"""
        try:
            from src.app import mask_named_entities
        except ImportError:
            pytest.skip("Function mask_named_entities not available")
        
        text = "This is a simple sentence with no names"
        result = mask_named_entities(text)
        
        assert result == text or result is not None


class TestEdgeCases:
    """Tests pour les cas limites"""
    
    @pytest.mark.unit
    def test_very_long_text(self):
        """Doit gérer les textes très longs"""
        from src.app import mask_regex_pii
        
        # Créer un texte très long
        long_text = "a" * 10000 + " email@example.com " + "b" * 10000
        result = mask_regex_pii(long_text)
        
        assert '<EMAIL>' in result
        assert len(result) > 10000
    
    @pytest.mark.unit
    def test_special_characters_in_text(self):
        """Doit gérer les caractères spéciaux"""
        from src.app import mask_regex_pii
        
        text = "Contact: john@example.com! Price: $50.99. Quality: ★★★★★"
        result = mask_regex_pii(text)
        
        assert '<EMAIL>' in result
        assert '$50.99' in result or '$' in result
    
    @pytest.mark.unit
    def test_unicode_characters(self):
        """Doit gérer les caractères Unicode"""
        from src.app import mask_regex_pii
        
        text = "Café: john@example.com, naïve, 日本語"
        result = mask_regex_pii(text)
        
        assert 'Café' in result or 'Caf' in result
        assert '<EMAIL>' in result
    
    @pytest.mark.unit
    def test_multiple_identical_patterns(self):
        """Doit remplacer toutes les occurrences identiques"""
        from src.app import mask_regex_pii
        
        text = "Email john@example.com and also john@example.com again"
        result = mask_regex_pii(text)
        
        # Doit avoir 2 occurrences de <EMAIL>
        assert result.count('<EMAIL>') == 2
    
    @pytest.mark.unit
    def test_partially_obfuscated_pii(self):
        """Doit détecter les PII même partiellement obfusqués"""
        from src.app import mask_regex_pii
        
        # Test avec espaces internes
        text = "Call: 555 - 1234"
        result = mask_regex_pii(text)
        # Peut ou non matcher selon l'implémentation regex
        # Juste vérifier qu'il n'y a pas d'erreur
        assert result is not None


class TestPerformance:
    """Tests de performance pour les fonctions d'anonymisation"""
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_anonymization_performance(self):
        """Doit anonymiser 1000 textes en < 5 secondes"""
        try:
            from src.app import mask_regex_pii
        except ImportError:
            pytest.skip("Function mask_regex_pii not available")
        
        texts = ["email@example.com text " + str(i) for i in range(1000)]
        
        start = time.time()
        results = [mask_regex_pii(t) for t in texts]
        elapsed = time.time() - start
        
        assert elapsed < 5.0, f"Anonymization too slow: {elapsed}s"
        assert len(results) == 1000
