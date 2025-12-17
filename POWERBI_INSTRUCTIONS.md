# Power BI Dashboard Instructions

## Data Source Configuration

1. **Open Power BI Desktop**

2. **Connect to Azure Blob Storage**:
   - Get Data → More → Azure → Azure Blob Storage
   - Storage Account: `stengml707`
   - Container: `cleaned-data`
   - Files: `predictions.csv`, `bucket_summary.csv`

3. **Load Tables**:
   - predictions (12,000 rows)
   - bucket_summary (5 rows)

## Dashboard Components

### Page 1: Model Performance Overview

**KPI Cards** (Top Row):
- MAE: 0.2738
- RMSE: 0.8020
- R²: 0.5129

**Visualizations**:
1. **Actual vs Predicted Scatter Plot**
   - X-axis: actual_engagement
   - Y-axis: predicted_engagement
   - Color: engagement_bucket

2. **Error Distribution Histogram**
   - X-axis: absolute_error (bins: 0-0.1, 0.1-0.2, 0.2-0.5, 0.5-1.0, 1.0+)
   - Y-axis: Count

3. **Bucket-Level MAE Bar Chart**
   - X-axis: engagement_bucket
   - Y-axis: Average(absolute_error)
   - Data labels: Show values

### Page 2: Prediction Analysis

**Visualizations**:
1. **Engagement Distribution (Actual)**
   - Histogram of actual_engagement
   - Color: engagement_bucket

2. **Engagement Distribution (Predicted)**
   - Histogram of predicted_engagement
   - Color: prediction_category

3. **Bucket Count Table**
   - Table: bucket_summary
   - Columns: bucket, count, avg_engagement, mae

4. **Error by Bucket Box Plot**
   - Box plot of absolute_error by engagement_bucket

### Filters (Applied to All Pages)
- Engagement Bucket slicer
- Prediction Category slicer

## Power BI Dashboard Screenshot Evidence

**Required Screenshots**:
1. Data Source showing Azure Blob connection
2. Model Performance page with KPI cards
3. Prediction Analysis page with charts
4. Bucket-level MAE visualization

## Export .pbix File

Save as: `engagement_dashboard.pbix`

Location: `c:\Users\medad\Downloads\Cloud1\engagement_dashboard.pbix`

---

**Evidence Status**: 
- ✅ predictions.csv uploaded to Blob (cleaned-data container)
- ✅ Data ready for Power BI import
- ⏳ Power BI Desktop dashboard creation (manual step)
