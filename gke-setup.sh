#!/bin/bash

# GKE Cluster Setup for x-sre-agents Langflow
set -e

# Configuration
PROJECT_ID="arctic-moon-463710-t0"
CLUSTER_NAME="x-sre-agents-cluster"
REGION="us-central1"
ZONE="us-central1-a"
NODE_COUNT=3
MACHINE_TYPE="e2-standard-4"

echo "🚀 Setting up GKE cluster for x-sre-agents..."

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Create GKE cluster
echo "🏗️ Creating GKE cluster..."
gcloud container clusters create $CLUSTER_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --num-nodes=$NODE_COUNT \
    --machine-type=$MACHINE_TYPE \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --enable-network-policy \
    --enable-ip-alias \
    --addons=HttpLoadBalancing,HorizontalPodAutoscaler \
    --workload-pool=$PROJECT_ID.svc.id.goog

# Get credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE

# Create namespace
echo "📁 Creating namespace..."
kubectl create namespace x-sre-agents --dry-run=client -o yaml | kubectl apply -f -

# Install Helm
echo "📦 Installing Helm..."
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Add Langflow Helm repository
echo "📚 Adding Langflow Helm repository..."
helm repo add langflow https://pixelstorecn.github.io/langflow-helm/
helm repo update

echo "✅ GKE cluster setup complete!"
echo "🌐 Cluster name: $CLUSTER_NAME"
echo "📍 Zone: $ZONE"
echo "🔧 Next steps:"
echo "   1. Deploy Langflow: ./deploy-langflow-gke.sh"
echo "   2. Access Langflow: kubectl port-forward -n x-sre-agents svc/langflow 7680:7680" 