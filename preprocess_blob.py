"""
BLOB-ENABLED DATA PREPROCESSING
Reads from Azure Blob raw-data/raw.csv
Writes to Azure Blob cleaned-data/{cleaned_data.csv, encoders.pkl, bucket_mae.csv}
Feature logic unchanged from preprocess_clean.py
"""

import pandas as pd
import numpy as np
import pickle
import io
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

# Azure config
STORAGE_ACCOUNT = "stengml707"
ACCOUNT_URL = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"
CONTAINER_RAW = "raw-data"
CONTAINER_CLEAN = "cleaned-data"
RAW_BLOB_NAME = "raw.csv"

def get_blob_client():
    """Create blob service client using DefaultAzureCredential"""
    credential = DefaultAzureCredential()
    return BlobServiceClient(account_url=ACCOUNT_URL, credential=credential)

def load_data_from_blob():
    """Load dataset from Azure Blob raw-data/raw.csv"""
    print("📂 Loading dataset from Azure Blob...")
    client = get_blob_client()
    blob_client = client.get_blob_client(container=CONTAINER_RAW, blob=RAW_BLOB_NAME)
    
    data = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(data))
    print(f"✅ Loaded from Blob: {len(df)} rows, {len(df.columns)} columns")
    return df

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

def select_features(df):
    """Keep only pre-posting features (data known BEFORE publishing)."""
    print("\n📋 Selecting pre-posting features...")
    
    features = [
        'day_of_week', 'platform', 'topic_category', 'sentiment_score',
        'emotion_type', 'toxicity_score', 'user_past_sentiment_avg',
        'user_engagement_growth', 'location', 'language', 'engagement_rate'
    ]
    
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

    bucket_specs = {
        'sentiment_bucket': (df['sentiment_score'], [-0.4, -0.1, 0.1, 0.4]),
        'toxicity_bucket': (df['toxicity_score'], [0.2, 0.4, 0.6, 0.8]),
        'past_perf_bucket': (df['user_past_sentiment_avg'], [-0.2, 0.0, 0.2, 0.5]),
        'growth_bucket': (df['user_engagement_growth'], [-0.2, 0.0, 0.2, 0.5])
    }
    
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
    
    df = df.dropna(thresh=len(df.columns) * 0.7)
    
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].median())

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
    engineered = [c for c in ['sentiment_bucket', 'toxicity_bucket', 'past_perf_bucket', 'growth_bucket'] if c in df.columns]
    interactions = [c for c in df.columns if c in ['sentiment_toxicity_interaction', 'abs_sentiment', 'perf_momentum', 'toxicity_squared', 'sentiment_squared']]
    
    final_cols = encoded + numerical + engineered + interactions + ['engagement_rate']
    df = df[final_cols].copy()
    
    print(f"✅ Final shape: {df.shape}")
    return df

def compute_regression_buckets(df_original, df_prepared):
    """
    For REGRESSION: Compute engagement_rate quantile buckets + MAE per bucket
    This addresses CDDA Data Balancing for regression (not oversampling)
    """
    print("\n📊 Computing regression buckets and per-bucket MAE...")
    
    # Create quantile buckets on ORIGINAL engagement rates
    engagement = df_original['engagement_rate']
    quantiles = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    bucket_labels = ['Q1_Very_Low', 'Q2_Low', 'Q3_Medium', 'Q4_High', 'Q5_Very_High']
    
    df_original['engagement_bucket'] = pd.qcut(engagement, q=quantiles, labels=bucket_labels, duplicates='drop')
    
    # For each bucket, compute theoretical MAE (using group means as pseudo-predictions)
    bucket_stats = []
    for bucket in df_original['engagement_bucket'].unique():
        mask = df_original['engagement_bucket'] == bucket
        bucket_engagement = engagement[mask]
        
        # Mean of bucket as baseline prediction
        bucket_mean = bucket_engagement.mean()
        bucket_mae = mean_absolute_error(bucket_engagement, [bucket_mean] * len(bucket_engagement))
        
        bucket_stats.append({
            'bucket': bucket,
            'count': mask.sum(),
            'engagement_min': bucket_engagement.min(),
            'engagement_max': bucket_engagement.max(),
            'engagement_mean': bucket_mean,
            'mae_baseline': bucket_mae
        })
    
    bucket_df = pd.DataFrame(bucket_stats)
    
    print("\n📈 Regression Bucket Statistics:")
    print(bucket_df.to_string(index=False))
    
    return bucket_df

def upload_to_blob(data_bytes, container, blob_name):
    """Upload bytes to Azure Blob"""
    client = get_blob_client()
    blob_client = client.get_blob_client(container=container, blob=blob_name)
    blob_client.upload_blob(data_bytes, overwrite=True)
    print(f"✅ Uploaded to {container}/{blob_name}")

def preprocess_with_balancing():
    """Full pipeline: load → clean → encode → prepare → bucket → upload to Blob"""
    print("\n" + "="*70)
    print("🔧 BLOB-ENABLED DATA PREPROCESSING + REGRESSION BALANCING")
    print("="*70)
    
    # Load from Blob
    df = load_data_from_blob()
    
    # Store original for bucket computation
    df_original = df.copy()
    
    # Preprocessing
    df = select_features(df)
    df = clean_data(df)
    df['topic_category'] = df['topic_category'].apply(expand_topic_category)
    df = add_feature_buckets(df)
    df = add_interaction_features(df)
    df, encoders, scaler = encode_and_normalize(df)
    df_ml = prepare_for_ml(df)
    
    # Compute regression buckets + MAE per bucket
    bucket_df = compute_regression_buckets(df_original, df_ml)
    
    # Upload to Blob
    print("\n📤 Uploading to Azure Blob...")
    
    # Upload cleaned_data.csv
    csv_buffer = io.BytesIO()
    df_ml.to_csv(csv_buffer, index=False)
    upload_to_blob(csv_buffer.getvalue(), CONTAINER_CLEAN, "cleaned_data.csv")
    
    # Upload encoders.pkl
    enc_buffer = io.BytesIO()
    pickle.dump(encoders, enc_buffer)
    upload_to_blob(enc_buffer.getvalue(), CONTAINER_CLEAN, "encoders.pkl")
    
    # Upload bucket_mae.csv
    bucket_buffer = io.BytesIO()
    bucket_df.to_csv(bucket_buffer, index=False)
    upload_to_blob(bucket_buffer.getvalue(), CONTAINER_CLEAN, "bucket_mae.csv")
    
    print("\n✅ PREPROCESSING + BALANCING COMPLETE!")
    print(f"   Cleaned data shape: {df_ml.shape}")
    print(f"   Buckets: {len(bucket_df)}")
    
    return df_ml, encoders, scaler, bucket_df

if __name__ == "__main__":
    df_ml, enc, scaler, buckets = preprocess_with_balancing()
