"""
Generate predictions.csv for Power BI Dashboard
"""

import pandas as pd
import pickle
import numpy as np

print("📊 Generating predictions.csv for Power BI...")

# Load model and data
with open("models/model_gb.pkl", "rb") as f:
    model = pickle.load(f)

df = pd.read_csv("data/processed/cleaned_data.csv")

# Split features and target
X = df.drop('engagement_rate', axis=1)
y_actual = df['engagement_rate']

# Generate predictions
y_pred = model.predict(X)

# Calculate errors
errors = np.abs(y_actual - y_pred)
squared_errors = (y_actual - y_pred) ** 2

# Create quantile buckets
quantiles = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
bucket_labels = ['Q1_Very_Low', 'Q2_Low', 'Q3_Medium', 'Q4_High', 'Q5_Very_High']
buckets = pd.qcut(y_actual, q=quantiles, labels=bucket_labels, duplicates='drop')

# Create predictions dataframe
predictions_df = pd.DataFrame({
    'id': range(len(y_actual)),
    'actual_engagement': y_actual,
    'predicted_engagement': y_pred,
    'absolute_error': errors,
    'squared_error': squared_errors,
    'engagement_bucket': buckets,
    'prediction_category': pd.cut(y_pred, bins=[0, 0.05, 0.1, 0.15, 0.3, 100], 
                                   labels=['Very_Low', 'Low', 'Medium', 'High', 'Very_High'])
})

# Add metrics summary
mae = errors.mean()
rmse = np.sqrt(squared_errors.mean())
r2 = 1 - (squared_errors.sum() / ((y_actual - y_actual.mean()) ** 2).sum())

print(f"\n📈 Model Performance:")
print(f"   MAE: {mae:.4f}")
print(f"   RMSE: {rmse:.4f}")
print(f"   R²: {r2:.4f}")

# Save predictions
predictions_df.to_csv("data/processed/predictions.csv", index=False)
print(f"\n✅ Saved predictions.csv ({len(predictions_df)} rows)")

# Generate summary stats for Power BI
bucket_stats = predictions_df.groupby('engagement_bucket').agg({
    'actual_engagement': ['count', 'mean', 'min', 'max'],
    'absolute_error': 'mean'
}).reset_index()

bucket_stats.columns = ['bucket', 'count', 'avg_engagement', 'min_engagement', 'max_engagement', 'mae']
bucket_stats.to_csv("data/processed/bucket_summary.csv", index=False)
print(f"✅ Saved bucket_summary.csv ({len(bucket_stats)} buckets)")

print("\n📊 Files ready for Power BI:")
print("   - predictions.csv")
print("   - bucket_summary.csv")
