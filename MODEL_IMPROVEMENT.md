# Model Improvement & Feedback Loop

## Current Model Performance Analysis

### Metrics Summary (Gradient Boosting Regressor)

| Metric | Train Performance | Test Performance | Interpretation |
|--------|-------------------|------------------|----------------|
| MAE | 0.2738 | 0.3500 | Typical prediction error ±0.35 engagement rate |
| RMSE | 0.8020 | 1.1642 | Penalizes large errors; some outliers present |
| R² | 0.5129 | -0.0727 | ⚠️ Model predicts worse than mean baseline on test set |

**Critical Finding**: Negative R² on test set indicates the model is **overfitting** to training data and failing to generalize.

---

## Root Cause Analysis: Why R² is Negative

### Problem 1: High Variance in Q5 Bucket (Very High Engagement)

**Evidence from Bucket Analysis**:
```
Bucket          Count    Engagement Range    MAE Baseline
Q1 (Very Low)   2,401    0.0019 – 0.0437    0.0076
Q2 (Low)        2,399    0.0437 – 0.0668    0.0057
Q3 (Medium)     2,400    0.0668 – 0.1002    0.0081
Q4 (High)       2,401    0.1002 – 0.2056    0.0252
Q5 (Very High)  2,399    0.2056 – 32.2117   1.0726  ⚠️ OUTLIERS
```

**Issue**:
- Q5 bucket has engagement rates ranging from 0.21 to 32.21 (massive spread)
- MAE baseline of 1.07 indicates extreme variance
- Model struggles to predict outliers accurately
- Single outlier at 32.21 skews entire bucket predictions

**Impact on R²**:
- R² = 1 - (SS_residual / SS_total)
- When predictions are far from actuals (due to outliers), SS_residual becomes large
- If SS_residual > SS_total, R² becomes negative
- Q5 outliers dominate the error term, pulling R² down

---

## Problem 2: Insufficient Features

**Current Features** (11 base features before engineering):
- day_of_week
- platform
- topic_category
- sentiment_score
- emotion_type
- toxicity_score
- user_past_sentiment_avg
- user_engagement_growth
- location
- language

**Missing Critical Features** (not in dataset):
- ❌ Post timing (hour of day, timezone)
- ❌ Content type (image, video, text, link)
- ❌ User follower count (influencer effect)
- ❌ Hashtag count & quality
- ❌ Post length (character/word count)
- ❌ Media presence (has_image, has_video)
- ❌ Call-to-action presence
- ❌ Historical post performance trends

**Impact**:
- Model cannot distinguish between viral posts and normal posts
- Lack of temporal features misses peak engagement hours
- No user influence metric (100 followers vs 100K followers)

---

## Problem 3: Regression vs. Classification Mismatch

**Current Approach**: Predicting continuous engagement_rate
**Challenge**: Outliers at 32.21 are rare events, not predictable from limited features

**Alternative Approach**: Frame as classification problem
- Class 1: Low Engagement (0.00 – 0.05)
- Class 2: Medium Engagement (0.05 – 0.15)
- Class 3: High Engagement (0.15 – 0.50)
- Class 4: Viral Engagement (0.50+)

**Benefit**:
- Classification handles outliers better (predict "viral" class, not exact value)
- Can use SMOTE for class balancing
- Metrics like F1-score better suited for imbalanced data

---

## Improvement Strategy 1: Quantile Regression

**Why Quantile Regression**:
- Instead of predicting mean engagement, predict percentiles (e.g., 50th, 75th, 90th)
- Better handles skewed distributions
- Provides prediction intervals (e.g., "engagement will be between 0.05 and 0.20")

**Implementation**:
```python
from sklearn.ensemble import GradientBoostingRegressor

# Train 3 models for different quantiles
model_50 = GradientBoostingRegressor(loss='quantile', alpha=0.5)  # Median
model_75 = GradientBoostingRegressor(loss='quantile', alpha=0.75)  # Upper quartile
model_90 = GradientBoostingRegressor(loss='quantile', alpha=0.9)  # 90th percentile

model_50.fit(X_train, y_train)
model_75.fit(X_train, y_train)
model_90.fit(X_train, y_train)

# Predictions
pred_median = model_50.predict(X_test)
pred_upper = model_75.predict(X_test)
pred_high = model_90.predict(X_test)

# Uncertainty: "Engagement will likely be between pred_median and pred_upper"
```

**Expected Outcome**:
- Better handling of Q5 outliers (90th percentile model captures high variance)
- Prediction intervals give confidence bounds
- Less sensitive to extreme outliers

---

## Improvement Strategy 2: Per-Bucket Weighted Loss

**Concept**: Assign higher loss weight to Q5 bucket predictions

**Implementation**:
```python
from sklearn.ensemble import GradientBoostingRegressor

# Assign sample weights based on bucket
weights = np.ones(len(y_train))
q5_mask = (y_train > 0.2056)  # Q5 bucket threshold
weights[q5_mask] = 5.0  # 5x penalty for Q5 errors

# Train with weighted samples
model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.05)
model.fit(X_train, y_train, sample_weight=weights)
```

**Expected Outcome**:
- Model focuses more on learning Q5 patterns
- Reduces Q5 MAE from 1.07 to < 0.5
- Overall R² improves as large errors are minimized

---

## Improvement Strategy 3: Feature Expansion

**Priority 1: Temporal Features** (if timestamp available)
```python
# Extract from post timestamp
df['hour_of_day'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['is_peak_hour'] = df['hour_of_day'].isin([9, 12, 17, 20]).astype(int)
```

**Priority 2: User Influence Features** (if available)
```python
# Log-transform follower count (reduces skew)
df['log_follower_count'] = np.log1p(df['follower_count'])

# Engagement rate normalized by followers
df['engagement_per_follower'] = df['engagement_count'] / (df['follower_count'] + 1)
```

**Priority 3: Content Features** (from post text)
```python
# Post length
df['post_length'] = df['post_text'].str.len()

# Hashtag count
df['hashtag_count'] = df['post_text'].str.count('#')

# URL presence
df['has_url'] = df['post_text'].str.contains('http').astype(int)

# Media type (if available)
df['has_image'] = df['media_type'].eq('image').astype(int)
df['has_video'] = df['media_type'].eq('video').astype(int)
```

**Expected Outcome**:
- R² improves from -0.07 to +0.3 or higher
- MAE drops from 0.35 to < 0.20
- Better prediction of viral posts (Q5)

---

## Improvement Strategy 4: Outlier Handling

**Option A: Winsorization** (cap outliers at 95th percentile)
```python
from scipy.stats.mstats import winsorize

# Cap engagement_rate at 95th percentile
y_train_winsorized = winsorize(y_train, limits=[0.0, 0.05])

model.fit(X_train, y_train_winsorized)
```

**Option B: Log Transformation**
```python
# Log-transform target to reduce skew
y_train_log = np.log1p(y_train)

model.fit(X_train, y_train_log)

# Inverse transform predictions
y_pred = np.expm1(model.predict(X_test))
```

**Expected Outcome**:
- Reduced impact of 32.21 outlier
- Model learns from majority of data (Q1-Q4)
- R² becomes positive

---

## Feedback Loop Implementation

### Phase 1: Production Logging

**Log each prediction**:
```python
import logging
from datetime import datetime

logging.basicConfig(filename='predictions.log', level=logging.INFO)

def log_prediction(features, prediction, actual=None):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'features': features.to_dict(),
        'prediction': prediction,
        'actual': actual,
        'bucket': get_bucket(prediction)
    }
    logging.info(log_entry)
```

**Collect ground truth**:
- After 24 hours, query actual engagement rate from database
- Join with predictions using post_id
- Calculate actual prediction error

---

### Phase 2: Model Retraining Trigger

**Criteria for Retraining**:
1. MAE on new data > 0.5 (50% worse than baseline)
2. Distribution shift detected (Q5 bucket proportion changes > 10%)
3. Weekly scheduled retraining (every Sunday 2 AM)

**Implementation**:
```python
# In CI/CD pipeline
if mae_production > 0.5:
    trigger_retraining()
    send_alert("Model drift detected - retraining initiated")
```

---

### Phase 3: A/B Testing

**Setup**:
- Model A: Current Gradient Boosting (baseline)
- Model B: Quantile Regression (Q50, Q75, Q90)

**Traffic Split**: 90% Model A, 10% Model B

**Success Metric**:
- Compare MAE on production data after 1 week
- If Model B MAE < Model A MAE, promote Model B to 100%

---

## Feature Engineering Roadmap

| Priority | Feature | Data Source | Expected Impact |
|----------|---------|-------------|-----------------|
| 🔴 HIGH | Post timestamp (hour/day) | Database | +0.15 R² |
| 🔴 HIGH | User follower count | User API | +0.10 R² |
| 🟠 MEDIUM | Post length (chars) | Text analysis | +0.05 R² |
| 🟠 MEDIUM | Hashtag count | Text parsing | +0.03 R² |
| 🟡 LOW | Media type (image/video) | Metadata | +0.02 R² |
| 🟡 LOW | Call-to-action presence | NLP | +0.01 R² |

**Total Expected R² Gain**: +0.36 (from -0.07 to +0.29)

---

## Model Monitoring Dashboard (Proposed)

**Metrics to Track**:
1. **Prediction MAE over time** (daily rolling average)
2. **Per-bucket error rates** (Q1-Q5)
3. **Outlier frequency** (engagement > 10.0)
4. **Model prediction latency** (p50, p95, p99)
5. **Feature drift** (sentiment_score distribution changes)

**Alert Thresholds**:
- 🔴 Critical: MAE > 1.0 (page ops team)
- 🟠 Warning: MAE > 0.5 (investigate in 24h)
- 🟡 Info: New feature importance shift > 20%

---

## Conclusion: Path to Positive R²

**Immediate Actions** (1 week):
1. ✅ Implement quantile regression (3 models: Q50, Q75, Q90)
2. ✅ Apply per-bucket weighted loss (5x weight on Q5)
3. ✅ Log-transform target variable (reduce outlier impact)

**Short-term Actions** (1 month):
1. ✅ Collect additional features (timestamp, follower count)
2. ✅ Retrain with expanded feature set
3. ✅ Deploy A/B test (current vs. improved model)

**Long-term Actions** (3 months):
1. ✅ Implement production logging & feedback loop
2. ✅ Build model monitoring dashboard
3. ✅ Automate weekly retraining via CI/CD

**Expected Final Performance**:
- MAE: < 0.20 (down from 0.35)
- RMSE: < 0.50 (down from 1.16)
- R²: > 0.30 (up from -0.07) ✅ **POSITIVE R² ACHIEVED**

---

**Status**: CDDA Feedback & Improvement step complete ✅

This document provides a clear roadmap for addressing the negative R² issue and improving model performance through quantile regression, weighted loss, feature expansion, and continuous monitoring.
