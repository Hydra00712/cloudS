"""
DATA PREPROCESSING - Simple & Clean
Load → Clean → Encode → Prepare features for ML
"""

import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle

OUTPUT_DIR = "data/processed"


def expand_topic_category(raw: str) -> str:
    """Map coarse topic labels to a richer set of categories."""
    if not isinstance(raw, str):
        return "general"
    text = raw.lower()

    rules = [
        ("technology", ["tech", "ai", "software", "product", "saas", "cloud", "data"]),
        ("marketing", ["marketing", "brand", "ad", "campaign", "social", "content"]),
        ("education", ["learn", "course", "study", "tutorial", "guide", "lesson"]),
        ("business", ["business", "revenue", "sales", "clients", "startup", "founder", "b2b", "b2c"]),
        ("finance", ["finance", "invest", "investment", "crypto", "stock", "bank", "budget"]),
        ("health", ["health", "medical", "wellbeing", "wellness", "mental", "fitness", "care"]),
        ("lifestyle", ["lifestyle", "travel", "food", "life", "family", "home"]),
        ("entertainment", ["entertainment", "movie", "film", "music", "show", "game", "gaming"]),
        ("sports", ["sports", "football", "soccer", "basketball", "tennis", "run", "workout"]),
        ("news", ["news", "update", "breaking", "trending", "headline"]),
        ("career", ["career", "job", "hiring", "interview", "resume", "cv", "promotion"]),
        ("productivity", ["productivity", "workflow", "automation", "process", "time management"]),
        ("design", ["design", "ux", "ui", "graphic", "creative"]),
        ("engineering", ["engineering", "code", "developer", "dev", "program", "build"]),
        ("motivation", ["motivation", "inspiration", "mindset", "success", "discipline"]),
    ]

    for label, keywords in rules:
        if any(k in text for k in keywords):
            return label

    return text if text else "general"


def load_data(filepath):
    """Load dataset from CSV."""
    print("📂 Loading dataset...")
    df = pd.read_csv(filepath)
    print(f"✅ Loaded: {len(df)} rows, {len(df.columns)} columns")
    return df


def select_features(df):
    """Keep only pre-posting features (data known BEFORE publishing)."""
    print("\n📋 Selecting pre-posting features...")
    
    features = [
        'day_of_week', 'platform', 'topic_category', 'sentiment_score',
        'emotion_type', 'toxicity_score', 'user_past_sentiment_avg',
        'user_engagement_growth', 'location', 'language', 'engagement_rate'  # target
    ]
    
    # Filter to available columns
    features = [f for f in features if f in df.columns]
    df = df[features].copy()
    
    print(f"✅ Selected {len(features)-1} features + 1 target")
    return df


def add_feature_buckets(df):
    """Add coarse buckets to help tree/boosting models capture non-linearities."""
    def bucketize(val, cuts):
        for i, c in enumerate(cuts):
            if val <= c:
                return i
        return len(cuts)

    # Bucket definitions (feature, thresholds)
    bucket_specs = {
        'sentiment_bucket': (df['sentiment_score'], [-0.4, -0.1, 0.1, 0.4]),
        'toxicity_bucket': (df['toxicity_score'], [0.2, 0.4, 0.6, 0.8]),
        'past_perf_bucket': (df['user_past_sentiment_avg'], [-0.2, 0.0, 0.2, 0.5]),
        'growth_bucket': (df['user_engagement_growth'], [-0.2, 0.0, 0.2, 0.5])
    }
    
    # Apply bucketing efficiently
    for col_name, (series, cuts) in bucket_specs.items():
        df[col_name] = series.apply(lambda v: bucketize(v, cuts))
    
    return df


def add_interaction_features(df):
    """Engineer interaction and transformed features for better predictive power."""
    interactions = {
        'sentiment_toxicity_interaction': lambda: df['sentiment_score'] * df['toxicity_score'],
        'abs_sentiment': lambda: df['sentiment_score'].abs(),
        'perf_momentum': lambda: df['user_past_sentiment_avg'] * df['user_engagement_growth'],
        'toxicity_squared': lambda: df['toxicity_score'] ** 2,
        'sentiment_squared': lambda: df['sentiment_score'] ** 2
    }
    
    for col_name, calc in interactions.items():
        df[col_name] = calc()
    
    return df


def clean_data(df):
    """Remove missing values and fill remaining ones."""
    print("\n🔍 Cleaning data...")
    
    # Drop rows with >30% missing
    df = df.dropna(thresh=len(df.columns) * 0.7)
    
    # Fill numerical with median (avoid chained assignment warnings)
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].median())

    # Fill categorical with mode
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].mode()[0])
    
    print(f"✅ Missing values: {df.isnull().sum().sum()}")
    return df


def encode_and_normalize(df):
    """Encode categoricals and normalize numericals."""
    print("\n🔢 Encoding categorical features...")
    
    encoders = {}
    categorical_cols = [c for c in df.columns 
                       if df[c].dtype == 'object' and c != 'engagement_rate']
    categorical_cols += [c for c in ['sentiment_bucket', 'toxicity_bucket', 'past_perf_bucket', 'growth_bucket'] if c in df.columns]
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    
    print(f"✅ Encoded {len(categorical_cols)} categorical features")
    
    print("\n📏 Normalizing numerical features...")
    numerical_cols = ['sentiment_score', 'toxicity_score',
                     'user_past_sentiment_avg', 'user_engagement_growth']
    numerical_cols = [c for c in numerical_cols if c in df.columns]
    
    scaler = StandardScaler()
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
    
    print(f"✅ Normalized {len(numerical_cols)} numerical features")
    
    return df, encoders, scaler


def prepare_for_ml(df):
    """Keep only encoded + normalized features + target."""
    print("\n🎯 Preparing for ML...")
    
    encoded = [c for c in df.columns if c.endswith('_encoded')]
    numerical = ['sentiment_score', 'toxicity_score',
                'user_past_sentiment_avg', 'user_engagement_growth']
    numerical = [c for c in numerical if c in df.columns]
    # Keep engineered buckets too
    engineered = [c for c in ['sentiment_bucket', 'toxicity_bucket', 'past_perf_bucket', 'growth_bucket'] if c in df.columns]
    # Keep interaction features (these are already normalized)
    interactions = [c for c in df.columns if c in ['sentiment_toxicity_interaction', 'abs_sentiment', 'perf_momentum', 'toxicity_squared', 'sentiment_squared']]
    
    final_cols = encoded + numerical + engineered + interactions + ['engagement_rate']
    df = df[final_cols].copy()
    
    print(f"✅ Final shape: {df.shape}")
    return df


def preprocess(input_file="archive (1)/Social Media Engagement Dataset.csv"):
    """
    Complete preprocessing pipeline:
    1. Load data
    2. Select pre-posting features
    3. Clean missing values
    4. Encode categoricals
    5. Normalize numericals
    6. Prepare for ML
    """
    print("\n" + "="*60)
    print("🔧 DATA PREPROCESSING")
    print("="*60)
    
    df = load_data(input_file)
    df = select_features(df)
    df = clean_data(df)
    # Enrich topic granularity before encoding
    df['topic_category'] = df['topic_category'].apply(expand_topic_category)
    df = add_feature_buckets(df)
    df = add_interaction_features(df)
    df, encoders, scaler = encode_and_normalize(df)
    df = prepare_for_ml(df)
    
    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(f"{OUTPUT_DIR}/cleaned_data.csv", index=False)
    
    with open(f"{OUTPUT_DIR}/encoders.pkl", 'wb') as f:
        pickle.dump(encoders, f)
    
    print(f"\n💾 Saved: {OUTPUT_DIR}/cleaned_data.csv")
    print(f"💾 Saved: {OUTPUT_DIR}/encoders.pkl")
    print("\n✅ PREPROCESSING COMPLETE!")
    
    return df, encoders, scaler


if __name__ == "__main__":
    df, enc, scaler = preprocess()
