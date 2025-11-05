"""
Integration tests for the API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create client that properly handles lifespan
client = TestClient(app, raise_server_exceptions=True)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Digital Social Score API"
    assert data["status"] == "operational"


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data


def test_analyze_non_toxic_text():
    """Test analyzing non-toxic text."""
    response = client.post(
        "/analyze",
        json={"text": "Hello, how are you today? Have a great day!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "text_id" in data
    assert "score" in data
    assert 0 <= data["score"] <= 100
    assert "toxic" in data
    assert "categories" in data


def test_analyze_toxic_text():
    """Test analyzing potentially toxic text."""
    response = client.post(
        "/analyze",
        json={"text": "I hate this stupid thing"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "text_id" in data
    assert "score" in data
    assert 0 <= data["score"] <= 100
    assert "toxic" in data
    assert isinstance(data["toxic"], bool)
    assert "categories" in data


def test_analyze_empty_text():
    """Test that empty text is rejected."""
    response = client.post(
        "/analyze",
        json={"text": ""}
    )
    assert response.status_code == 422  # Validation error


def test_analyze_long_text():
    """Test analyzing very long text."""
    long_text = "This is a test. " * 1000  # 16,000 characters
    response = client.post(
        "/analyze",
        json={"text": long_text[:10000]}  # Within limit
    )
    assert response.status_code == 200


def test_gdpr_compliance_different_hashes():
    """Test that same text gets same hash (GDPR anonymization)."""
    text = "Test message for GDPR"
    
    response1 = client.post("/analyze", json={"text": text})
    response2 = client.post("/analyze", json={"text": text})
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Same text should produce same hash
    assert response1.json()["text_id"] == response2.json()["text_id"]


def test_metrics_endpoint():
    """Test the Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Check that it contains Prometheus metrics format
    assert "api_requests_total" in response.text or "# HELP" in response.text


def test_response_structure():
    """Test that response has all required fields."""
    response = client.post(
        "/analyze",
        json={"text": "Sample text for testing"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check all required fields
    assert "text_id" in data
    assert "score" in data
    assert "toxic" in data
    assert "categories" in data
    
    # Check types
    assert isinstance(data["text_id"], str)
    assert isinstance(data["score"], (int, float))
    assert isinstance(data["toxic"], bool)
    assert isinstance(data["categories"], dict)
