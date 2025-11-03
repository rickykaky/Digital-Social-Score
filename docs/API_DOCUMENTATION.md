# Digital Social Score API - Documentation

## Overview

The Digital Social Score API is a GDPR-compliant REST API for detecting toxicity in text content. It assigns scores from 0 to 100 based on the level of toxicity detected.

## Base URL

```
http://localhost:8000  (Development)
https://api.digitalsocialscore.com  (Production)
```

## Authentication

Currently, the API is open for testing. Production deployment will require API key authentication.

```http
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### 1. Root Endpoint

Get API information.

**Endpoint:** `GET /`

**Response:**
```json
{
  "name": "Digital Social Score API",
  "version": "1.0.0",
  "description": "GDPR-compliant text toxicity detection API",
  "documentation": "/docs"
}
```

### 2. Health Check

Check API service health status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1699876543.21,
  "services": {
    "anonymizer": "ready",
    "classifier": "ready"
  }
}
```

**Status Values:**
- `healthy`: All services operational
- `degraded`: Some services unavailable

### 3. Analyze Single Text

Analyze a single text for toxicity.

**Endpoint:** `POST /analyze`

**Request Body:**
```json
{
  "text": "Your text content here",
  "anonymize": true,
  "anonymization_method": "mask"
}
```

**Parameters:**
- `text` (required): Text to analyze (1-5000 characters)
- `anonymize` (optional): Whether to anonymize PII (default: `true`)
- `anonymization_method` (optional): Method to use - `mask`, `pseudonymize`, or `remove` (default: `mask`)

**Response:**
```json
{
  "toxicity_score": 15.5,
  "is_toxic": false,
  "confidence": 0.92,
  "severity": "low",
  "categories": {
    "insults": 0.0,
    "hate_speech": 0.0,
    "threats": 0.0,
    "harassment": 0.0,
    "obscenity": 20.0
  },
  "anonymized": true,
  "processing_time_ms": 145.23
}
```

**Response Fields:**
- `toxicity_score`: Overall toxicity score (0-100)
- `is_toxic`: Boolean indicating if text is considered toxic (score > 50)
- `confidence`: Model confidence level (0-1)
- `severity`: Toxicity severity level
  - `none`: 0-20
  - `low`: 20-40
  - `medium`: 40-60
  - `high`: 60-80
  - `critical`: 80-100
- `categories`: Scores for specific toxicity types
- `anonymized`: Whether PII was anonymized
- `processing_time_ms`: Processing time in milliseconds

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test comment",
    "anonymize": true
  }'
```

**Example Request (Python):**
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "text": "This is a test comment",
        "anonymize": True
    }
)
print(response.json())
```

### 4. Batch Analysis

Analyze multiple texts in a single request.

**Endpoint:** `POST /analyze/batch`

**Request Body:**
```json
{
  "texts": [
    "First text to analyze",
    "Second text to analyze",
    "Third text to analyze"
  ],
  "anonymize": true,
  "anonymization_method": "mask"
}
```

**Parameters:**
- `texts` (required): Array of texts to analyze (1-100 texts)
- `anonymize` (optional): Whether to anonymize PII (default: `true`)
- `anonymization_method` (optional): Anonymization method (default: `mask`)

**Response:**
```json
{
  "results": [
    {
      "toxicity_score": 10.0,
      "is_toxic": false,
      "confidence": 0.95,
      "severity": "none",
      "categories": {...},
      "anonymized": true,
      "processing_time_ms": 120.5
    },
    {
      "toxicity_score": 75.0,
      "is_toxic": true,
      "confidence": 0.88,
      "severity": "high",
      "categories": {...},
      "anonymized": true,
      "processing_time_ms": 135.2
    }
  ],
  "count": 2,
  "total_processing_time_ms": 255.7
}
```

### 5. GDPR Compliance Information

Get information about GDPR compliance measures.

**Endpoint:** `GET /gdpr/compliance`

**Response:**
```json
{
  "compliant": true,
  "data_processing": {
    "personal_data_storage": "None - No personal data is stored",
    "anonymization": "PII is anonymized using NER before processing",
    "data_retention": "No data is retained after request processing",
    "user_rights": [...]
  },
  "security_measures": [...],
  "anonymization_methods": [...]
}
```

### 6. Metrics (Prometheus)

Get Prometheus-compatible metrics.

**Endpoint:** `GET /metrics`

**Response:** Prometheus text format
```
# HELP api_requests_total Total API requests
# TYPE api_requests_total counter
api_requests_total{endpoint="/analyze",method="POST",status="200"} 1543.0
...
```

## Anonymization Methods

### Masking
Replaces PII with entity type markers.

**Example:**
- Input: `"Contact John Smith at john@example.com"`
- Output: `"Contact [PERSON] at [EMAIL]"`

### Pseudonymization
Replaces PII with consistent hash-based identifiers.

**Example:**
- Input: `"Contact John Smith at john@example.com"`
- Output: `"Contact [PERSON_a3f5b8c2] at [EMAIL_7d9e4f1a]"`

### Removal
Completely removes PII from text.

**Example:**
- Input: `"Contact John Smith at john@example.com"`
- Output: `"Contact  at "`

## Error Responses

### 400 Bad Request
Invalid request parameters.

```json
{
  "detail": "Invalid request format"
}
```

### 422 Validation Error
Request validation failed.

```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
Server-side error.

```json
{
  "detail": "Error analyzing text: ..."
}
```

### 503 Service Unavailable
Service components not available.

```json
{
  "detail": "Toxicity classifier not available"
}
```

## Rate Limiting

Production API implements rate limiting:
- **Free tier**: 100 requests/minute
- **Standard tier**: 1000 requests/minute
- **Enterprise tier**: Custom limits

Rate limit headers included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699876643
```

## Best Practices

### 1. Enable Anonymization
Always enable anonymization for GDPR compliance:
```json
{
  "text": "Your text",
  "anonymize": true
}
```

### 2. Handle Errors Gracefully
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    print(f"API error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 3. Batch Processing
Use batch endpoint for multiple texts to reduce overhead:
```python
texts = ["text1", "text2", "text3"]
response = requests.post(
    f"{base_url}/analyze/batch",
    json={"texts": texts}
)
```

### 4. Monitor Response Times
Track `processing_time_ms` to identify performance issues.

### 5. Respect Rate Limits
Implement exponential backoff for rate limit errors.

## Integration Examples

### Python Integration

```python
import requests

class ToxicityDetector:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def analyze(self, text, anonymize=True):
        """Analyze single text for toxicity."""
        response = requests.post(
            f"{self.base_url}/analyze",
            json={
                "text": text,
                "anonymize": anonymize
            }
        )
        response.raise_for_status()
        return response.json()
    
    def is_toxic(self, text, threshold=50.0):
        """Check if text is toxic above threshold."""
        result = self.analyze(text)
        return result["toxicity_score"] > threshold

# Usage
detector = ToxicityDetector()
result = detector.analyze("Your text here")
print(f"Toxicity score: {result['toxicity_score']}")
```

### JavaScript Integration

```javascript
class ToxicityDetector {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async analyze(text, anonymize = true) {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        anonymize: anonymize
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  }
}

// Usage
const detector = new ToxicityDetector();
detector.analyze('Your text here')
  .then(result => {
    console.log(`Toxicity score: ${result.toxicity_score}`);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

## Swagger/OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

For issues, questions, or feature requests:
- GitHub Issues: [repository issues page]
- Email: support@digitalsocialscore.com
- Documentation: [docs website]
