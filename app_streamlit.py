"""
Streamlit App: Engagement Rate Prediction
Loads model from Blob, makes predictions
"""

import streamlit as st
import pandas as pd
import pickle
import numpy as np
import os

st.set_page_config(page_title="Engagement Predictor", layout="wide")

st.title("📊 Social Media Engagement Rate Predictor")
st.markdown("""
This app predicts engagement rates using a Gradient Boosting model trained on social media data.
""")

# Load model from Azure Blob Storage
@st.cache_resource
def load_model():
    """Load model from Azure Blob Storage"""
    try:
        from azure.storage.blob import BlobServiceClient
        from azure.identity import DefaultAzureCredential
        import io
        
        # Try loading from Blob first
        try:
            credential = DefaultAzureCredential()
            account_url = "https://stengml707.blob.core.windows.net"
            blob_service = BlobServiceClient(account_url=account_url, credential=credential)
            blob_client = blob_service.get_blob_client(container="models", blob="model_gb.pkl")
            
            model_bytes = blob_client.download_blob().readall()
            model = pickle.loads(model_bytes)
            
            st.success("✅ Model loaded from Azure Blob Storage: models/model_gb.pkl")
            return model
        except:
            # Fallback to local if Blob fails
            with open("models/model_gb.pkl", "rb") as f:
                model = pickle.load(f)
            st.warning("⚠️ Model loaded from local filesystem (fallback)")
            return model
    except Exception as e:
        st.error(f"❌ Could not load model: {e}")
        return None

@st.cache_resource
def load_encoders():
    """Load encoders"""
    try:
        with open("data/processed/encoders.pkl", "rb") as f:
            encoders = pickle.load(f)
        return encoders
    except:
        return {}

# Load assets
model = load_model()
encoders = load_encoders()

if model is None:
    st.error("Model failed to load. Please check deployment.")
    st.stop()

# Sidebar for input
st.sidebar.header("📝 Input Features")

# Create sample input form
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sentiment & Toxicity")
    sentiment_score = st.slider("Sentiment Score", -1.0, 2.0, 0.0, 0.1)
    toxicity_score = st.slider("Toxicity Score", -2.0, 2.0, 0.0, 0.1)
    
    st.subheader("User History")
    past_sentiment = st.slider("Past Sentiment Avg", -0.5, 0.5, 0.0, 0.1)
    engagement_growth = st.slider("Engagement Growth", -2.0, 2.0, 0.0, 0.1)

with col2:
    st.subheader("Engagement Features")
    sentiment_interaction = sentiment_score * toxicity_score
    abs_sentiment = abs(sentiment_score)
    perf_momentum = past_sentiment * engagement_growth
    toxicity_sq = toxicity_score ** 2
    sentiment_sq = sentiment_score ** 2
    
    st.metric("Sentiment-Toxicity Interaction", f"{sentiment_interaction:.4f}")
    st.metric("Absolute Sentiment", f"{abs_sentiment:.4f}")
    st.metric("Perf Momentum", f"{perf_momentum:.4f}")
    st.metric("Toxicity Squared", f"{toxicity_sq:.4f}")
    st.metric("Sentiment Squared", f"{sentiment_sq:.4f}")

# Create feature vector for prediction
feature_names = [
    'day_of_week_encoded', 'platform_encoded', 'topic_category_encoded',
    'emotion_type_encoded', 'location_encoded', 'language_encoded',
    'sentiment_bucket_encoded', 'toxicity_bucket_encoded',
    'past_perf_bucket_encoded', 'growth_bucket_encoded',
    'sentiment_score', 'toxicity_score', 'user_past_sentiment_avg',
    'user_engagement_growth', 'sentiment_bucket', 'toxicity_bucket',
    'past_perf_bucket', 'growth_bucket', 'sentiment_toxicity_interaction',
    'abs_sentiment', 'perf_momentum', 'toxicity_squared', 'sentiment_squared'
]

# Sample feature vector (in real app, would be dynamic input)
sample_vector = np.array([
    1, 1, 2, 1, 15, 7,  # Encoded categoricals (day_of_week, platform, topic, emotion, location, language)
    0, 0, 2, 0,  # Buckets
    sentiment_score, toxicity_score, past_sentiment, engagement_growth,
    0, 0, 2, 0,  # Bucket integer values
    sentiment_interaction, abs_sentiment, perf_momentum, toxicity_sq, sentiment_sq
])

# Make prediction
if st.button("🔮 Predict Engagement Rate"):
    try:
        prediction = model.predict([sample_vector])[0]
        
        # Display prediction
        st.success(f"### Predicted Engagement Rate: **{prediction:.4f}**")
        
        # Categorize
        if prediction < 0.05:
            category = "🔴 Very Low"
        elif prediction < 0.1:
            category = "🟠 Low"
        elif prediction < 0.15:
            category = "🟡 Medium"
        elif prediction < 0.3:
            category = "🟢 High"
        else:
            category = "🟣 Very High"
        
        st.info(f"**Category: {category}**")
        
        # Show model performance metrics
        st.subheader("📊 Model Performance (Test Set)")
        col1, col2, col3 = st.columns(3)
        col1.metric("MAE", "0.3500")
        col2.metric("RMSE", "1.1642")
        col3.metric("R²", "-0.0727")
        
    except Exception as e:
        st.error(f"Prediction error: {e}")

st.markdown("""
---
**Model Details:**
- Algorithm: Gradient Boosting Regressor
- Features: 23 (encoded, normalized, engineered)
- Training Data: 12,000 social media posts
- Target: Engagement Rate (continuous)
""")
