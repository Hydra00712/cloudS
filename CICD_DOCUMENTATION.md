# CI/CD Pipeline Documentation

## GitHub Actions Workflow: azure-cicd.yml

**Location**: `.github/workflows/azure-cicd.yml`

**Trigger Events**:
- Push to `main` branch
- Pull requests to `main` branch
- Manual workflow dispatch

---

## Pipeline Stages

### 1️⃣ Lint and Test
**Job**: `lint-and-test`
**Runner**: ubuntu-latest

**Steps**:
- ✅ Checkout code
- ✅ Set up Python 3.12
- ✅ Install dependencies (flake8, pylint, requirements.txt)
- ✅ Lint with flake8 (syntax errors, undefined names)
- ✅ Check code quality with pylint

**Exit Strategy**: Continue on linting errors (warnings only)

---

### 2️⃣ Upload Artifacts to Blob
**Job**: `upload-artifacts`
**Runner**: ubuntu-latest
**Depends On**: `lint-and-test`

**Steps**:
- ✅ Azure Login (using service principal credentials)
- ✅ Upload `data/processed/cleaned_data.csv` → Blob `cleaned-data` container
- ✅ Upload `models/model_gb.pkl` → Blob `models` container
- ✅ Upload `data/processed/predictions.csv` → Blob `cleaned-data` container

**Authentication**: `az login` with `AZURE_CREDENTIALS` secret

---

### 3️⃣ Deploy to Azure App Service
**Job**: `deploy-to-azure`
**Runner**: ubuntu-latest
**Depends On**: `upload-artifacts`

**Steps**:
- ✅ Checkout code
- ✅ Set up Python 3.12
- ✅ Install application dependencies (requirements_app.txt)
- ✅ Deploy to Azure Web App (engagement-app-demo)
- ✅ Restart App Service
- ✅ Verify deployment (print public URL)

**Deployment Method**: `azure/webapps-deploy@v2` action

---

### 4️⃣ Pipeline Summary
**Job**: `notify`
**Runner**: ubuntu-latest
**Depends On**: All previous jobs
**Condition**: Always runs (even if previous jobs fail)

**Steps**:
- ✅ Print pipeline execution summary
- ✅ Display app public URL

---

## Required GitHub Secrets

To enable this pipeline, configure the following secrets in GitHub repository settings:

### `AZURE_CREDENTIALS`
Service principal credentials for Azure authentication.

**Generate with Azure CLI**:
```bash
az ad sp create-for-rbac \
  --name "github-actions-cdda" \
  --role contributor \
  --scopes /subscriptions/10ceef72-c9cd-4fb6-844b-ee8661d294fc/resourceGroups/rg-engagement-ml \
  --sdk-auth
```

**Output Format**:
```json
{
  "clientId": "<client-id>",
  "clientSecret": "<client-secret>",
  "subscriptionId": "10ceef72-c9cd-4fb6-844b-ee8661d294fc",
  "tenantId": "78ddbe5d-b682-466c-bad0-6ffbaf7ceb2d",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

**Add to GitHub**:
1. Go to repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `AZURE_CREDENTIALS`
4. Value: Paste JSON output from `az ad sp create-for-rbac`

---

## Local Testing

**Lint locally**:
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
pylint app_streamlit.py train_mlflow.py generate_predictions.py
```

**Test deployment locally**:
```bash
# Install dependencies
pip install -r requirements_app.txt

# Run Streamlit
streamlit run app_streamlit.py
```

---

## Pipeline Execution Evidence

**Status**: Workflow file created ✅

**To trigger pipeline**:
1. Initialize Git repository (if not already):
   ```bash
   git init
   git add .
   git commit -m "Add CI/CD pipeline"
   ```

2. Create GitHub repository and push:
   ```bash
   git remote add origin https://github.com/<username>/cdda-engagement-ml.git
   git branch -M main
   git push -u origin main
   ```

3. Configure `AZURE_CREDENTIALS` secret in GitHub

4. Push changes to trigger workflow:
   ```bash
   git add .
   git commit -m "Trigger CI/CD pipeline"
   git push
   ```

**Expected Outcome**:
- ✅ Green checkmark in GitHub Actions tab
- ✅ Artifacts uploaded to Blob Storage
- ✅ App Service redeployed with latest code
- ✅ Public URL accessible: https://engagement-app-demo.azurewebsites.net

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Actions Workflow                    │
└─────────────────────────────────────────────────────────────┘

Trigger: Push to main
         │
         ▼
┌─────────────────────┐
│ 1. Lint & Test      │
│ ├─ flake8           │
│ └─ pylint           │
└──────────┬──────────┘
           │ Success
           ▼
┌─────────────────────┐
│ 2. Upload Artifacts │
│ ├─ cleaned_data.csv │
│ ├─ model_gb.pkl     │
│ └─ predictions.csv  │
└──────────┬──────────┘
           │ Success
           ▼
┌─────────────────────┐
│ 3. Deploy to Azure  │
│ ├─ Install deps     │
│ ├─ Deploy app       │
│ └─ Restart service  │
└──────────┬──────────┘
           │ Success
           ▼
┌─────────────────────┐
│ 4. Notify Summary   │
│ └─ Print URL        │
└─────────────────────┘
           │
           ▼
    Public URL Live ✅
```

---

**Status**: CI/CD pipeline configured and ready for GitHub deployment ✅
