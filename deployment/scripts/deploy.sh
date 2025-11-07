#!/bin/bash

################################################################################
# GKE Deployment Script for Social Score API
# 
# Usage:
#   ./deploy.sh [OPTIONS]
#
# Options:
#   -p, --project       GCP Project ID (required)
#   -c, --cluster       GKE Cluster name (required)
#   -z, --zone          Cluster zone (default: us-west1-a)
#   -r, --region        Artifact Registry region (default: us-west1)
#   -i, --image         Docker image name (default: social-score-api)
#   -t, --tag           Image tag (default: latest)
#   -n, --namespace     K8s namespace (default: default)
#   -d, --dry-run       Dry run mode (no actual deployment)
#   -h, --help          Show this help message
#
# Example:
#   ./deploy.sh -p my-project -c social-score-cluster -z us-west1-a
#
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_ID=""
CLUSTER_NAME=""
ZONE="us-west1-a"
REGION="us-west1"
IMAGE_NAME="social-score-api"
TAG="latest"
NAMESPACE="default"
DRY_RUN=false
VERBOSE=false

# Functions
print_help() {
    grep '^#' "$0" | sed 's/^#\s*//'
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--project)
            PROJECT_ID="$2"
            shift 2
            ;;
        -c|--cluster)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        -z|--zone)
            ZONE="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            ;;
    esac
done

# Validate required arguments
if [[ -z "$PROJECT_ID" ]]; then
    log_error "Project ID is required. Use -p or --project"
fi

if [[ -z "$CLUSTER_NAME" ]]; then
    log_error "Cluster name is required. Use -c or --cluster"
fi

# Set up environment
log_info "Setting up deployment environment..."
gcloud config set project "$PROJECT_ID"
gcloud container clusters get-credentials "$CLUSTER_NAME" --zone "$ZONE" --project "$PROJECT_ID"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/social-score-repo/${IMAGE_NAME}:${TAG}"

log_success "Configuration loaded:"
log_info "  Project ID: $PROJECT_ID"
log_info "  Cluster: $CLUSTER_NAME"
log_info "  Zone: $ZONE"
log_info "  Region: $REGION"
log_info "  Image: $IMAGE_URL"
log_info "  Namespace: $NAMESPACE"
log_info "  Dry Run: $DRY_RUN"

# Create namespace if it doesn't exist
if [[ "$NAMESPACE" != "default" ]]; then
    log_info "Creating namespace $NAMESPACE if it doesn't exist..."
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
fi

# Create service account if needed
log_info "Ensuring service account exists..."
kubectl create serviceaccount social-score-sa -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Update deployment image
log_info "Updating deployment image reference..."
DEPLOYMENT_FILE="deployment/k8s/social-score-deployment.yaml"

# Replace PROJECT_ID placeholder in deployment file
if [[ ! -f "$DEPLOYMENT_FILE" ]]; then
    log_error "Deployment file not found: $DEPLOYMENT_FILE"
fi

# Create temporary file with replaced values
TEMP_FILE=$(mktemp)
sed "s|PROJECT_ID|$PROJECT_ID|g" "$DEPLOYMENT_FILE" > "$TEMP_FILE"

# Apply Kubernetes manifests
log_info "Applying Kubernetes manifests..."

if [[ "$DRY_RUN" == true ]]; then
    log_warning "DRY RUN MODE - No changes will be applied"
    kubectl apply -f "$TEMP_FILE" --dry-run=client -o yaml
    kubectl apply -f "deployment/k8s/ingress.yaml" --dry-run=client -o yaml
else
    log_info "Applying deployment manifests..."
    kubectl apply -f "$TEMP_FILE"
    log_success "Deployment manifests applied"
    
    if [[ -f "deployment/k8s/ingress.yaml" ]]; then
        log_info "Applying ingress configuration..."
        kubectl apply -f "deployment/k8s/ingress.yaml"
        log_success "Ingress configuration applied"
    fi
fi

# Clean up temporary file
rm -f "$TEMP_FILE"

# Wait for rollout
if [[ "$DRY_RUN" == false ]]; then
    log_info "Waiting for deployment rollout..."
    
    if kubectl rollout status deployment/social-score-deployment -n "$NAMESPACE" --timeout=5m; then
        log_success "Deployment rollout completed successfully"
    else
        log_warning "Deployment rollout timed out or failed"
    fi
    
    # Get deployment status
    log_info "Deployment status:"
    kubectl get deployment -n "$NAMESPACE" -l app=social-score-api -o wide
    
    # Get pod status
    log_info "Pod status:"
    kubectl get pods -n "$NAMESPACE" -l app=social-score-api -o wide
    
    # Get service info
    log_info "Service information:"
    kubectl get service social-score-service -n "$NAMESPACE" -o wide
    
    # Get replica set info
    log_info "Replica set information:"
    kubectl get replicaset -n "$NAMESPACE" -l app=social-score-api -o wide
    
    # Show recent events
    log_info "Recent events:"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10
fi

log_success "Deployment script completed successfully!"

# Display next steps
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Verify pods are running: kubectl get pods -n $NAMESPACE"
echo "  2. Check pod logs: kubectl logs -n $NAMESPACE -l app=social-score-api -f"
echo "  3. Port forward to local machine:"
echo "     kubectl port-forward -n $NAMESPACE svc/social-score-service 8000:80"
echo "  4. Test the API: curl http://localhost:8000/health"
echo ""
