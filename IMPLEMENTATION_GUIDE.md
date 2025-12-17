# 📋 COMPLETE IMPLEMENTATION GUIDE

## Quick Start Checklist

### Phase 1: Local Testing (Before Azure)
- [ ] ✅ preprocess_clean.py works locally
- [ ] ✅ train_model_clean.py produces model.pkl
- [ ] ✅ app_clean.py runs with `streamlit run`

### Phase 2: Azure Setup (Do Once)
- [ ] Create Azure account (free tier)
- [ ] Run `azure_setup.sh` to provision all resources
- [ ] Save connection strings to `.env`
- [ ] Configure GitHub Secrets for CI/CD

### Phase 3: Cloud Migration (Sequential)
- [ ] Update preprocess_clean.py to read/write Azure Blob
- [ ] Update train_model_clean.py with MLflow + Azure storage
- [ ] Deploy model to Azure ML endpoint
- [ ] Test endpoint with sample request

### Phase 4: Infrastructure (Automation)
- [ ] Create GitHub Actions workflow
- [ ] Setup Application Insights monitoring
- [ ] Create Power BI dashboard
- [ ] Configure Key Vault + RBAC

### Phase 5: Defense Preparation
- [ ] Export Power BI dashboard to PDF
- [ ] Take screenshots of each Azure service
- [ ] Practice 5-minute pitch
- [ ] Prepare Q&A answers

---

## File Inventory

### Core ML Files (Already Created)
```
preprocess_clean.py      ✅ Optimized
train_model_clean.py     ✅ Optimized + syntax error fixed
app_clean.py             ✅ Optimized
requirements.txt         ✅ Dependency list
```

### New Azure-Ready Files (Create These)
```
📁 Azure Infrastructure
├─ azure_setup.sh                      # CLI provisioning script
├─ mlflow_config.py                    # MLflow setup helpers
├─ train_with_mlflow.py               # Training with experiment tracking
├─ score.py                           # ML endpoint scoring script
├─ monitoring.py                      # Instrumentation code

📁 Configuration Files
├─ environment.yml                    # Conda environment for deployment
├─ Dockerfile.preprocess              # Container for preprocessing
├─ Dockerfile.train                   # Container for training
├─ Dockerfile.app                     # Container for Streamlit app
├─ .github/workflows/deploy.yml       # GitHub Actions CI/CD

📁 Documentation (Already Created)
├─ MIGRATION_PLAN.md                 # How to migrate each file
├─ MLFLOW_SETUP.md                   # Experiment tracking guide
├─ DEPLOYMENT_PLAN.md                # Model deployment options
├─ POWERBI_DASHBOARD.md              # Dashboard creation
├─ CI_CD_PIPELINE.md                 # GitHub Actions setup
├─ MONITORING_ALERTS.md              # Monitoring + alerting
├─ SECURITY_GOVERNANCE.md            # Security implementation
├─ PROFESSOR_DEFENSE.md              # Defense talking points
```

---

## Step-by-Step Implementation

### STEP 1: Provision Azure Resources (20 minutes)

```bash
# 1. Login to Azure
az login

# 2. Set default subscription
az account set --subscription "Azure for Students"

# 3. Run provisioning script
bash azure_setup.sh

# 4. Save output (connection strings, keys)
# Store in .env file (never commit to GitHub!)
```

**Verify:**
```bash
az group list --query "[].name"
# Should show: rg-engagement-ml

az storage account list --resource-group rg-engagement-ml
# Should show: stengagementdata...
```

---

### STEP 2: Create Azure-Ready Python Files (60 minutes)

#### File: `mlflow_config.py` (Copy from MLFLOW_SETUP.md)

```bash
cp MLFLOW_SETUP.md mlflow_config.py
# Edit to keep only Python code sections
```

#### File: `train_with_mlflow.py` (Copy from MLFLOW_SETUP.md)

```bash
cp MLFLOW_SETUP.md train_with_mlflow.py
# Edit to keep only Python code sections
```

#### File: `score.py` (Copy from DEPLOYMENT_PLAN.md)

```bash
cp DEPLOYMENT_PLAN.md score.py
# Edit to keep only Python code sections
```

---

### STEP 3: Update requirements.txt

```bash
# Add Azure + MLflow packages
cat >> requirements.txt << EOF
azure-storage-blob==12.18.0
azure-identity==1.14.0
azure-monitor-opentelemetry==1.0.0
mlflow==2.9.0
azure-ai-ml==1.13.0
EOF
```

---

### STEP 4: Create Docker Images (45 minutes)

#### Dockerfile.preprocess
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY preprocess_clean.py .
ENV AZURE_STORAGE_ACCOUNT=${STORAGE_ACCOUNT}
CMD ["python", "preprocess_clean.py"]
```

#### Dockerfile.train
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY train_with_mlflow.py mlflow_config.py ./
ENV MLFLOW_TRACKING_URI=azureml://
CMD ["python", "train_with_mlflow.py"]
```

#### Dockerfile.app
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install streamlit
COPY app_clean.py .
ENV STREAMLIT_SERVER_PORT=8000
EXPOSE 8000
CMD ["streamlit", "run", "app_clean.py"]
```

---

### STEP 5: Setup GitHub Repository (30 minutes)

```bash
# Initialize repo
git init
git add .
git commit -m "Initial commit: Cloud ML project"

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/engagement-ml.git
git push -u origin main
```

**Add Secrets:**
```
Go to GitHub → Settings → Secrets and variables → Actions

Create these secrets:
├─ AZURE_SUBSCRIPTION_ID
├─ AZURE_TENANT_ID
├─ AZURE_CLIENT_ID
├─ AZURE_CLIENT_SECRET
└─ AZURE_CREDENTIALS (full JSON)
```

---

### STEP 6: Create GitHub Actions Workflow (20 minutes)

Create file: `.github/workflows/deploy.yml`

```bash
# Copy from CI_CD_PIPELINE.md
cp CI_CD_PIPELINE.md .github/workflows/deploy.yml
```

**Commit and push:**
```bash
git add .github/
git commit -m "Add CI/CD pipeline"
git push
```

**Verify:** GitHub → Actions tab should show workflow starting

---

### STEP 7: Deploy Model to Azure ML (45 minutes)

```bash
# Create conda environment file
cat > environment.yml << EOF
name: engagement-inference
channels:
  - conda-forge
dependencies:
  - python=3.11
  - pip
  - pip:
    - xgboost==2.0.0
    - scikit-learn==1.3.0
    - pandas==2.0.0
EOF

# Register environment
az ml environment create \
  --resource-group rg-engagement-ml \
  --workspace-name aml-engagement \
  --name engagement-env \
  --file environment.yml

# Create deployment config
cat > deployment.yml << EOF
name: engagement-predictor
endpoint_name: engagement-endpoint
model:
  path: models:engagement-predictor:1
code_configuration:
  code: .
  scoring_script: score.py
environment: azureml:engagement-env@latest
compute: azureml:cpu-cluster
instance_type: Standard_DS1_v2
EOF

# Deploy
az ml online-deployment create \
  --resource-group rg-engagement-ml \
  --workspace-name aml-engagement \
  --file deployment.yml \
  --all-traffic

# Test
az ml online-endpoint invoke \
  --endpoint-name engagement-endpoint \
  --resource-group rg-engagement-ml \
  --workspace-name aml-engagement \
  --request-file sample_request.json
```

---

### STEP 8: Setup Monitoring (30 minutes)

```bash
# Create alert for high latency
az monitor metrics alert create \
  --resource-group rg-engagement-ml \
  --rule-name "HighLatencyAlert" \
  --scopes /subscriptions/{SUB_ID}/resourceGroups/rg-engagement-ml/providers/Microsoft.MachineLearningServices/workspaces/aml-engagement \
  --condition "avg RequestLatency > 500" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2
```

---

### STEP 9: Create Power BI Dashboard (45 minutes)

```bash
# In Azure, run SQL script to create tables
# (See POWERBI_DASHBOARD.md for SQL script)

# Export from Azure SQL:
# 1. Open Power BI Desktop
# 2. Get Data → Azure SQL Database
# 3. Connect with credentials
# 4. Load: predictions, model_metrics tables
# 5. Create visualizations (see dashboard template)
# 6. Publish to workspace (optional)
# 7. Export to PDF
```

---

### STEP 10: Test Everything End-to-End (60 minutes)

```bash
# 1. Test preprocessing
python preprocess_clean.py
# Check: cleaned_data.csv created, encoders.pkl saved

# 2. Test training with MLflow
python train_with_mlflow.py
# Check: Models trained, MLflow experiment recorded

# 3. Test endpoint
curl -X POST https://engagement-endpoint.eastus2.inference.ml.azure.com/score \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{...}'
# Check: 200 status, prediction returned

# 4. Check monitoring
az monitor metrics list \
  --resource /subscriptions/{SUB_ID}/resourceGroups/rg-engagement-ml/providers/Microsoft.MachineLearningServices/workspaces/aml-engagement \
  --metric RequestLatency
# Check: Latency < 200ms

# 5. View Power BI dashboard
# Check: Metrics displayed correctly, data refreshed
```

---

## Time Estimate

| Phase | Task | Time |
|---|---|---|
| 1 | Azure provisioning | 20 min |
| 2 | Python files + Docker | 120 min |
| 3 | GitHub Actions setup | 30 min |
| 4 | Model deployment | 45 min |
| 5 | Monitoring + Power BI | 75 min |
| 6 | Testing + debugging | 60 min |
| | **TOTAL** | **~5.5 hours** |

---

## Troubleshooting Common Issues

### Issue 1: Azure CLI not found
```bash
# Solution:
pip install azure-cli
# Or download from https://aka.ms/installazurecliwindows
```

### Issue 2: Insufficient quota
```
Error: Quota exceeded for model training.

Solution:
az quota show --resource-group rg-engagement-ml
az quota request --sku "CPU" --amount 10
```

### Issue 3: Endpoint timeout
```
Error: Prediction request takes > 60 seconds.

Solution:
az ml online-deployment scale \
  --endpoint-name engagement-endpoint \
  --instance-count 3
```

### Issue 4: Storage access denied
```
Error: Unauthorized access to Blob Storage.

Solution:
# Grant yourself storage access
az storage account keys list --account-name stengagementdata
# Copy key to .env
# Or use Managed Identity (check SECURITY_GOVERNANCE.md)
```

### Issue 5: Model not found in registry
```
Error: Model version 1 doesn't exist.

Solution:
# Register model first
az ml model create \
  --resource-group rg-engagement-ml \
  --workspace-name aml-engagement \
  --name engagement-predictor \
  --version 1 \
  --path models/model_XGBoost.pkl
```

---

## Documentation to Print/Show Professor

1. **README.md** - High-level overview
2. **PROFESSOR_DEFENSE.md** - Talking points + Q&A
3. **MIGRATION_PLAN.md** - Architecture decisions
4. **CDDA Audit Table** - Coverage checklist
5. **Power BI Dashboard PDF** - Visualizations
6. **Architecture Diagram** - Data flow

---

## Final Verification Checklist

Before grading:

- [ ] All resources in Azure Portal (rg-engagement-ml)
- [ ] Model registered in Model Registry
- [ ] Endpoint responding to requests (< 200ms)
- [ ] GitHub Actions showing successful deployments
- [ ] MLflow experiments visible with metrics
- [ ] Power BI dashboard exported to PDF
- [ ] Monitoring alerts configured + screenshot taken
- [ ] Key Vault secrets configured
- [ ] RBAC roles assigned
- [ ] No hardcoded credentials in code
- [ ] .env file in .gitignore
- [ ] All documentation files created
- [ ] Defense script memorized

**Ready for presentation! 🎓**

