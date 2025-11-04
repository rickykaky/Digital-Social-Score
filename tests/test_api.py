"""
Tests for the API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


client = TestClient(app)


class TestRootEndpoints:
    """Test basic API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "Digital Social Score API"
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert data["status"] in ["healthy", "degraded"]


class TestGDPREndpoints:
    """Test GDPR compliance endpoints."""
    
    def test_gdpr_compliance_endpoint(self):
        """Test GDPR compliance information endpoint."""
        response = client.get("/gdpr/compliance")
        assert response.status_code == 200
        data = response.json()
        assert data["compliant"] is True
        assert "data_processing" in data
        assert "security_measures" in data
        assert "anonymization_methods" in data


class TestAnalysisEndpoints:
    """Test text analysis endpoints."""
    
    def test_analyze_simple_text(self):
        """Test analyzing a simple non-toxic text."""
        payload = {
            "text": "This is a nice day.",
            "anonymize": False
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "toxicity_score" in data
        assert "is_toxic" in data
        assert "confidence" in data
        assert "severity" in data
        assert "categories" in data
        assert 0 <= data["toxicity_score"] <= 100
    
    def test_analyze_with_anonymization(self):
        """Test analysis with anonymization enabled."""
        payload = {
            "text": "Contact john@example.com for details.",
            "anonymize": True,
            "anonymization_method": "mask"
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["anonymized"] is True
        assert "toxicity_score" in data
    
    def test_analyze_empty_text(self):
        """Test that empty text is rejected."""
        payload = {
            "text": "",
            "anonymize": False
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_invalid_method(self):
        """Test that invalid anonymization method is rejected."""
        payload = {
            "text": "Test text",
            "anonymize": True,
            "anonymization_method": "invalid_method"
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_batch_analysis(self):
        """Test batch text analysis."""
        payload = {
            "texts": [
                "This is good.",
                "This is bad."
            ],
            "anonymize": False
        }
        response = client.post("/analyze/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["results"]) == 2
    
    def test_batch_analysis_empty(self):
        """Test that empty batch is rejected."""
        payload = {
            "texts": [],
            "anonymize": False
        }
        response = client.post("/analyze/batch", json=payload)
        assert response.status_code == 422  # Validation error


class TestMetricsEndpoint:
    """Test metrics endpoint."""
    
    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Metrics should be in Prometheus format
        assert "api_requests_total" in response.text or response.text != ""
