# Workload Identity Federation Repository Name Fix

## Issue Resolved

The GitHub Actions workflow was failing with the error:
```
google-github-actions/auth failed with: failed to generate Google Cloud federated token for //iam.googleapis.com/projects/228332951437/locations/global/workloadIdentityPools/github-pool/providers/github-provider: {"error":"unauthorized_client","error_description":"The given credential is rejected by the attribute condition."}
```

## Root Cause

The Workload Identity Federation provider was configured with the wrong repository name in the attribute condition:

- **Configured**: `harshvardhan/x-sre-agents`
- **Actual**: `inderanz/x-sre-agents`

The attribute condition was rejecting the GitHub Actions credentials because the repository name didn't match exactly.

## Solution Applied

### 1. Updated Workload Identity Provider
Changed the attribute condition to match the correct repository name:

```bash
gcloud iam workload-identity-pools providers update-oidc "github-provider" \
  --project="arctic-moon-463710-t0" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --attribute-condition="assertion.repository=='inderanz/x-sre-agents'"
```

### 2. Updated Service Account Binding
Removed the old binding and added the correct one:

```bash
# Remove old binding
gcloud iam service-accounts remove-iam-policy-binding "github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com" \
  --project="arctic-moon-463710-t0" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/228332951437/locations/global/workloadIdentityPools/github-pool/attribute.repository/harshvardhan/x-sre-agents"

# Add correct binding
gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com" \
  --project="arctic-moon-463710-t0" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/228332951437/locations/global/workloadIdentityPools/github-pool/attribute.repository/inderanz/x-sre-agents"
```

### 3. Updated Documentation
Updated `WIF_SETUP.md` to reflect the correct repository name in all examples and commands.

## Verification

The updated configuration now shows:

```bash
# Attribute condition
assertion.repository=='inderanz/x-sre-agents'

# Service account binding
principalSet://iam.googleapis.com/projects/228332951437/locations/global/workloadIdentityPools/github-pool/attribute.repository/inderanz/x-sre-agents
```

## Current Configuration Status

### ✅ Workload Identity Pool
- **Name**: `github-pool`
- **Status**: ACTIVE
- **Location**: global

### ✅ Workload Identity Provider
- **Name**: `github-provider`
- **Issuer URI**: `https://token.actions.githubusercontent.com`
- **Attribute Condition**: `assertion.repository=='inderanz/x-sre-agents'`
- **Status**: ACTIVE

### ✅ Service Account
- **Name**: `github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com`
- **Binding**: Correctly bound to `inderanz/x-sre-agents`
- **Permissions**: All required roles granted

## Expected Behavior

After this fix:

1. **GitHub Actions authentication** will work correctly
2. **Workload Identity Federation** will accept credentials from `inderanz/x-sre-agents`
3. **Deploy and Terraform workflows** will run successfully
4. **No more attribute condition rejections**

## Security Benefits

- ✅ **Repository-specific access** - Only `inderanz/x-sre-agents` can use this service account
- ✅ **Exact match validation** - Attribute condition ensures precise repository matching
- ✅ **No credential exposure** - Uses temporary tokens via WIF
- ✅ **Audit trail** - All authentication events are logged

## Next Steps

1. **Monitor GitHub Actions** - Check that workflows run successfully
2. **Verify deployment** - Confirm the service deploys to Cloud Run
3. **Test endpoints** - Validate the FastAPI application is accessible
4. **Deploy infrastructure** - Run Terraform workflow for Langflow setup

## Troubleshooting

If you encounter similar issues in the future:

1. **Check repository name** - Verify the exact GitHub repository name
2. **Verify attribute condition** - Ensure it matches the repository exactly
3. **Check service account binding** - Confirm the binding uses the correct repository
4. **Review GitHub Actions logs** - Look for specific error messages

## Commands for Verification

```bash
# Check provider configuration
gcloud iam workload-identity-pools providers describe "github-provider" \
  --project="arctic-moon-463710-t0" \
  --location="global" \
  --workload-identity-pool="github-pool"

# Check service account bindings
gcloud iam service-accounts get-iam-policy "github-actions-sa@arctic-moon-463710-t0.iam.gserviceaccount.com" \
  --project="arctic-moon-463710-t0"
``` 