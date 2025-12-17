# How to Upload Notebooks to Azure ML Studio

## Problem
The notebooks in the `azureml_notebooks/` folder were empty (just created as placeholders).

## Solution
I've created proper notebooks with content in the `notebooks/` folder:
- `Engagement_Model_Demo.ipynb` - Full demo notebook
- `Quick_Model_Check.ipynb` - Quick verification notebook

## Upload to Azure ML Studio (2 minutes)

### Method 1: Via Azure ML Studio UI (RECOMMENDED)

1. **Open Azure ML Studio**
   - Go to: https://ml.azure.com
   - Select workspace: `engagement-ml-ws`

2. **Navigate to Notebooks**
   - Click "Notebooks" in the left sidebar
   - You'll see the file browser

3. **Upload Notebooks**
   - Click the "📁" (folder) icon or "Upload files" button
   - Select both notebooks from the `notebooks/` folder:
     - `Engagement_Model_Demo.ipynb`
     - `Quick_Model_Check.ipynb`
   - Click "Upload"

4. **Run a Notebook**
   - Click on `Quick_Model_Check.ipynb`
   - Select compute: "Serverless Compute" or create a compute instance
   - Click "Run All" or run cells individually

### Method 2: Via Python SDK (Alternative)

If you want to upload programmatically:

```python
from azure.ai.ml import MLClient
from azure.identity import InteractiveBrowserCredential

credential = InteractiveBrowserCredential(tenant_id="78ddbe5d-b682-466c-bad0-6ffbaf7ceb2d")
ml_client = MLClient(
    credential=credential,
    subscription_id="10ceef72-c9cd-4fb6-844b-ee8661d294fc",
    resource_group_name="rg-engagement-ml",
    workspace_name="engagement-ml-ws"
)

# Note: Notebooks are typically uploaded via the UI
# The SDK is mainly for jobs, models, and datasets
```

## What the Notebooks Do

### `Engagement_Model_Demo.ipynb`
- Connects to Azure ML Workspace
- Retrieves registered model (`engagement-gb-model`)
- Lists experiment jobs
- Displays model metrics (MAE, RMSE, R²)
- Shows model metadata and tags

### `Quick_Model_Check.ipynb`
- Fast verification script
- Checks model registry
- Checks experiments
- Checks compute cluster
- Minimal output for quick status check

## Expected Output

When you run the notebooks, you should see:

```
✅ Connected to workspace: engagement-ml-ws
   Resource Group: rg-engagement-ml
   Subscription: 10ceef72-c9cd-4fb6-844b-ee8661d294fc

Model Name: engagement-gb-model
Version: 2
Description: Gradient Boosting model for social media engagement rate prediction

Model Tags:
  framework: scikit-learn
  algorithm: HistGradientBoostingRegressor
  mae: 0.3500
  rmse: 1.1642
  r2: -0.0727
  features: 23
  samples: 11899
  stage: production

📊 Model Performance Metrics:
Metric              Value
MAE                 0.3500
RMSE                1.1642
R²                  -0.0727
Features            23
Training Samples    11899
```

## Troubleshooting

### If notebooks don't appear in Azure ML Studio:
1. Make sure you're in the correct workspace (`engagement-ml-ws`)
2. Refresh the browser
3. Check the "Users" folder in the Notebooks section

### If cells fail to run:
1. Select a compute instance (or create one)
2. Make sure the kernel is "Python 3.10 - SDK v2"
3. Install required packages if prompted:
   ```python
   %pip install azure-ai-ml azure-identity pandas
   ```

### If authentication fails:
1. The notebook will prompt for Azure login
2. Use the same credentials as your Azure Portal
3. Grant permissions when prompted

## Why This Matters for Your Project

The professor will see:
1. **Working notebooks** in Azure ML Studio
2. **Code that demonstrates** model registry access
3. **Metrics visualization** from the registered model
4. **Experiment tracking** integration
5. **Professional ML workflow** using Azure ML SDK

This shows you understand:
- Azure ML Studio notebook environment
- Model registry and versioning
- Experiment tracking
- Azure ML SDK v2
- ML governance best practices

## Quick Verification

After uploading, the professor can:
1. Open Azure ML Studio
2. Click "Notebooks"
3. See your uploaded notebooks
4. Run them to verify the model and experiments
5. See live output showing your model metrics

This provides **interactive proof** that your ML pipeline is working in Azure.

