# Workload Identity Federation Setup for x-sre-agents

## Overview
This document contains the complete setup for Workload Identity Federation (WIF) to enable secure authentication between GitHub Actions and Google Cloud Platform for the x-sre-agents project.

## Configuration Details

### Project Information
- **Project ID**: `arctic-moon-463710-t0`
- **Project Number**: `228332951437`
- **Region**: `us-central1`

### Workload Identity Pool
- **Pool Name**: `github-pool`
- **Pool Resource**: `projects/228332951437/locations/global/workloadIdentityPools/github-pool`
- **Display Name**: GitHub Actions Pool
- **State**: ACTIVE

### Workload Identity Provider
- **Provider Name**: `github-provider`
- **Provider Resource**: `projects/228332951437/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
- **Display Name**: GitHub provider
- **Issuer URI**: `https://token.actions.githubusercontent.com`
- **Attribute Mapping**: 
  - `google.subject=assertion.sub`
  - `attribute.actor=assertion.actor`
  - `attribute.repository=assertion.repository`
- **Attribute Condition**: `assertion.repository=='inderanz/x-sre-agents'`

### Service Account
- **Service Account Name**: `github-actions-sa`
- **Service Account Email**: `github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com`
- **Display Name**: GitHub Actions Service Account
- **Description**: Service account for GitHub Actions deployments

### IAM Roles Granted
The service account has been granted the following roles:
- `roles/iam.workloadIdentityUser` (bound to WIF pool)
- `roles/run.admin` (Cloud Run administration)
- `roles/iam.serviceAccountUser` (Service account usage)
- `roles/storage.admin` (Storage administration)

## GitHub Actions Configuration

### Required Permissions
```yaml
permissions:
  contents: 'read'
  id-token: 'write'
```

### Authentication Step
```yaml
- name: Google Auth
  id: auth
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/228332951437/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
    service_account: 'github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com'
```

## Commands Used for Setup

### 1. Create Workload Identity Pool
```bash
gcloud iam workload-identity-pools create "github-pool" \
  --project="arctic-moon-463710-t0" \
  --location="global" \
  --display-name="GitHub Actions Pool"
```

### 2. Create Workload Identity Provider
```bash
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="arctic-moon-463710-t0" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-condition="assertion.repository=='inderanz/x-sre-agents'"
```

### 3. Create Service Account
```bash
gcloud iam service-accounts create "github-actions-sa" \
  --project="arctic-moon-463710-t0" \
  --display-name="GitHub Actions Service Account" \
  --description="Service account for GitHub Actions deployments"
```

### 4. Bind Service Account to WIF Pool
```bash
gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com" \
  --project="arctic-moon-463710-t0" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/228332951437/locations/global/workloadIdentityPools/github-pool/attribute.repository/inderanz/x-sre-agents"
```

### 5. Grant Additional Roles
```bash
# Cloud Run Admin
gcloud projects add-iam-policy-binding "arctic-moon-463710-t0" \
  --member="serviceAccount:github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Service Account User
gcloud projects add-iam-policy-binding "arctic-moon-463710-t0" \
  --member="serviceAccount:github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Storage Admin
gcloud projects add-iam-policy-binding "arctic-moon-463710-t0" \
  --member="serviceAccount:github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

## Security Benefits

1. **No Long-lived Credentials**: No service account keys stored in GitHub secrets
2. **Repository-specific Access**: Only the specified repository can use this service account
3. **Automatic Token Rotation**: Tokens are automatically rotated by Google Cloud
4. **Audit Trail**: All authentication events are logged in Cloud Audit Logs
5. **Principle of Least Privilege**: Service account has only the minimum required permissions

## Troubleshooting

### Common Issues

1. **Attribute Condition Error**: Ensure the attribute condition references valid claims from the provider
2. **Permission Denied**: Verify the service account has the required roles
3. **Pool Not Found**: Check that the pool and provider names match exactly
4. **Repository Mismatch**: Ensure the repository name in the attribute condition matches your GitHub repository

### Verification Commands

```bash
# Check pool status
gcloud iam workload-identity-pools describe "github-pool" \
  --project="arctic-moon-463710-t0" \
  --location="global"

# Check provider status
gcloud iam workload-identity-pools providers describe "github-provider" \
  --project="arctic-moon-463710-t0" \
  --location="global" \
  --workload-identity-pool="github-pool"

# Check service account permissions
gcloud projects get-iam-policy "arctic-moon-463710-t0" \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com"
```

## Next Steps

1. Push this configuration to your GitHub repository
2. The GitHub Actions workflow will automatically use WIF for authentication
3. Monitor the deployment logs in GitHub Actions
4. Verify the service is accessible at the provided URL

## References

- [Workload Identity Federation Documentation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub Actions with WIF](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [Google Auth Action](https://github.com/google-github-actions/auth) 