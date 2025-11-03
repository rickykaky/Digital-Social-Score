# Digital Social Score API

> De l'analyse de texte à l'infrastructure Cloud sécurisée, scalable et conforme

## 🎯 Overview

Digital Social Score is a production-ready REST API that detects toxicity in text, providing comprehensive analysis with GDPR compliance, scalability, and full observability.

## ✨ Features

- **🔍 Toxicity Detection**: Analyzes text for insults, racism, harassment, and hate speech
- **📊 Numerical Scoring**: Returns scores from 0 (non-toxic) to 100 (highly toxic)
- **🔒 GDPR Compliant**: No personal data stored in clear text, SHA-256 anonymization
- **📈 Scalable**: Handles from few users to thousands with auto-scaling (3-20 pods)
- **👁️ Observable**: Comprehensive logging, Prometheus metrics, and alerts
- **☁️ Cloud-Ready**: Docker and Kubernetes deployment configurations
- **📚 Well-Documented**: Complete API documentation and architecture diagrams

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- Kubernetes cluster (for production deployment)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/rickykaky/Digital-Social-Score.git
cd Digital-Social-Score
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the API**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. **Access the API**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Docker Deployment

```bash
# Build the image
docker build -t toxicity-api:latest .

# Run the container
docker run -p 8000:8000 toxicity-api:latest
```

### Kubernetes Deployment

```bash
# Deploy the application
kubectl apply -f kubernetes/deployment.yaml

# Deploy auto-scaling
kubectl apply -f kubernetes/hpa.yaml

# Deploy monitoring
kubectl apply -f kubernetes/monitoring.yaml
```

## 📖 API Usage

### Analyze Text

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text to analyze"}'
```

**Response:**
```json
{
  "text_id": "a7f3e9c2b1d4f5e6...",
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

### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"text": "Hello, how are you?"}
)
result = response.json()
print(f"Toxicity Score: {result['score']}")
print(f"Is Toxic: {result['toxic']}")
```

## 🏗️ Architecture

### System Architecture

```
Internet → Load Balancer → Kubernetes Cluster → API Pods (3-20)
                                              ↓
                                      Monitoring Stack
                                (Prometheus + Grafana + Alerts)
```

### Components

- **FastAPI**: High-performance async web framework
- **Transformers**: NLP models for toxicity detection
- **Prometheus**: Metrics collection and alerting
- **Kubernetes**: Container orchestration and auto-scaling
- **Docker**: Application containerization

### Scalability

- **Horizontal Scaling**: Auto-scales from 3 to 20 pods based on CPU/memory
- **Load Balancing**: Kubernetes service distributes traffic
- **High Availability**: Multiple replicas ensure 99.9% uptime
- **Performance**: Handles 2000+ requests/second at scale

## 🔐 GDPR Compliance

### Data Protection

- ✅ **No data storage**: Text is never persisted
- ✅ **Anonymization**: SHA-256 hashing for identification
- ✅ **No PII**: Zero personally identifiable information retained
- ✅ **Ephemeral processing**: Data exists only during request
- ✅ **Encrypted transit**: TLS 1.3 for all communications

### Privacy by Design

All data handling follows GDPR Article 25 principles:
- Data minimization
- Purpose limitation
- Storage limitation
- Integrity and confidentiality

## 📊 Monitoring & Observability

### Metrics

Access Prometheus metrics at `/metrics`:

- `api_requests_total`: Total API requests by endpoint and status
- `api_request_duration_seconds`: Request latency histogram
- `toxicity_score`: Distribution of toxicity scores

### Alerts

Configured alerts for:
- High error rate (>5% for 5 minutes)
- High latency (>2s at p95)
- Pod failures
- Abnormal toxicity patterns

### Logging

Structured logs include:
- Request/response metadata
- Performance metrics
- Error tracking
- Anonymized text hashes (GDPR compliant)

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

- ✅ Unit tests for toxicity detector
- ✅ Unit tests for GDPR handler
- ✅ Integration tests for API endpoints
- ✅ Validation tests for scoring system

## 📚 Documentation

- [API Documentation](docs/API_DOCUMENTATION.md) - Complete API reference
- [Architecture Guide](docs/ARCHITECTURE.md) - Cloud architecture and design decisions
- [Interactive API Docs](http://localhost:8000/docs) - Swagger UI (when running)

## 🛠️ Development

### Project Structure

```
Digital-Social-Score/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── toxicity_detector.py # ML model integration
│   └── gdpr_handler.py      # GDPR compliance
├── tests/
│   ├── test_api.py          # API integration tests
│   ├── test_toxicity_detector.py
│   └── test_gdpr_handler.py
├── kubernetes/
│   ├── deployment.yaml      # K8s deployment config
│   ├── hpa.yaml            # Auto-scaling config
│   └── monitoring.yaml     # Monitoring config
├── docs/
│   ├── API_DOCUMENTATION.md
│   └── ARCHITECTURE.md
├── Dockerfile
├── requirements.txt
└── README.md
```

### Technologies Used

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **ML/NLP**: Transformers, PyTorch, DistilBERT
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Testing**: pytest, httpx

## 🔄 CI/CD

### Deployment Pipeline

1. **Build**: Create Docker image
2. **Test**: Run automated tests
3. **Push**: Upload to container registry
4. **Deploy**: Rolling update to Kubernetes
5. **Monitor**: Health checks and metrics validation

### Rolling Updates

- Zero-downtime deployments
- Automatic rollback on failure
- Health check validation before traffic routing

## 🌍 Cloud Providers

The application is cloud-agnostic and can be deployed on:

- **AWS**: EKS (Elastic Kubernetes Service)
- **Google Cloud**: GKE (Google Kubernetes Engine)
- **Azure**: AKS (Azure Kubernetes Service)
- **Other**: Any Kubernetes-compatible platform

## 📈 Performance

### Benchmarks

- **Latency**:
  - Average: < 500ms
  - P95: < 1s
  - P99: < 2s
- **Throughput**:
  - Single pod: ~100 req/s
  - Full cluster: 2000+ req/s

### Resource Requirements

Per pod:
- **CPU**: 500m (request), 2000m (limit)
- **Memory**: 512Mi (request), 2Gi (limit)

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Tests pass (`pytest tests/`)
- Code follows project style
- Documentation is updated
- GDPR compliance maintained

## 📄 License

This project is licensed under the MIT License.

## 🔍 Security

### Reporting Vulnerabilities

Please report security vulnerabilities privately to the repository maintainers.

### Security Features

- Non-root container execution
- Input validation and sanitization
- Resource limits to prevent DoS
- TLS encryption for all traffic
- Regular security updates

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Review the documentation
- Check the FAQ in the docs

## 🎓 Educational Purpose

This project demonstrates:
- Production-ready API development
- GDPR-compliant data handling
- Cloud-native architecture
- Kubernetes deployment and scaling
- Observability best practices
- Security-first design

---

**Built with ❤️ for secure, scalable, and compliant text analysis**
