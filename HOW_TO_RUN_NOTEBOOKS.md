# 🚀 HOW TO RUN NOTEBOOKS IN AZURE ML STUDIO

## ✅ COMPUTE INSTANCE CREATED!

**Name**: `notebook-compute-free`  
**Size**: STANDARD_DS1_V2 (1 core, 3.5 GB RAM)  
**Status**: ✅ RUNNING  
**Auto-shutdown**: 30 minutes idle  
**Cost**: ~$0.10/hour when active (FREE tier eligible)

---

## 📋 STEP-BY-STEP GUIDE

### Step 1: Open Azure ML Studio ✅ DONE
The browser should now be open at: https://ml.azure.com

You should see the **Compute** page showing your new compute instance.

---

### Step 2: Go to Notebooks

1. Click **"Notebooks"** in the left sidebar (📓 icon)
2. You'll see the Notebooks interface

---

### Step 3: Upload Your Notebooks

**Option A: Drag & Drop**
1. Open File Explorer: `C:\Users\medad\Downloads\Cloud1\notebooks\`
2. Select all 4 `.ipynb` files
3. Drag them into the Azure ML Studio Notebooks area

**Option B: Upload Button**
1. Click the **"📁 Upload files"** button at the top
2. Navigate to: `C:\Users\medad\Downloads\Cloud1\notebooks\`
3. Select these files:
   - ✅ `Interactive_Prediction_Demo.ipynb` ⭐ START HERE
   - ✅ `Launch_Streamlit_App.ipynb`
   - ✅ `Engagement_Model_Demo.ipynb`
   - ✅ `Quick_Model_Check.ipynb`
4. Click **"Upload"**

---

### Step 4: Run a Notebook

1. **Click on** `Interactive_Prediction_Demo.ipynb` (recommended first)

2. **Select Compute**:
   - At the top, you'll see a "Compute" dropdown
   - Select: **`notebook-compute-free`**
   - Status should show: "Running" ✅

3. **Run the Notebook**:
   - Click **"▶ Run All"** button at the top
   - OR run cells one by one with **Shift + Enter**

4. **Wait for Results**:
   - First cell: Installs dependencies (~30 seconds)
   - Second cell: Shows model information
   - Third cell: **Interactive sliders appear!**
   - Adjust sliders and click "🎯 Predict"

---

## 🎯 WHAT YOU'LL SEE

### After Running `Interactive_Prediction_Demo.ipynb`:

```
📊 Model Performance
Algorithm: HistGradientBoostingRegressor
MAE: 0.3500
RMSE: 1.1642
R²: -0.0727

🎮 Adjust Input Features:

Sentiment:        [========|====] 0.70
Toxicity:         [==|==========] 0.10
Past Sentiment:   [======|======] 0.65
Engagement Growth:[=====|=======] 0.50

[🎯 Predict Engagement Rate]

┌─────────────────────────────────────────┐
│ Predicted Engagement Rate: 0.6250       │
│ 📈 MODERATE                             │
│ Decent engagement expected.             │
└─────────────────────────────────────────┘

Feature Contributions:
[Colored table with gradient showing each feature's impact]
```

---

## 🎬 QUICK START (30 SECONDS)

1. ✅ **Compute instance created** - `notebook-compute-free` is RUNNING
2. ⏳ **Go to Notebooks** - Click "Notebooks" in left sidebar
3. ⏳ **Upload** - Upload `Interactive_Prediction_Demo.ipynb`
4. ⏳ **Select compute** - Choose `notebook-compute-free`
5. ⏳ **Run All** - Click "▶ Run All"
6. ⏳ **Interact** - Adjust sliders and predict!

---

## 💰 COST SAFETY

✅ **Auto-shutdown**: Stops after 30 minutes of inactivity  
✅ **Smallest VM**: STANDARD_DS1_V2 (minimal cost)  
✅ **Only charged when running**: Stops when not in use  
✅ **Estimated cost**: ~$0.10/hour when active  
✅ **Free tier eligible**: Azure for Students may cover this

**To manually stop**:
1. Go to "Compute" → "Compute instances"
2. Click "Stop" next to `notebook-compute-free`

---

## 📚 WHICH NOTEBOOK TO RUN FIRST?

### 🥇 **BEST FOR DEMO**: `Interactive_Prediction_Demo.ipynb`
- Beautiful interactive interface
- Real-time predictions
- Visual feedback
- Feature analysis
- **USE THIS FOR YOUR DEFENSE!**

### 🥈 **SECOND**: `Quick_Model_Check.ipynb`
- Fast verification
- Shows model is registered
- Shows experiments
- Quick status check

### 🥉 **THIRD**: `Engagement_Model_Demo.ipynb`
- Detailed model information
- Experiment tracking
- Model registry demo

### 🎯 **ADVANCED**: `Launch_Streamlit_App.ipynb`
- Launches full Streamlit server
- Complete web application
- Requires port forwarding

---

## 🔧 TROUBLESHOOTING

### If compute doesn't appear:
- Refresh the page
- Wait 1-2 minutes for provisioning
- Check "Compute" → "Compute instances" tab

### If notebook won't run:
- Make sure compute is selected (dropdown at top)
- Make sure compute is "Running" (green status)
- Try running cells individually (Shift + Enter)

### If dependencies fail to install:
- Run the first cell again
- Wait for installation to complete
- Check for error messages

### If sliders don't appear:
- Make sure you ran all previous cells
- Check for errors in output
- Try running the cell again

---

## ✅ CHECKLIST

- [x] Compute instance created: `notebook-compute-free`
- [x] Compute is running
- [x] Auto-shutdown enabled (30 min)
- [x] Browser opened to Azure ML Studio
- [ ] Upload notebooks (YOU DO THIS)
- [ ] Select compute in notebook
- [ ] Run `Interactive_Prediction_Demo.ipynb`
- [ ] Interact with sliders
- [ ] Take screenshot for defense

---

## 🎓 FOR YOUR DEFENSE

**Show the professor**:
1. Compute instance in Azure ML Studio
2. Uploaded notebooks
3. Running `Interactive_Prediction_Demo.ipynb`
4. Interactive sliders working
5. Real-time predictions
6. Feature contribution analysis

**This demonstrates**:
- ✅ Azure ML Studio proficiency
- ✅ Compute management
- ✅ Interactive ML development
- ✅ Model deployment
- ✅ Cost-aware cloud usage

---

## 🚀 YOU'RE READY!

**Compute Instance**: ✅ RUNNING  
**Notebooks**: ✅ READY TO UPLOAD  
**Azure ML Studio**: ✅ OPEN  

**Next Step**: Upload `Interactive_Prediction_Demo.ipynb` and run it!

---

**Need help?** The compute instance is ready and waiting for you! 🎉

