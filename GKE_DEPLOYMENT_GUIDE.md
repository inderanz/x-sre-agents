# GKE Deployment Guide for x-sre-agents

## Overview

This guide provides step-by-step instructions for deploying the x-sre-agents platform on Google Kubernetes Engine (GKE) with Langflow integration.

## Prerequisites

- Google Cloud Project with billing enabled
- gcloud CLI configured
- kubectl installed
- Helm 3.x installed

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub        │    │   GKE Cluster   │    │   Cloud SQL     │
│   Actions       │───▶│   (Kubernetes)  │───▶│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   (Memorystore) │
                       └─────────────────┘
```

## Step 1: Fix Docker Build Issues

The Docker build was failing due to `psycopg2` compilation issues. This has been fixed by:

1. **Updated requirements.txt**: Added `psycopg2-binary` instead of `psycopg2`
2. **Updated Dockerfile**: Added system dependencies for compilation

### Changes Made:
```dockerfile
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```

## Step 2: Set Up GKE Infrastructure

### Option A: Using Terraform (Recommended)

```bash
# Navigate to Terraform directory
cd terraform-gke

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply
```

### Option B: Using gcloud CLI

```bash
# Run the GKE setup script
./gke-setup.sh
```

## Step 3: Deploy Langflow on GKE

### Using the Deployment Script

```bash
# Deploy Langflow
./deploy-langflow-gke.sh
```

### Manual Deployment

```bash
# Get cluster credentials
gcloud container clusters get-credentials x-sre-agents-cluster \
  --project=arctic-moon-463710-t0 \
  --zone=us-central1-a

# Create namespace
kubectl create namespace x-sre-agents

# Deploy Langflow with Helm
helm install langflow langflow/langflow \
  --namespace x-sre-agents \
  --set image.tag=0.6.10 \
  --set service.type=LoadBalancer \
  --set ingress.enabled=true
```

## Step 4: Deploy x-sre-agents Platform

### Using GitHub Actions

The platform will automatically deploy when you push to the main branch. The workflow includes:

1. **Authentication**: Uses Workload Identity Federation
2. **Build**: Creates Docker image with fixed dependencies
3. **Deploy**: Deploys to GKE with proper configuration

### Manual Deployment

```bash
# Build and push image
docker build -t gcr.io/arctic-moon-463710-t0/x-sre-agents:latest .
docker push gcr.io/arctic-moon-463710-t0/x-sre-agents:latest

# Deploy to GKE
kubectl apply -f k8s/
```

## Step 5: Access Your Applications

### Langflow Access

```bash
# Port forward
kubectl port-forward -n x-sre-agents svc/langflow 7680:7680

# Or get LoadBalancer IP
kubectl get svc langflow -n x-sre-agents
```

### x-sre-agents Platform Access

```bash
# Port forward
kubectl port-forward -n x-sre-agents svc/x-sre-agents-service 8080:80

# Or get LoadBalancer IP
kubectl get svc x-sre-agents-service -n x-sre-agents
```

## Configuration

### Environment Variables

#### Langflow Configuration
```yaml
LANGFLOW_DATABASE_URL: "postgresql://langflow:password@db-host:5432/langflow"
LANGFLOW_CACHE_TYPE: "redis"
LANGFLOW_REDIS_URL: "redis://redis-host:6379/1"
LANGFLOW_SUPERUSER: "admin"
LANGFLOW_SUPERUSER_PASSWORD: "admin123"
```

#### x-sre-agents Configuration
```yaml
DATABASE_URL: "sqlite:///./x-sre-agents.db"
LOG_LEVEL: "info"
```

### Secrets Management

```bash
# Create secrets
kubectl create secret generic langflow-secrets \
  --namespace=x-sre-agents \
  --from-literal=OPENAI_API_KEY=your-api-key-here
```

## Monitoring and Logging

### View Logs

```bash
# Langflow logs
kubectl logs -n x-sre-agents deployment/langflow

# x-sre-agents logs
kubectl logs -n x-sre-agents deployment/x-sre-agents
```

### Monitor Resources

```bash
# Check pod status
kubectl get pods -n x-sre-agents

# Check services
kubectl get svc -n x-sre-agents

# Check ingress
kubectl get ingress -n x-sre-agents
```

## Scaling

### Horizontal Pod Autoscaling

```bash
# Check HPA status
kubectl get hpa -n x-sre-agents

# Scale manually
kubectl scale deployment x-sre-agents --replicas=5 -n x-sre-agents
```

### Cluster Autoscaling

The GKE cluster is configured with autoscaling:
- **Min nodes**: 1
- **Max nodes**: 10
- **Machine type**: e2-standard-4

## Security

### Workload Identity Federation

The deployment uses Workload Identity Federation for secure authentication:
- **Provider**: `projects/228332951437/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
- **Service Account**: `github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com`
- **Repository**: `inderanz/x-sre-agents`

### Network Policies

```bash
# Apply network policies
kubectl apply -f k8s/network-policies/
```

## Troubleshooting

### Common Issues

1. **Docker Build Fails**
   - Solution: Use `psycopg2-binary` instead of `psycopg2`
   - Add system dependencies in Dockerfile

2. **Authentication Errors**
   - Check Workload Identity Federation configuration
   - Verify repository name in attribute condition

3. **Pod Startup Issues**
   - Check resource limits
   - Verify environment variables
   - Check liveness/readiness probes

### Debug Commands

```bash
# Check pod events
kubectl describe pod <pod-name> -n x-sre-agents

# Check service endpoints
kubectl get endpoints -n x-sre-agents

# Check ingress status
kubectl describe ingress -n x-sre-agents
```

## Cost Optimization

### Resource Recommendations

- **Development**: e2-standard-2 (2 vCPU, 8 GB RAM)
- **Production**: e2-standard-4 (4 vCPU, 16 GB RAM)
- **Database**: db-f1-micro for development, db-n1-standard-1 for production

### Scaling Policies

- **CPU target**: 80%
- **Memory target**: 80%
- **Min replicas**: 1
- **Max replicas**: 5 (development), 10 (production)

## Next Steps

1. **Configure CI/CD**: Set up automated testing and deployment
2. **Add Monitoring**: Implement Prometheus and Grafana
3. **Set up Logging**: Configure Cloud Logging integration
4. **Security Hardening**: Implement network policies and RBAC
5. **Backup Strategy**: Set up automated backups for databases

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Check GKE cluster logs
4. Verify Workload Identity Federation configuration 