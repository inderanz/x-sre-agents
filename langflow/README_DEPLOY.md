# Langflow Helm Deployment Guide

This guide explains how to deploy Langflow on GKE using the local Helm chart under `langflow/helm`, with scalable folder structure and environment overlays for production, staging, and development. It also covers CloudSQL (Postgres) integration.

## Folder Structure

```
langflow/
  helm/                # Local Helm chart for Langflow
    templates/         # Helm templates
    values.yaml        # Default values
    Chart.yaml         # Chart metadata
    ...
  environments/
    production/
      values.yaml      # Production-specific overrides
    staging/
      values.yaml      # Staging-specific overrides
    development/
      values.yaml      # Dev/test overrides
```

## Environment Overlay Example

- **langflow/helm/values.yaml**: Base values (do not edit for env-specific config)
- **langflow/environments/production/values.yaml**: Production overrides (CloudSQL, Redis, Ingress, resources, secrets)
- **langflow/environments/staging/values.yaml**: Staging/test overrides
- **langflow/environments/development/values.yaml**: Local/dev overrides

## Example: Production values.yaml

```
configMap:
  LANGFLOW_DATABASE_URL: "postgresql://<USER>:<PASSWORD>@127.0.0.1:5432/<DB_NAME>"
  LANGFLOW_AUTO_LOGIN: "false"
  LANGFLOW_SUPERUSER: "admin"
  LANGFLOW_SUPERUSER_PASSWORD: "<superuser-password>"
  LANGFLOW_SECRET_KEY: "<random-secret-key>"
  LANGFLOW_NEW_USER_IS_ACTIVE: "false"
  LANGFLOW_CACHE_TYPE: "redis"
  LANGFLOW_REDIS_URL: "redis://:<redis-password>@<redis-service>:6379/1"
  LANGFLOW_LOG_LEVEL: "info"

image:
  tag: "latest"

INGRESS:
  ENABLE: true
  HOSTS:
    - HOST: "langflow.example.com"

resources:
  limits:
    cpu: "2"
    memory: "4Gi"
  requests:
    cpu: "500m"
    memory: "1Gi"
```

## CloudSQL Integration (Production)

- Deploy [CloudSQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-kubernetes-engine) as a sidecar or separate deployment.
- Set `LANGFLOW_DATABASE_URL` to use `127.0.0.1:5432` (proxy endpoint).
- Store DB credentials in GCP Secret Manager or as Kubernetes secrets.

## Deploying Langflow

1. **Set up your environment overlay:**
   - Edit `langflow/environments/production/values.yaml` with your secrets and endpoints.
2. **Deploy CloudSQL Proxy** (if using CloudSQL):
   - Use a Deployment or sidecar pattern.
3. **Install Langflow with Helm:**
   ```sh
   helm install langflow langflow/helm \
     -n langflow \
     -f langflow/environments/production/values.yaml
   ```
4. **Configure Ingress and DNS:**
   - Point your domain to the Ingress IP.
   - Use HTTPS (cert-manager or Google-managed certs).
5. **Monitor and Scale:**
   - Use GKE autoscaling, Cloud Operations, and best practices for security and resource management.

## Best Practices
- Use separate namespaces for each environment.
- Store all secrets in GCP Secret Manager or as Kubernetes secrets.
- Enable Workload Identity for secure GCP access.
- Use resource requests/limits for predictable scaling.
- Enable logging and monitoring with Google Cloud Operations Suite.

## References
- [Langflow Helm Chart (community)](https://github.com/pixelstorecn/langflow-helm)
- [Langflow Deployment Docs](https://docs.langflow.org/deployment-overview)
- [CloudSQL GKE Integration](https://cloud.google.com/sql/docs/postgres/connect-kubernetes-engine)
- [GKE Production Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices) 