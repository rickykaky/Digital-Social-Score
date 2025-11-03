# Digital Social Score - Cloud Architecture

## Architecture Overview

The Digital Social Score API is designed as a scalable, GDPR-compliant microservice for text toxicity detection.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Applications                      │
│                    (Web, Mobile, Other Services)                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ HTTPS/REST API
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                      API Gateway / Load Balancer                 │
│                    (NGINX, AWS ALB, GCP Load Balancer)          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ Distribute requests
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                   Digital Social Score API                       │
│                        (FastAPI Service)                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  1. Request Validation (Pydantic)                      │    │
│  │  2. PII Anonymization (spaCy NER)                      │    │
│  │  3. Toxicity Detection (Transformers ML Model)         │    │
│  │  4. Score Calculation (0-100)                          │    │
│  │  5. Response Generation                                │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────┬────────────────────┬────────────────────────┘
                   │                    │
                   │                    │
      ┌────────────▼──────────┐    ┌───▼──────────────────┐
      │  Monitoring Service   │    │  Logging Service     │
      │  (Prometheus)         │    │  (ELK, CloudWatch)   │
      └───────────────────────┘    └──────────────────────┘
```

## Components

### 1. API Layer (FastAPI)
- **Purpose**: Handle HTTP requests, validation, routing
- **Technology**: FastAPI with Uvicorn
- **Scalability**: Horizontal scaling with multiple workers
- **Features**:
  - Request/response validation (Pydantic)
  - OpenAPI documentation (Swagger UI)
  - CORS support
  - Rate limiting (production)

### 2. Anonymization Module
- **Purpose**: GDPR compliance through PII removal
- **Technology**: spaCy NER (Named Entity Recognition)
- **Entities Detected**:
  - Personal names (PERSON)
  - Locations (GPE, LOC)
  - Organizations (ORG)
  - Dates/Times
  - Email addresses (regex)
  - Phone numbers (regex)
  - IP addresses (regex)
- **Methods**:
  - Masking: Replace with `[ENTITY_TYPE]`
  - Pseudonymization: Replace with hash-based identifier
  - Removal: Delete PII completely

### 3. Toxicity Detection Model
- **Purpose**: Detect and score toxic content
- **Technology**: Transformer-based model (RoBERTa/DistilBERT)
- **Model**: `facebook/roberta-hate-speech-dynabench-r4-target`
- **Fallback**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Categories Detected**:
  - General toxicity
  - Insults
  - Hate speech
  - Threats
  - Harassment
  - Obscenity

### 4. Monitoring & Observability
- **Metrics**: Prometheus-compatible metrics
  - Request count by endpoint
  - Request duration histogram
  - Toxicity score distribution
- **Logging**: Structured logging with timestamps
- **Health Checks**: `/health` endpoint for service monitoring

## Cloud Deployment Options

### Option 1: AWS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Route 53 (DNS)                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ CloudFront (CDN) + WAF (Security)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ Application Load Balancer (ALB)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ ECS/EKS Cluster (Container Orchestration)                   │
│  - Auto-scaling based on CPU/Memory/Request count           │
│  - Multiple availability zones                              │
│  - Health checks and auto-recovery                          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ CloudWatch (Monitoring & Logging)                           │
│ X-Ray (Distributed Tracing)                                 │
└─────────────────────────────────────────────────────────────┘
```

**AWS Services Used**:
- **ECS/EKS**: Container orchestration
- **ALB**: Load balancing
- **CloudWatch**: Logging and metrics
- **WAF**: Security and DDoS protection
- **Secrets Manager**: API keys and credentials
- **S3**: Model storage (optional)

### Option 2: Google Cloud Platform (GCP)

```
┌─────────────────────────────────────────────────────────────┐
│ Cloud DNS                                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ Cloud Load Balancing + Cloud Armor (Security)               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ Google Kubernetes Engine (GKE)                              │
│  - Auto-scaling with HPA                                    │
│  - Multi-zone deployment                                    │
│  - Workload identity for security                           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ Cloud Logging & Cloud Monitoring                            │
│ Cloud Trace (Distributed Tracing)                           │
└─────────────────────────────────────────────────────────────┘
```

**GCP Services Used**:
- **GKE**: Kubernetes orchestration
- **Cloud Load Balancing**: Load distribution
- **Cloud Logging/Monitoring**: Observability
- **Cloud Armor**: Security
- **Secret Manager**: Credentials management

### Option 3: Azure Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Azure DNS                                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ Application Gateway + Azure Front Door                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ Azure Kubernetes Service (AKS)                              │
│  - Cluster autoscaler                                       │
│  - Multiple node pools                                      │
│  - Azure AD integration                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ Azure Monitor + Application Insights                        │
└─────────────────────────────────────────────────────────────┘
```

**Azure Services Used**:
- **AKS**: Kubernetes orchestration
- **Application Gateway**: Load balancing
- **Azure Monitor**: Logging and metrics
- **Key Vault**: Secrets management
- **Azure Front Door**: CDN and security

## Scalability Strategy

### Horizontal Scaling
- **Container Orchestration**: Deploy multiple API instances
- **Auto-scaling Rules**:
  - Scale up: CPU > 70% or Request rate > 100 req/s
  - Scale down: CPU < 30% and Request rate < 20 req/s
- **Minimum Instances**: 2 (for high availability)
- **Maximum Instances**: 10-50 (based on budget and traffic)

### Vertical Scaling
- **CPU**: 2-4 vCPUs per instance
- **Memory**: 4-8 GB RAM per instance
- **GPU**: Optional for faster ML inference (production)

### Caching Strategy
- **Model Caching**: Load ML models once per instance
- **Result Caching**: Cache frequent queries (optional)
- **CDN**: Cache static content (documentation)

## Security Measures

### 1. Network Security
- HTTPS/TLS encryption
- API Gateway with rate limiting
- WAF for DDoS protection
- VPC isolation (cloud environments)

### 2. Data Security
- No persistent storage of user data
- PII anonymization before processing
- Encrypted secrets management
- Secure logging (no PII in logs)

### 3. Authentication & Authorization
- API key authentication (production)
- OAuth 2.0 support (optional)
- Role-based access control (RBAC)

### 4. GDPR Compliance
- Data minimization (only process text)
- PII anonymization
- No data retention
- Right to be forgotten (N/A - no storage)
- Data processing registry

## Monitoring & Alerting

### Metrics to Monitor
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Toxicity score distribution
- CPU and memory usage
- Container health

### Alerting Rules
- Error rate > 5% for 5 minutes
- Response time p95 > 2 seconds
- Service unavailable (health check failures)
- CPU usage > 80% for 10 minutes

## Cost Optimization

### Recommendations
1. Use spot/preemptible instances for non-critical workloads
2. Right-size containers based on actual usage
3. Implement request caching for repeated queries
4. Use CDN for static content
5. Scale down during off-peak hours
6. Use managed services to reduce operational overhead

## Disaster Recovery

### Backup Strategy
- Configuration as code (IaC)
- Model versioning and storage
- Multi-region deployment (optional)

### Recovery Procedures
- Automated health checks and restarts
- Blue-green deployments for zero-downtime updates
- Rollback capability to previous versions
- Multi-zone deployment for high availability

## Performance Benchmarks

### Expected Performance
- **Latency**: < 500ms (p95) for single text analysis
- **Throughput**: 100-1000 requests/second (depending on scale)
- **Availability**: 99.9% uptime (3 nines)

### Optimization Techniques
- Model quantization for faster inference
- Batch processing for multiple texts
- Async processing for non-blocking operations
- Connection pooling and keep-alive

## Future Enhancements

1. **ML Model Improvements**
   - Fine-tune on domain-specific data
   - Multi-language support
   - Real-time model updates

2. **Features**
   - User feedback loop for model improvement
   - Detailed toxicity explanations
   - Confidence thresholds customization

3. **Infrastructure**
   - Multi-region deployment
   - Edge computing for lower latency
   - Serverless options (AWS Lambda, Cloud Functions)

4. **Security**
   - Advanced threat detection
   - Anomaly detection
   - Enhanced audit logging
