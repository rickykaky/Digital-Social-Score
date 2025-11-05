# Deployment Guide - Digital Social Score API

## Quick Start

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/rickykaky/Digital-Social-Score.git
cd Digital-Social-Score

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Access the API
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health
# - Metrics: http://localhost:8000/metrics
```

### Docker Deployment

```bash
# Build the image
docker build -t toxicity-api:latest .

# Run the container
docker run -d -p 8000:8000 --name toxicity-api toxicity-api:latest

# Check logs
docker logs -f toxicity-api

# Test the API
curl http://localhost:8000/health
```

### Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (v1.20+)
- kubectl configured
- Container registry access (optional)

#### Steps

```bash
# 1. Build and push Docker image (if using registry)
docker build -t your-registry/toxicity-api:v1.0.0 .
docker push your-registry/toxicity-api:v1.0.0

# Update deployment.yaml with your image name

# 2. Deploy the application
kubectl apply -f kubernetes/deployment.yaml

# 3. Deploy auto-scaling
kubectl apply -f kubernetes/hpa.yaml

# 4. Deploy monitoring (if Prometheus is installed)
kubectl apply -f kubernetes/monitoring.yaml

# 5. Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# 6. Get the external IP
kubectl get service toxicity-api-service

# 7. Test the API
EXTERNAL_IP=$(kubectl get service toxicity-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$EXTERNAL_IP/health
```

## Cloud Provider Specific Deployment

### AWS (EKS)

```bash
# 1. Create EKS cluster
eksctl create cluster \
  --name toxicity-api-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 10

# 2. Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name toxicity-api-cluster

# 3. Push image to ECR
aws ecr create-repository --repository-name toxicity-api
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag toxicity-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/toxicity-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/toxicity-api:latest

# 4. Update deployment.yaml with ECR image URL and deploy
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/hpa.yaml

# 5. Install metrics server (required for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Google Cloud (GKE)

```bash
# 1. Create GKE cluster
gcloud container clusters create toxicity-api-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10

# 2. Get credentials
gcloud container clusters get-credentials toxicity-api-cluster --zone us-central1-a

# 3. Push image to GCR
gcloud auth configure-docker
docker tag toxicity-api:latest gcr.io/<project-id>/toxicity-api:latest
docker push gcr.io/<project-id>/toxicity-api:latest

# 4. Update deployment.yaml with GCR image URL and deploy
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/hpa.yaml
```

### Azure (AKS)

```bash
# 1. Create AKS cluster
az aks create \
  --resource-group toxicity-api-rg \
  --name toxicity-api-cluster \
  --node-count 3 \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 10 \
  --node-vm-size Standard_DS2_v2

# 2. Get credentials
az aks get-credentials --resource-group toxicity-api-rg --name toxicity-api-cluster

# 3. Create ACR and push image
az acr create --resource-group toxicity-api-rg --name toxicityapiregistry --sku Basic
az acr login --name toxicityapiregistry
docker tag toxicity-api:latest toxicityapiregistry.azurecr.io/toxicity-api:latest
docker push toxicityapiregistry.azurecr.io/toxicity-api:latest

# 4. Attach ACR to AKS
az aks update --name toxicity-api-cluster --resource-group toxicity-api-rg --attach-acr toxicityapiregistry

# 5. Update deployment.yaml with ACR image URL and deploy
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/hpa.yaml
```

## Monitoring Setup

### Install Prometheus and Grafana

```bash
# 1. Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 2. Install Prometheus
kubectl create namespace monitoring
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# 3. Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# 4. Login to Grafana
# Username: admin
# Password: (get from secret)
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# 5. Add dashboard for the API
# Import dashboard ID or create custom dashboard using metrics from /metrics endpoint
```

### Configure Alerts

```bash
# Apply alert configuration
kubectl apply -f kubernetes/monitoring.yaml

# Verify alerts
kubectl get servicemonitor -n monitoring
```

## Testing the Deployment

### Basic Health Check

```bash
# Get service URL
SERVICE_URL=$(kubectl get service toxicity-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health
curl http://$SERVICE_URL/health

# Expected response:
# {"status":"healthy","model_loaded":true}
```

### API Testing

```bash
# Test non-toxic text
curl -X POST http://$SERVICE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you today?"}'

# Test toxic text
curl -X POST http://$SERVICE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "You are an idiot!"}'

# Check metrics
curl http://$SERVICE_URL/metrics | grep api_requests_total
```

### Load Testing

```bash
# Install Apache Bench or use other load testing tools
# Test with 1000 requests, 10 concurrent
ab -n 1000 -c 10 -p test_payload.json -T application/json http://$SERVICE_URL/analyze

# Monitor auto-scaling
watch kubectl get hpa
watch kubectl get pods
```

## Configuration

### Environment Variables

The API supports the following environment variables:

- `LOG_LEVEL`: Logging level (default: INFO)
  - Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

Update `kubernetes/deployment.yaml` to add environment variables:

```yaml
env:
- name: LOG_LEVEL
  value: "INFO"
```

### Resource Tuning

Adjust resources in `kubernetes/deployment.yaml`:

```yaml
resources:
  requests:
    memory: "512Mi"  # Increase for better performance
    cpu: "500m"
  limits:
    memory: "2Gi"    # Adjust based on workload
    cpu: "2000m"
```

### Scaling Configuration

Adjust HPA in `kubernetes/hpa.yaml`:

```yaml
minReplicas: 3        # Minimum pods
maxReplicas: 20       # Maximum pods (increase for higher scale)
targetCPUUtilization: 70  # CPU threshold
targetMemoryUtilization: 80  # Memory threshold
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# - Image pull errors: Check image URL and registry access
# - Resource limits: Increase memory/CPU limits
# - Health check failures: Verify /health endpoint works
```

### High Latency

```bash
# Check pod resources
kubectl top pods

# Check HPA status
kubectl get hpa

# Solutions:
# - Scale up replicas
# - Increase resource limits
# - Optimize detection algorithm
```

### Metrics Not Showing

```bash
# Verify metrics endpoint
kubectl port-forward <pod-name> 8000:8000
curl http://localhost:8000/metrics

# Check ServiceMonitor
kubectl get servicemonitor
kubectl describe servicemonitor toxicity-api-monitor

# Verify Prometheus can scrape
kubectl logs -n monitoring <prometheus-pod-name>
```

## Security Considerations

### Production Checklist

- [ ] Enable TLS/SSL for external access
- [ ] Configure network policies
- [ ] Set up authentication/authorization (API keys, OAuth)
- [ ] Enable audit logging
- [ ] Configure resource quotas
- [ ] Set up backup and disaster recovery
- [ ] Enable pod security policies
- [ ] Configure RBAC properly
- [ ] Use secrets for sensitive data
- [ ] Regular security updates

### Enable TLS

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Create certificate issuer and certificate
# Update ingress to use TLS
```

## Maintenance

### Updates and Rollbacks

```bash
# Update deployment with new image
kubectl set image deployment/toxicity-api api=toxicity-api:v1.1.0

# Check rollout status
kubectl rollout status deployment/toxicity-api

# Rollback if needed
kubectl rollout undo deployment/toxicity-api

# View rollout history
kubectl rollout history deployment/toxicity-api
```

### Backup and Restore

```bash
# Backup Kubernetes manifests
kubectl get all -o yaml > backup.yaml

# Version control all YAML files in git
git add kubernetes/
git commit -m "Update deployment configuration"
git push
```

## Cost Optimization

### Recommendations

1. **Right-size resources**: Monitor actual usage and adjust
2. **Use spot instances**: For non-critical workloads
3. **Scale down during low traffic**: Configure HPA min replicas
4. **Use cluster autoscaler**: Scale nodes based on demand
5. **Monitor costs**: Use cloud provider cost management tools

## Support

For issues or questions:
- Check logs: `kubectl logs <pod-name>`
- Review documentation: See README.md and API_DOCUMENTATION.md
- Create GitHub issue with details

## Next Steps

1. Set up CI/CD pipeline for automated deployments
2. Configure monitoring alerts and dashboards
3. Implement API authentication
4. Add rate limiting
5. Set up multi-region deployment for disaster recovery
