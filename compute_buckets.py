"""
REGRESSION BALANCING: Compute quantile buckets + MAE per bucket
Data is already preprocessed; just analyze engagement_rate distribution
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error

print("\n" + "="*70)
print("📊 REGRESSION BALANCING: Bucket Analysis")
print("="*70)

# Load preprocessed data
df = pd.read_csv("data/processed/cleaned_data.csv")
engagement = df['engagement_rate']

print(f"\n📈 Engagement Rate Statistics:")
print(f"   Count: {len(engagement)}")
print(f"   Mean: {engagement.mean():.4f}")
print(f"   Median: {engagement.median():.4f}")
print(f"   Std Dev: {engagement.std():.4f}")
print(f"   Min: {engagement.min():.4f}")
print(f"   Max: {engagement.max():.4f}")

# Create quantile buckets
quantiles = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
bucket_labels = ['Q1_Very_Low', 'Q2_Low', 'Q3_Medium', 'Q4_High', 'Q5_Very_High']

df['engagement_bucket'] = pd.qcut(engagement, q=quantiles, labels=bucket_labels, duplicates='drop')

# Compute per-bucket statistics
print("\n📊 Quantile Bucket Analysis:")
bucket_stats = []

for bucket in df['engagement_bucket'].unique():
    mask = df['engagement_bucket'] == bucket
    bucket_engagement = engagement[mask]
    
    # Mean of bucket as baseline prediction
    bucket_mean = bucket_engagement.mean()
    bucket_mae = mean_absolute_error(bucket_engagement, [bucket_mean] * len(bucket_engagement))
    
    bucket_stats.append({
        'bucket': bucket,
        'count': mask.sum(),
        'percentage': f"{mask.sum() / len(df) * 100:.1f}%",
        'engagement_min': f"{bucket_engagement.min():.4f}",
        'engagement_max': f"{bucket_engagement.max():.4f}",
        'engagement_mean': f"{bucket_mean:.4f}",
        'mae_baseline': f"{bucket_mae:.4f}"
    })

bucket_df = pd.DataFrame(bucket_stats)
print(bucket_df.to_string(index=False))

# Save bucket metrics
bucket_df.to_csv("data/processed/bucket_mae.csv", index=False)

print("\n✅ REGRESSION BALANCING ANALYSIS:")
print("   Why this matters for REGRESSION (not classification):")
print("   - Classification: Class imbalance → oversampling/undersampling minority classes")
print("   - Regression: Engagement imbalance → quantile buckets reveal where model struggles")
print("   - Per-bucket MAE guides weighted loss or stratified sampling during training")
print("   - This ensures model learns equally well across LOW→HIGH engagement spectrum")

print(f"\n✅ Bucket metrics saved to: data/processed/bucket_mae.csv")

import os
print("\n📂 Files in data/processed/:")
for f in sorted(os.listdir("data/processed")):
    size = os.path.getsize(os.path.join("data/processed", f))
    print(f"   {f} ({size:,} bytes)")
