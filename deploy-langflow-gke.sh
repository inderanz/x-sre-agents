#!/bin/bash

# Deploy Langflow on GKE
set -e

# Configuration
PROJECT_ID="arctic-moon-463710-t0"
CLUSTER_NAME="x-sre-agents-cluster"
ZONE="us-central1-a"
NAMESPACE="x-sre-agents"

echo "🚀 Deploying Langflow on GKE..."

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE

# Create namespace if it doesn't exist
echo "📁 Ensuring namespace exists..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Create ConfigMap for Langflow configuration
echo "⚙️ Creating Langflow configuration..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: langflow-config
  namespace: $NAMESPACE
data:
  LANGFLOW_DATABASE_URL: "sqlite:///./langflow.db"
  LANGFLOW_AUTO_LOGIN: "true"
  LANGFLOW_CACHE_TYPE: "memory"
  LANGFLOW_SECRET_KEY: "your-secret-key-here"
  LANGFLOW_NEW_USER_IS_ACTIVE: "true"
  LANGFLOW_SUPERUSER: "admin"
  LANGFLOW_SUPERUSER_PASSWORD: "admin123"
  LANGFLOW_LOG_LEVEL: "info"
EOF

# Create Secret for sensitive data
echo "🔐 Creating secrets..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: langflow-secrets
  namespace: $NAMESPACE
type: Opaque
data:
  OPENAI_API_KEY: $(echo -n "your-openai-api-key-here" | base64)
EOF

# Deploy Langflow using Helm
echo "📦 Deploying Langflow with Helm..."
helm install langflow langflow/langflow \
    --namespace $NAMESPACE \
    --set image.tag=0.6.10 \
    --set configMap.name=langflow-config \
    --set secret.name=langflow-secrets \
    --set service.type=LoadBalancer \
    --set ingress.enabled=true \
    --set ingress.hosts[0].host=langflow.x-sre-agents.local \
    --set ingress.hosts[0].paths[0].path=/ \
    --set ingress.hosts[0].paths[0].pathType=Prefix \
    --set resources.requests.memory=512Mi \
    --set resources.requests.cpu=250m \
    --set resources.limits.memory=1Gi \
    --set resources.limits.cpu=500m \
    --set autoscaling.enabled=true \
    --set autoscaling.minReplicas=1 \
    --set autoscaling.maxReplicas=5 \
    --set autoscaling.targetCPUUtilizationPercentage=80

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/langflow -n $NAMESPACE

# Get service information
echo "🌐 Getting service information..."
kubectl get svc -n $NAMESPACE

echo "✅ Langflow deployment complete!"
echo "🔧 Access options:"
echo "   1. Port forward: kubectl port-forward -n $NAMESPACE svc/langflow 7680:7680"
echo "   2. LoadBalancer IP: kubectl get svc langflow -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
echo "   3. Ingress: kubectl get ingress -n $NAMESPACE"

# Show deployment status
echo "📊 Deployment status:"
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE 