#!/bin/bash
# Deploy Langflow to Google Cloud Run

PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
SERVICE_NAME=langflow
IMAGE=gcr.io/$PROJECT_ID/langflow:latest

# Build container image
gcloud builds submit --tag $IMAGE langflow/

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 7860

echo "Langflow deployed to Cloud Run." 