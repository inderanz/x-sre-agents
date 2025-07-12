# Langflow on Cloud Run

## Deployment

1. Ensure you have Google Cloud SDK and billing enabled.
2. Set your project and region:
   ```sh
   gcloud config set project YOUR_PROJECT_ID
   gcloud config set run/region YOUR_REGION
   ```
3. Build and deploy Langflow:
   ```sh
   bash deploy_langflow_cloudrun.sh
   ```
4. Access Langflow via the Cloud Run service URL.

## Integration
- Use the Langflow UI to visually orchestrate agent workflows.
- Reference `docs/langflow/mindops_flow.json` for the recommended flow.
- Connect Langflow nodes to your deployed agent endpoints as needed. 