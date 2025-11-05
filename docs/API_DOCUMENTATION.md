# Digital Social Score API - Documentation

## Overview

The Digital Social Score API is a REST API that analyzes text for toxicity, providing scores from 0 (non-toxic) to 100 (highly toxic). It detects various forms of toxic content including insults, racism, harassment, and hate speech.

## Key Features

- **Toxicity Detection**: Analyzes text using advanced NLP models
- **Scoring System**: Returns numerical scores from 0-100
- **GDPR Compliant**: No personal data stored in clear text
- **Scalable**: Designed to handle from few to thousands of users
- **Observable**: Comprehensive logging, metrics, and health checks
- **Production-Ready**: Docker and Kubernetes deployment configurations

## API Endpoints

### 1. Root Endpoint

**GET /**

Returns basic API information.

**Response:**
```json
{
  "service": "Digital Social Score API",
  "version": "1.0.0",
  "status": "operational"
}
```

### 2. Health Check

**GET /health**

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 3. Text Analysis

**POST /analyze**

Analyzes text for toxicity.

**Request Body:**
```json
{
  "text": "Your text to analyze"
}
```

**Response:**
```json
{
  "text_id": "a7f3e9c2b1...",
  "score": 45.5,
  "toxic": false,
  "categories": {
    "insults": 0.0,
    "racism": 0.0,
    "harassment": 0.0,
    "hate_speech": 50.0
  }
}
```

**Fields:**
- `text_id`: Anonymized SHA-256 hash of the text (GDPR compliant)
- `score`: Overall toxicity score (0-100)
- `toxic`: Boolean indicating if text exceeds toxicity threshold (50)
- `categories`: Breakdown by toxicity type

**Constraints:**
- Text must be between 1 and 10,000 characters
- Text is not stored (GDPR compliance)

### 4. Metrics

**GET /metrics**

Returns Prometheus-formatted metrics for monitoring.

**Metrics Provided:**
- `api_requests_total`: Total number of API requests
- `api_request_duration_seconds`: Request duration histogram
- `toxicity_score`: Distribution of toxicity scores

## GDPR Compliance

### Data Protection Measures

1. **No Data Storage**: The API does not store analyzed text
2. **Anonymization**: Text is hashed using SHA-256 for identification
3. **No PII**: No personally identifiable information is retained
4. **Ephemeral Processing**: Text exists only during request processing

### Privacy Guarantees

- Original text is never logged or stored
- Only anonymized hashes are used for tracking
- No user identification or profiling
- Full compliance with GDPR Article 25 (Data Protection by Design)

## Scalability

### Horizontal Scaling

The API is designed to scale horizontally using:

- **Container Orchestration**: Kubernetes deployment
- **Auto-scaling**: HorizontalPodAutoscaler (HPA) configuration
- **Load Balancing**: Service load balancer distribution

### Performance Characteristics

- **Baseline**: 3 replicas for high availability
- **Maximum**: Scales up to 20 replicas under load
- **Resource Allocation**: 
  - Requests: 500m CPU, 512Mi memory
  - Limits: 2000m CPU, 2Gi memory

### Scaling Triggers

- CPU utilization > 70%
- Memory utilization > 80%
- Custom metrics based on request rate

## Observability

### Logging

Structured logging with:
- Request/response details
- Performance metrics
- Error tracking
- Anonymized text hashes

### Metrics

Prometheus metrics include:
- Request count by endpoint and status
- Request duration percentiles
- Toxicity score distribution
- System resource usage

### Alerts

Configured alerts for:
- High error rates (>5%)
- High latency (>2s at p95)
- Pod failures
- Abnormal toxicity patterns

## Deployment

### Docker

Build and run locally:
```bash
docker build -t toxicity-api:latest .
docker run -p 8000:8000 toxicity-api:latest
```

### Kubernetes

Deploy to Kubernetes:
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/hpa.yaml
kubectl apply -f kubernetes/monitoring.yaml
```

### Environment Variables

- `LOG_LEVEL`: Logging level (default: INFO)

## Security

### Best Practices Implemented

1. **Non-root User**: Container runs as non-root user
2. **Resource Limits**: Memory and CPU limits prevent abuse
3. **Health Checks**: Automatic restart of unhealthy pods
4. **Input Validation**: Strict validation of all inputs
5. **No Data Persistence**: Eliminates data breach risks

## Error Handling

### Error Codes

- `200`: Success
- `422`: Validation error (invalid input)
- `500`: Internal server error

### Error Response Format

```json
{
  "detail": "Error description"
}
```

## Usage Examples

### Python

```python
import requests

response = requests.post(
    "http://api-url/analyze",
    json={"text": "Your text here"}
)
result = response.json()
print(f"Toxicity Score: {result['score']}")
```

### cURL

```bash
curl -X POST http://api-url/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'
```

### JavaScript

```javascript
const response = await fetch('http://api-url/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Your text here' })
});
const result = await response.json();
console.log(`Toxicity Score: ${result.score}`);
```

## Performance

### Response Times

- Average: < 500ms
- P95: < 1s
- P99: < 2s

### Throughput

- Single instance: ~100 requests/second
- With auto-scaling: 2000+ requests/second

## Support

For issues or questions, please refer to the repository documentation.
