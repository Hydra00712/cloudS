# 7️⃣ POWER BI DASHBOARD STRATEGY

## Purpose
Visualize model performance and predictions for academic grading demonstration.

## Data Flow

```
Azure SQL Database (predictions table)
    ↓ (Direct connection)
Power BI Desktop
    ↓ (Visualizations)
Reports & Insights
    ↓ (Export)
PDF for Professor
```

## Setup Steps

### Step 1: Create Predictions Table in Azure SQL

Run this SQL script:

```sql
-- Create table to store all predictions
CREATE TABLE dbo.predictions (
    prediction_id INT PRIMARY KEY IDENTITY(1,1),
    timestamp DATETIME DEFAULT GETDATE(),
    day_of_week NVARCHAR(20),
    platform NVARCHAR(50),
    topic_category NVARCHAR(50),
    emotion_type NVARCHAR(50),
    sentiment_score FLOAT,
    toxicity_score FLOAT,
    predicted_engagement_rate FLOAT,
    engagement_level NVARCHAR(20),
    model_version NVARCHAR(20)
);

-- Create table for model metrics
CREATE TABLE dbo.model_metrics (
    metric_id INT PRIMARY KEY IDENTITY(1,1),
    model_version NVARCHAR(20),
    model_type NVARCHAR(50),
    mae_test FLOAT,
    rmse_test FLOAT,
    r2_test FLOAT,
    created_date DATETIME DEFAULT GETDATE()
);

-- Sample data (for demo before live predictions)
INSERT INTO dbo.model_metrics VALUES
('v1.0', 'XGBoost', 0.085, 0.132, 0.876, GETDATE()),
('v1.0', 'RandomForest', 0.092, 0.145, 0.851, GETDATE()),
('v1.0', 'HistGradientBoosting', 0.098, 0.155, 0.841, GETDATE());
```

### Step 2: Connect Power BI to Azure SQL

1. Open **Power BI Desktop**
2. **Get Data** → **Azure** → **Azure SQL Database**
3. Enter:
   - Server: `sql-engagement-xxxx.database.windows.net`
   - Database: `engagement_db`
   - Username: `sqladmin`
   - Password: `P@ssw0rd123!`
4. Load tables: `predictions`, `model_metrics`

### Step 3: Create Visualizations

#### Dashboard 1: Model Performance

| Visualization | Type | Data |
|---|---|---|
| **Model Comparison Card** | 3-Column Card | MAE, RMSE, R² by model |
| **Accuracy Trend Line** | Line Chart | R² score over time |
| **Error Distribution** | Histogram | MAE distribution |
| **Model Selector Slicer** | Slicer | Filter by model_type |

**Power BI Recipe:**

```
Visualizations Tab → Line Chart
  X-Axis: model_version
  Y-Axis: r2_test
  Legend: model_type
  Title: "Model Performance Over Time"
```

#### Dashboard 2: Predictions Overview

| Visualization | Type | Data |
|---|---|---|
| **Engagement Distribution** | Histogram | Count by engagement_level |
| **Top Platforms** | Bar Chart | Prediction count by platform |
| **Sentiment vs Engagement** | Scatter | sentiment_score vs predicted_engagement |
| **Time Series** | Line | Daily prediction volume |

**Power BI Recipe:**

```
Visualizations Tab → Clustered Bar Chart
  X-Axis: engagement_level
  Y-Axis: COUNT(prediction_id)
  Data Colors: engagement_level
  Title: "Engagement Distribution"
```

#### Dashboard 3: Daily Summary

| Visualization | Type | Data |
|---|---|---|
| **KPI Cards** | Card | Total predictions, Avg engagement |
| **Category Breakdown** | Pie Chart | % LOW / MODERATE / HIGH |
| **Platform Performance** | Table | Platform, Avg engagement, Count |

### Step 4: Export to PDF

**File** → **Export** → **Export to PDF**

Name: `engagement_dashboard.pdf`

---

## Sample Dashboard Layout (Text Representation)

```
┌─────────────────────────────────────────────────────────────────────┐
│          📊 SOCIAL MEDIA ENGAGEMENT ML MODEL DASHBOARD             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │  R² Score   │  │   MAE       │  │   RMSE      │                  │
│  │  0.876      │  │   0.085     │  │   0.132     │                  │
│  │  (XGBoost)  │  │  (Test Set) │  │  (Test Set) │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
│                                                                      │
│  ┌────────────────────────┐  ┌────────────────────────┐             │
│  │ Engagement Distribution│  │  Model Performance     │             │
│  │                        │  │                        │             │
│  │  🔴 LOW:  45%          │  │    R² Score Trend      │             │
│  │  🟡 MOD:  35%          │  │    ░░░░░░░░░░░░░      │             │
│  │  🟢 HIGH: 20%          │  │    0.876  (XGBoost)   │             │
│  │                        │  │    0.851  (RF)        │             │
│  └────────────────────────┘  └────────────────────────┘             │
│                                                                      │
│  ┌────────────────────────┐  ┌────────────────────────┐             │
│  │ Predictions by Platform│  │ Daily Prediction Volume│             │
│  │                        │  │                        │             │
│  │  Twitter:     1,245    │  │    ███████             │             │
│  │  Instagram:   980      │  │    ███████             │             │
│  │  Facebook:    756      │  │    ███████             │             │
│  │  TikTok:      1,523    │  │    ███████             │             │
│  └────────────────────────┘  └────────────────────────┘             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Sentiment Score vs Predicted Engagement (Scatter Plot)      │   │
│  │ • Each dot = prediction                                      │   │
│  │ • X-axis: Sentiment (-1 to +1)                              │   │
│  │ • Y-axis: Engagement (0 to 1)                               │   │
│  │ • Trend: Positive sentiment → Higher engagement             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## What Professor Evaluates

| Criteria | Evidence |
|---|---|
| **Data connectivity** | ✅ Live connection to Azure SQL |
| **Metric accuracy** | ✅ MAE/RMSE/R² match training output |
| **Visualization clarity** | ✅ Clear labeling, color coding |
| **Data governance** | ✅ Timestamp tracking, version info |
| **Business insight** | ✅ Trends, platform comparison |
| **Reproducibility** | ✅ PDF export shows exact metrics |

---

## Automation (Future)

To auto-refresh predictions:

```python
# Function in Azure Functions (timer trigger)
import pymssql
from datetime import datetime

def refresh_predictions(timer):
    """Daily refresh of predictions table"""
    
    # Connect to SQL
    conn = pymssql.connect(
        server='sql-engagement.database.windows.net',
        user='sqladmin',
        password='...',
        database='engagement_db'
    )
    
    cursor = conn.cursor()
    
    # Insert mock prediction (or actual API call)
    cursor.execute("""
        INSERT INTO predictions VALUES (%s, %s, %s, ...)
        VALUES ('%s', '%s', '%s', ...)
    """, (datetime.now(), 'Twitter', ...))
    
    conn.commit()
    conn.close()
```

Then in Power BI: **Refresh** tab → Set schedule to daily.

