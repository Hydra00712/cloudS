# 6️⃣ DEPLOYMENT & INFERENCE STRATEGY

## Option A: Azure ML Real-Time Endpoint (RECOMMENDED)

### Why Choose This?
- ✅ No container infrastructure needed
- ✅ Auto-scaling built-in
- ✅ RESTful API (easy integration)
- ✅ Free tier CPU-only endpoint available
- ✅ Swagger docs auto-generated
- ✅ Azure Monitor integration

### Deployment Steps

#### Step 1: Create Score Script

File: `score.py`
```python
"""Scoring script for Azure ML endpoint"""

import json
import joblib
import numpy as np
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import pandas as pd

def init():
    """Called once when endpoint starts"""
    global model, encoders
    
    # Load model from Model Registry
    # (Azure ML handles this automatically)
    
    # For now, load from blob
    credential = DefaultAzureCredential()
    blob_service = BlobServiceClient(
        account_url="https://{STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=credential
    )
    
    models_container = blob_service.get_container_client("models")
    blob = models_container.get_blob_client("model_XGBoost.pkl")
    
    import pickle
    model = pickle.loads(blob.download_blob().readall())
    
    print("✅ Model loaded successfully")


def run(raw_data):
    """
    Called for each prediction request
    
    Input format:
    {
        "data": [{
            "day_of_week_encoded": 0,
            "platform_encoded": 1,
            ... (23 features total)
        }]
    }
    """
    
    try:
        # Parse input
        data = json.loads(raw_data)
        features = data["data"][0]  # First sample
        
        # Convert to numpy array (same order as training)
        feature_order = [
            'day_of_week_encoded', 'platform_encoded', 'topic_category_encoded',
            'emotion_type_encoded', 'location_encoded', 'language_encoded',
            'sentiment_bucket_encoded', 'toxicity_bucket_encoded',
            'past_perf_bucket_encoded', 'growth_bucket_encoded',
            'sentiment_score', 'toxicity_score', 'user_past_sentiment_avg',
            'user_engagement_growth', 'sentiment_bucket', 'toxicity_bucket',
            'past_perf_bucket', 'growth_bucket', 'sentiment_toxicity_interaction',
            'abs_sentiment', 'perf_momentum', 'toxicity_squared', 'sentiment_squared'
        ]
        
        X = np.array([[features[col] for col in feature_order]])
        
        # Predict
        engagement_rate = model.predict(X)[0]
        
        # Categorize
        if engagement_rate < 0.3:
            level = "LOW"
        elif engagement_rate < 0.6:
            level = "MODERATE"
        else:
            level = "HIGH"
        
        result = {
            "engagement_rate": float(engagement_rate),
            "level": level
        }
        
        return json.dumps(result)
    
    except Exception as e:
        return json.dumps({"error": str(e)})
```

#### Step 2: Create Environment File

File: `environment.yml`
```yaml
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
    - numpy==1.24.0
    - azure-storage-blob==12.18.0
    - azure-identity==1.14.0
```

#### Step 3: Deploy via Azure ML CLI

```bash
# Create deployment configuration
cat > deployment.yml << EOF
name: engagement-predictor
endpoint_name: engagement-endpoint
model:
  path: models:engagement-predictor:1
code_configuration:
  code: score.py
  scoring_script: score.py
environment: azureml:engagement-inference@latest
compute: cpu-cluster
instance_type: Standard_DS1_v2
request_settings:
  request_timeout_ms: 3000
EOF

# Deploy
az ml online-deployment create \
  --resource-group rg-engagement-ml \
  --workspace-name aml-engagement \
  --file deployment.yml \
  --all-traffic
```

#### Step 4: Test Endpoint

```bash
# Get endpoint URL
ENDPOINT_URL=$(az ml online-endpoint show \
  --resource-group rg-engagement-ml \
  --workspace-name aml-engagement \
  --name engagement-endpoint \
  --query scoring_uri -o tsv)

# Get API key
API_KEY=$(az ml online-endpoint get-credentials \
  --resource-group rg-engagement-ml \
  --workspace-name aml-engagement \
  --name engagement-endpoint \
  --query primaryKey -o tsv)

# Test prediction
curl -X POST $ENDPOINT_URL \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data": [{"day_of_week_encoded": 0, "platform_encoded": 1, ...}]}'
```

---

## Option B: Azure Container Apps (Alternative)

If you want to deploy the full Streamlit app:

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app_clean.py .
COPY data/processed/encoders.pkl data/processed/

ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8080

CMD ["streamlit", "run", "app_clean.py"]
```

### Deploy to Container Apps
```bash
# Build image
az acr build \
  --resource-group rg-engagement-ml \
  --registry crengagement \
  --image engagement-app:latest .

# Create Container App
az containerapp create \
  --resource-group rg-engagement-ml \
  --name engagement-app \
  --image crengagement.azurecr.io/engagement-app:latest \
  --environment-variables \
    ML_ENDPOINT_URL="https://..." \
    ML_API_KEY="..." \
  --ingress external \
  --target-port 8080
```

---

## Summary

| Aspect | ML Endpoint | Container App |
|--------|---|---|
| **Best for** | API-first, scalable | Full UI, more control |
| **Free tier** | ✅ CPU-only | ⚠️ ~$15/month minimum |
| **Deployment time** | 5-10 min | 10-15 min |
| **Recommendation** | **YES** | Alternative |

