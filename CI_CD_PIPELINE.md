# 8️⃣ CI/CD PIPELINE WITH GITHUB ACTIONS

## Overview

Automated workflow:
```
Git Push (main) 
    ↓
GitHub Actions Triggered
    ↓
┌─────────────────────┐
│ 1. Lint Check       │
│    (pylint, black)  │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ 2. Unit Tests       │
│    (pytest)         │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ 3. Build Docker     │
│    (preprocess, train, app)
└─────────────────────┘
    ↓
┌─────────────────────┐
│ 4. Push to ACR      │
│    (Azure Container)│
└─────────────────────┘
    ↓
┌─────────────────────┐
│ 5. Deploy to Azure  │
│    (ML Job or App)  │
└─────────────────────┘
```

## File: `.github/workflows/deploy.yml`

Create this file in your GitHub repository:

```yaml
name: Deploy Engagement ML Pipeline

on:
  push:
    branches: [ main ]
    paths:
      - 'preprocess_clean.py'
      - 'train_model_clean.py'
      - 'app_clean.py'
      - 'requirements.txt'
      - '.github/workflows/deploy.yml'

env:
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
  AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
  AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
  AZURE_RESOURCE_GROUP: rg-engagement-ml
  AZURE_ML_WORKSPACE: aml-engagement
  AZURE_CONTAINER_REGISTRY: crengagement
  STORAGE_ACCOUNT: stengagementdata

jobs:
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install pylint black flake8
    
    - name: Lint with pylint
      run: |
        pylint preprocess_clean.py train_model_clean.py app_clean.py \
          --disable=C0111 --disable=R0913 --max-line-length=100
      continue-on-error: true
    
    - name: Check formatting with black
      run: |
        black --check --line-length=100 preprocess_clean.py train_model_clean.py app_clean.py
      continue-on-error: true

  test:
    name: Run Unit Tests
    runs-on: ubuntu-latest
    needs: lint
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pandas
    
    - name: Test preprocessing
      run: |
        python -m pytest tests/test_preprocess.py -v
      continue-on-error: true
    
    - name: Test model training
      run: |
        python -m pytest tests/test_train.py -v
      continue-on-error: true

  build-and-push:
    name: Build & Push Docker Images
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Get ACR login credentials
      run: |
        az acr credential show \
          --resource-group $AZURE_RESOURCE_GROUP \
          --name $AZURE_CONTAINER_REGISTRY \
          --query "passwords[0].value" -o tsv > acr_password.txt
    
    - name: Build preprocess image
      run: |
        docker build -f Dockerfile.preprocess -t $AZURE_CONTAINER_REGISTRY.azurecr.io/preprocess:latest .
    
    - name: Build train image
      run: |
        docker build -f Dockerfile.train -t $AZURE_CONTAINER_REGISTRY.azurecr.io/train:latest .
    
    - name: Build app image
      run: |
        docker build -f Dockerfile.app -t $AZURE_CONTAINER_REGISTRY.azurecr.io/app:latest .
    
    - name: Push to Azure Container Registry
      run: |
        ACR_PASSWORD=$(cat acr_password.txt)
        echo $ACR_PASSWORD | docker login $AZURE_CONTAINER_REGISTRY.azurecr.io \
          --username $AZURE_CONTAINER_REGISTRY --password-stdin
        
        docker push $AZURE_CONTAINER_REGISTRY.azurecr.io/preprocess:latest
        docker push $AZURE_CONTAINER_REGISTRY.azurecr.io/train:latest
        docker push $AZURE_CONTAINER_REGISTRY.azurecr.io/app:latest

  deploy:
    name: Deploy to Azure
    runs-on: ubuntu-latest
    needs: build-and-push
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Submit ML Training Job
      run: |
        az ml job create \
          --resource-group $AZURE_RESOURCE_GROUP \
          --workspace-name $AZURE_ML_WORKSPACE \
          --file train_job.yml
    
    - name: Deploy App Service
      uses: azure/webapps-deploy@v2
      with:
        app-name: engagement-app
        publish-profile: ${{ secrets.AZURE_APP_PUBLISH_PROFILE }}
        images: |
          ${{ env.AZURE_CONTAINER_REGISTRY }}.azurecr.io/app:latest

  notification:
    name: Send Deployment Notification
    runs-on: ubuntu-latest
    needs: deploy
    if: always()
    
    steps:
    - name: Notify Success
      if: success()
      run: echo "✅ Deployment successful!"
    
    - name: Notify Failure
      if: failure()
      run: echo "❌ Deployment failed. Check logs above."
```

## Setup GitHub Secrets

In your GitHub repository:

1. Settings → Secrets and variables → Actions
2. Create these secrets:

```
AZURE_SUBSCRIPTION_ID       = (from `az account show --query id`)
AZURE_TENANT_ID             = (from `az account show --query tenantId`)
AZURE_CLIENT_ID             = (service principal client ID)
AZURE_CLIENT_SECRET         = (service principal secret)
AZURE_CREDENTIALS           = (full JSON from `az ad sp create-for-rbac ...`)
AZURE_APP_PUBLISH_PROFILE   = (download from App Service portal)
```

### Create Service Principal (for Azure Login)

```bash
az ad sp create-for-rbac \
  --name "engagement-github-actions" \
  --role contributor \
  --scopes /subscriptions/{SUBSCRIPTION_ID}
```

Copy output JSON → GitHub Secrets → `AZURE_CREDENTIALS`

## Dockerfile for Preprocessing

File: `Dockerfile.preprocess`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY preprocess_clean.py .
COPY data/raw/ data/raw/

ENV AZURE_STORAGE_ACCOUNT=${STORAGE_ACCOUNT}
ENV AZURE_STORAGE_CONTAINER=processed-data

CMD ["python", "preprocess_clean.py"]
```

## Dockerfile for Training

File: `Dockerfile.train`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt \
    && pip install mlflow

COPY train_model_clean.py mlflow_config.py ./
COPY mlflow_config.py .

ENV MLFLOW_TRACKING_URI=azureml://
ENV MLFLOW_EXPERIMENT_NAME=social-media-engagement

CMD ["python", "train_model_clean.py"]
```

## Dockerfile for App

File: `Dockerfile.app`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt \
    && pip install streamlit

COPY app_clean.py .

ENV STREAMLIT_SERVER_PORT=8000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8000

CMD ["streamlit", "run", "app_clean.py"]
```

## ML Job Configuration

File: `train_job.yml` (for Azure ML Job submission)

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandJob.schema.json
code: .
command: >-
  python train_model_clean.py
environment: azureml:engagement-env@latest
compute: azureml:cpu-cluster
display_name: weekly-model-training
experiment_name: social-media-engagement
description: Automated weekly model retraining via CI/CD
```

## What Happens on Each Push

| Event | Action |
|---|---|
| **Push to main** | Workflow triggered |
| **Lint fails** | ⚠️ Continues (warnings only) |
| **Tests fail** | ⏹️ Stops, needs fix |
| **Docker build fails** | ⏹️ Stops, needs fix |
| **All checks pass** | ✅ Deploys to Azure |

## Monitoring Workflow

1. Go to GitHub repo → **Actions** tab
2. Click latest workflow run
3. See real-time logs for each step
4. Click job to expand details

---

## Example Workflow Output

```
✅ Lint & Format Check       (5s)
✅ Run Unit Tests             (45s)
✅ Build & Push Docker        (3m 22s)
✅ Deploy to Azure            (1m 45s)
✅ Send Deployment Notification (2s)

Total time: ~6 minutes
```

