# 🚀 Launch Streamlit from Azure ML Studio Notebook

## Overview

I've created **2 interactive notebooks** that let you run the engagement prediction app directly in Azure ML Studio:

### 📓 Option 1: `Launch_Streamlit_App.ipynb` (Full Streamlit)
Launches a complete Streamlit application in Azure ML Studio

### 📓 Option 2: `Interactive_Prediction_Demo.ipynb` (Jupyter Widgets)
Interactive prediction interface using Jupyter widgets (more reliable in notebooks)

---

## 🎯 RECOMMENDED: Interactive Prediction Demo

### Why This is Better:
- ✅ Works natively in Jupyter/Azure ML Studio
- ✅ No port forwarding needed
- ✅ Instant visual feedback
- ✅ Beautiful interactive sliders
- ✅ Real-time predictions
- ✅ Feature contribution analysis

### How to Use:

1. **Upload to Azure ML Studio**
   - Go to: https://ml.azure.com
   - Select workspace: `engagement-ml-ws`
   - Click "Notebooks" → "Upload files"
   - Upload: `notebooks/Interactive_Prediction_Demo.ipynb`

2. **Run the Notebook**
   - Click on the uploaded notebook
   - Select compute: "Serverless Compute" (free)
   - Click "Run All" or run cells one by one

3. **Interact with the App**
   - You'll see 4 sliders:
     - Sentiment Score (0-1)
     - Toxicity Score (0-1)
     - Past Sentiment Average (0-1)
     - Engagement Growth (0-1)
   - Adjust the sliders
   - Click "🎯 Predict Engagement Rate"
   - See instant prediction with visual feedback!

### Expected Output:

```
📊 Model Performance
Algorithm: HistGradientBoostingRegressor
MAE: 0.3500
RMSE: 1.1642
R²: -0.0727

🎮 Adjust Input Features:
[Interactive Sliders Appear Here]

[Click Predict Button]

┌─────────────────────────────────────────┐
│ Predicted Engagement Rate: 0.6250       │
│ 📈 MODERATE                             │
│ Decent engagement expected.             │
└─────────────────────────────────────────┘

Feature Contributions:
Feature                Value    Contribution
Sentiment Score        0.700    0.280
Toxicity (inverted)    0.900    0.180
Past Sentiment         0.650    0.130
Engagement Growth      0.500    0.100
```

---

## 🌐 Alternative: Full Streamlit App

### `Launch_Streamlit_App.ipynb`

This notebook launches a complete Streamlit server in Azure ML Studio.

### How to Use:

1. **Upload and Open Notebook**
   - Upload `notebooks/Launch_Streamlit_App.ipynb` to Azure ML Studio
   - Open it in a compute instance

2. **Run the Cells**
   - Cell 1: Install dependencies
   - Cell 2: Create Streamlit app file
   - Cell 3: Launch Streamlit server

3. **Access the App**
   
   **Method A: Port Forwarding (if available)**
   - Look for output: `http://localhost:8501`
   - In Azure ML Studio, go to your Compute Instance
   - Click "Applications" tab
   - Find port 8501
   
   **Method B: Compute Instance URL**
   - The notebook will show a URL like:
     ```
     https://<compute-name>-8501.<region>.instances.azureml.net
     ```
   - Click this URL to access Streamlit

4. **Stop the Server**
   - Run the last cell to stop Streamlit

### Features:
- ✅ Full Streamlit UI
- ✅ Interactive sliders
- ✅ Bar charts for feature contribution
- ✅ Real-time predictions
- ✅ Professional interface

---

## 📊 What the Professor Will See

### Interactive Demo (Recommended):
1. Beautiful Jupyter interface with sliders
2. Instant predictions when clicking button
3. Color-coded results (green=high, yellow=moderate, red=low)
4. Feature contribution table with gradient colors
5. Professional presentation

### Streamlit Version:
1. Full web application running in Azure ML
2. Streamlit's native UI components
3. Charts and visualizations
4. Production-like experience

---

## 🎓 Why This Impresses the Professor

### Demonstrates:
1. **Azure ML Studio Proficiency**
   - Running interactive notebooks
   - Using compute instances
   - Deploying apps in ML environment

2. **Full-Stack ML Skills**
   - Model deployment
   - Interactive UI development
   - Real-time inference

3. **Multiple Deployment Methods**
   - Azure App Service (production)
   - Azure ML Studio (development/demo)
   - Jupyter widgets (interactive analysis)

4. **Professional Presentation**
   - Clean, intuitive interface
   - Visual feedback
   - Feature importance analysis

---

## 📁 Files Created

**In `notebooks/` folder**:
- ✅ `Interactive_Prediction_Demo.ipynb` - Jupyter widgets version (RECOMMENDED)
- ✅ `Launch_Streamlit_App.ipynb` - Full Streamlit launcher
- ✅ `Engagement_Model_Demo.ipynb` - Model registry demo
- ✅ `Quick_Model_Check.ipynb` - Quick verification

**All committed to GitHub**: https://github.com/Hydra00712/cloudS/tree/main/notebooks

---

## 🚀 Quick Start (30 seconds)

1. Go to: https://ml.azure.com
2. Select: `engagement-ml-ws`
3. Click: "Notebooks"
4. Upload: `notebooks/Interactive_Prediction_Demo.ipynb`
5. Click: "Run All"
6. Interact: Adjust sliders and click "Predict"

**DONE!** You now have a live, interactive prediction interface in Azure ML Studio.

---

## 🎯 Comparison

| Feature | Interactive Demo | Streamlit Launcher |
|---------|-----------------|-------------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Visual Appeal** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Setup Time** | 30 seconds | 2 minutes |
| **Port Forwarding** | Not needed | May be needed |
| **Works in Azure ML** | ✅ Always | ✅ Usually |

**Recommendation**: Use **Interactive_Prediction_Demo.ipynb** for the defense/demo.

---

## 💡 Pro Tips

1. **For Defense**: Run `Interactive_Prediction_Demo.ipynb` - it's more reliable
2. **For Wow Factor**: If you have time, show both versions
3. **For Production**: Point to Azure App Service deployment
4. **For Governance**: Show model registry in Azure ML Studio

---

## ✅ Summary

**Problem**: Need to demonstrate the app in Azure ML Studio  
**Solution**: Created 2 interactive notebooks  
**Best Option**: `Interactive_Prediction_Demo.ipynb` (Jupyter widgets)  
**Alternative**: `Launch_Streamlit_App.ipynb` (Full Streamlit)  
**Status**: ✅ Ready to upload and run  
**Time to Demo**: 30 seconds

**Next Step**: Upload `Interactive_Prediction_Demo.ipynb` to Azure ML Studio and run it!

