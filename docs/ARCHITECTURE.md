# Cloud Architecture - Digital Social Score API

## Architecture Overview

This document describes the cloud architecture for the Digital Social Score API, designed for scalability, GDPR compliance, and high availability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INTERNET / CLIENT LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Client 1 │  │ Client 2 │  │ Client 3 │  │ Client N │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼─────────────┼─────────────┼─────────────┼────────────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER / INGRESS                            │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │  Kubernetes Ingress Controller / Cloud Load Balancer          │    │
│  │  • SSL/TLS Termination                                         │    │
│  │  • Request Distribution                                        │    │
│  │  • DDoS Protection                                             │    │
│  └───────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER (API LAYER)                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  Horizontal Pod Autoscaler (HPA)                                │  │
│  │  • Min Replicas: 3                                              │  │
│  │  • Max Replicas: 20                                             │  │
│  │  • Scaling based on CPU (70%) and Memory (80%)                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                        │                                                │
│  ┌─────────────────────┴───────────────────────┐                      │
│  │                                               │                      │
│  ▼                  ▼                  ▼        ▼                      │
│  ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐                       │
│  │ Pod 1 │   │ Pod 2 │   │ Pod 3 │   │ Pod N │                       │
│  ├───────┤   ├───────┤   ├───────┤   ├───────┤                       │
│  │FastAPI│   │FastAPI│   │FastAPI│   │FastAPI│                       │
│  │API    │   │API    │   │API    │   │API    │                       │
│  ├───────┤   ├───────┤   ├───────┤   ├───────┤                       │
│  │Toxity │   │Toxity │   │Toxity │   │Toxity │                       │
│  │Model  │   │Model  │   │Model  │   │Model  │                       │
│  ├───────┤   ├───────┤   ├───────┤   ├───────┤                       │
│  │GDPR   │   │GDPR   │   │GDPR   │   │GDPR   │                       │
│  │Handler│   │Handler│   │Handler│   │Handler│                       │
│  └───┬───┘   └───┬───┘   └───┬───┘   └───┬───┘                       │
│      │           │           │           │                             │
└──────┼───────────┼───────────┼───────────┼─────────────────────────────┘
       │           │           │           │
       └───────────┴───────────┴───────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MONITORING & OBSERVABILITY LAYER                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │   Prometheus     │  │   Grafana        │  │  AlertManager    │    │
│  │  • Metrics       │  │  • Dashboards    │  │  • Alerts        │    │
│  │  • Time Series   │  │  • Visualization │  │  • Notifications │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │   Logging Stack (ELK / Cloud Logging)                        │    │
│  │   • Centralized Logs                                          │    │
│  │   • Log Aggregation                                           │    │
│  │   • Search & Analysis                                         │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components Description

### 1. Client Layer

- **Purpose**: End users and applications accessing the API
- **Access**: HTTPS requests through public internet
- **Security**: TLS encryption, API authentication (if needed)

### 2. Load Balancer / Ingress

- **Type**: Kubernetes Ingress Controller or Cloud Load Balancer (AWS ALB, GCP LB, Azure LB)
- **Functions**:
  - SSL/TLS termination
  - Request routing
  - DDoS protection
  - Geographic distribution
- **Justification**: Distributes traffic across multiple pods for high availability

### 3. Kubernetes Cluster

#### API Pods

- **Container**: Docker image with FastAPI application
- **Components per Pod**:
  - FastAPI web server
  - Toxicity detection model
  - GDPR handler
- **Resources**:
  - Request: 500m CPU, 512Mi RAM
  - Limit: 2000m CPU, 2Gi RAM

#### Horizontal Pod Autoscaler (HPA)

- **Scaling Policy**:
  - Minimum: 3 replicas (high availability)
  - Maximum: 20 replicas (cost-effective scaling)
  - Triggers: CPU > 70%, Memory > 80%
- **Justification**: Automatically scales based on demand, handling traffic spikes

#### Service Discovery

- **Kubernetes Service**: Internal load balancing between pods
- **Health Checks**: Liveness and readiness probes ensure only healthy pods receive traffic

### 4. Monitoring & Observability

#### Prometheus

- **Purpose**: Metrics collection and storage
- **Metrics**:
  - Request rates and latencies
  - Error rates
  - Toxicity score distributions
  - Resource utilization

#### Grafana

- **Purpose**: Visualization and dashboards
- **Dashboards**:
  - Real-time API performance
  - Toxicity trends
  - System health

#### AlertManager

- **Purpose**: Alert routing and notification
- **Configured Alerts**:
  - High error rate (> 5%)
  - High latency (> 2s at p95)
  - Pod failures
  - Abnormal patterns

#### Logging

- **Solution**: Cloud-native logging (CloudWatch, Stackdriver) or ELK Stack
- **Purpose**: Centralized log aggregation and analysis
- **GDPR Note**: Logs contain only anonymized hashes, no PII

## Cloud Provider Options

### AWS Architecture

```
Internet Gateway
    ↓
Application Load Balancer (ALB)
    ↓
EKS Cluster (Kubernetes)
    ↓
- EC2 Auto Scaling Groups
- Fargate (serverless option)
    ↓
Monitoring: CloudWatch + Prometheus
Storage: S3 (for models)
```

### GCP Architecture

```
Cloud Load Balancing
    ↓
GKE Cluster (Kubernetes)
    ↓
- Compute Engine instances
- Cloud Run (serverless option)
    ↓
Monitoring: Cloud Monitoring + Prometheus
Storage: Cloud Storage (for models)
```

### Azure Architecture

```
Azure Load Balancer
    ↓
AKS Cluster (Kubernetes)
    ↓
- Virtual Machine Scale Sets
- Azure Container Instances
    ↓
Monitoring: Azure Monitor + Prometheus
Storage: Blob Storage (for models)
```

## Scalability Design

### Horizontal Scaling

- **Stateless Design**: No session state in pods
- **Load Distribution**: Kubernetes Service load balancing
- **Auto-scaling**: HPA based on metrics
- **Capacity**: From 3 to 20+ pods automatically

### Vertical Scaling

- **Resource Limits**: Configurable per pod
- **Model Optimization**: Lightweight transformer models
- **Caching**: Model loaded once per pod startup

### Performance Targets

- **Latency**: 
  - P50: < 300ms
  - P95: < 1s
  - P99: < 2s
- **Throughput**: 
  - Single pod: ~100 req/s
  - Cluster: 2000+ req/s (20 pods)
- **Availability**: 99.9% uptime

## GDPR Compliance Architecture

### Data Flow

1. **Request Reception**: Text received via HTTPS
2. **Anonymization**: Immediate SHA-256 hashing
3. **Processing**: Analysis using ML model
4. **Response**: Results with anonymized ID
5. **No Storage**: Text discarded after processing

### Privacy Guarantees

- **No Data Persistence**: Ephemeral processing only
- **No Logging of PII**: Only hashes logged
- **Encryption in Transit**: TLS 1.3
- **Right to Erasure**: Not applicable (no data stored)
- **Data Minimization**: Only necessary data processed

## Security Measures

### Application Security

- **Non-root Containers**: Least privilege principle
- **Input Validation**: Strict request validation
- **Rate Limiting**: Protection against abuse
- **Resource Limits**: Prevent resource exhaustion

### Network Security

- **TLS Encryption**: All traffic encrypted
- **Network Policies**: Kubernetes network isolation
- **Firewall Rules**: Cloud provider firewalls
- **DDoS Protection**: Cloud provider services

### Monitoring Security

- **Audit Logs**: All API access logged
- **Anomaly Detection**: Alert on unusual patterns
- **Security Scanning**: Container vulnerability scanning

## Disaster Recovery

### High Availability

- **Multi-Pod Deployment**: Minimum 3 replicas
- **Health Checks**: Automatic pod replacement
- **Load Balancing**: Traffic distribution
- **Rolling Updates**: Zero-downtime deployments

### Backup Strategy

- **Configuration**: GitOps for infrastructure as code
- **Models**: Stored in cloud object storage
- **Metrics**: Prometheus remote storage
- **Logs**: Retained in centralized logging

## Cost Optimization

### Efficient Resource Usage

- **Right-sizing**: Appropriate resource requests/limits
- **Auto-scaling**: Scale down during low traffic
- **Spot Instances**: Use for non-critical workloads
- **Model Optimization**: Lightweight models reduce compute

### Monitoring Costs

- **Metrics Retention**: 30 days default
- **Log Retention**: 90 days for compliance
- **Alert Optimization**: Reduce noise, focus on critical

## Deployment Strategy

### CI/CD Pipeline

1. **Build**: Docker image creation
2. **Test**: Automated testing
3. **Push**: Container registry
4. **Deploy**: Kubernetes rolling update
5. **Monitor**: Health checks and metrics

### Blue-Green Deployment

- **Zero Downtime**: Switch traffic between versions
- **Rollback**: Quick revert if issues detected
- **Testing**: Validate before full rollout

## Justification Summary

### Why Kubernetes?

- **Scalability**: Native horizontal pod autoscaling
- **Portability**: Cloud-agnostic deployment
- **Ecosystem**: Rich tooling for monitoring and management
- **Self-healing**: Automatic recovery from failures

### Why FastAPI?

- **Performance**: Async support for high concurrency
- **Documentation**: Auto-generated OpenAPI docs
- **Validation**: Built-in request/response validation
- **Modern**: Type hints and modern Python features

### Why Prometheus?

- **Industry Standard**: De facto for Kubernetes monitoring
- **Pull-based**: Efficient metric collection
- **Query Language**: Powerful PromQL for analysis
- **Integration**: Works seamlessly with Kubernetes

### Why Transformer Models?

- **Accuracy**: State-of-the-art NLP performance
- **Pre-trained**: Leverage existing models
- **Multilingual**: Support multiple languages
- **Flexible**: Easy to fine-tune for specific needs

## Future Enhancements

### Potential Improvements

1. **Custom ML Model**: Fine-tuned toxicity detection model
2. **Caching Layer**: Redis for frequently analyzed texts
3. **API Gateway**: Kong or AWS API Gateway for advanced features
4. **Multi-region**: Deploy across multiple regions for low latency
5. **Real-time Dashboard**: Live toxicity monitoring
6. **Feedback Loop**: Collect user feedback for model improvement

### Scalability Roadmap

- **Phase 1**: Current (3-20 pods)
- **Phase 2**: Multi-region deployment (20-50 pods per region)
- **Phase 3**: Global CDN integration (100+ pods)
- **Phase 4**: Serverless functions for extreme scale
