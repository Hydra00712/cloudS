"""
Cloud-Enabled Streamlit App
Can load model from Azure Blob Storage or local file
"""

import streamlit as st
import pandas as pd
import pickle
import os
from datetime import datetime

# Try to import Azure libraries
try:
    from azure.storage.blob import BlobServiceClient
    from azure_config import (
        STORAGE_ACCOUNT_NAME,
        CONTAINER_MODELS,
        get_storage_account_key
    )
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

def load_model_from_azure():
    """Load model from Azure Blob Storage"""
    if not AZURE_AVAILABLE:
        return None
    
    try:
        print("📥 Loading model from Azure Blob Storage...")
        
        # Get storage account key
        account_key = get_storage_account_key()
        if not account_key:
            return None
        
        # Create connection string
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={STORAGE_ACCOUNT_NAME};"
            f"AccountKey={account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        
        # Download model
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_MODELS,
            blob="model.pkl"
        )
        
        model_data = blob_client.download_blob().readall()
        model = pickle.loads(model_data)
        
        print("✅ Model loaded from Azure")
        return model
        
    except Exception as e:
        print(f"⚠️  Could not load from Azure: {e}")
        return None

def load_model_local():
    """Load model from local file"""
    model_path = "models/model.pkl"
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    return None

@st.cache_resource
def load_model():
    """Load model from Azure or local file"""
    # Try Azure first
    if AZURE_AVAILABLE:
        model = load_model_from_azure()
        if model is not None:
            return model, "Azure Blob Storage"
    
    # Fall back to local
    model = load_model_local()
    if model is not None:
        return model, "Local File"
    
    return None, None

# Page config
st.set_page_config(
    page_title="Social Media Engagement Predictor",
    page_icon="📱",
    layout="wide"
)

# Title
st.title("📱 Social Media Engagement Predictor")
st.markdown("---")

# Load model
model, source = load_model()

if model is None:
    st.error("❌ Could not load model. Please train the model first.")
    st.stop()

# Display model source
st.sidebar.success(f"✅ Model loaded from: {source}")

# Sidebar - Input features
st.sidebar.header("📊 Post Features")

# Platform
platform = st.sidebar.selectbox(
    "Platform",
    ["Instagram", "Twitter", "Facebook", "LinkedIn"]
)

platform_mapping = {
    "Instagram": 0,
    "Twitter": 1,
    "Facebook": 2,
    "LinkedIn": 3
}

# Post Type
post_type = st.sidebar.selectbox(
    "Post Type",
    ["Image", "Video", "Text", "Link"]
)

post_type_mapping = {
    "Image": 0,
    "Video": 1,
    "Text": 2,
    "Link": 3
}

# Topic
topic = st.sidebar.selectbox(
    "Topic",
    ["technology", "marketing", "education", "business", "finance", 
     "health", "lifestyle", "entertainment", "sports", "news"]
)

topic_mapping = {
    "technology": 0, "marketing": 1, "education": 2, "business": 3,
    "finance": 4, "health": 5, "lifestyle": 6, "entertainment": 7,
    "sports": 8, "news": 9, "general": 10
}

# User features
st.sidebar.subheader("👤 User Features")
follower_count = st.sidebar.number_input(
    "Follower Count",
    min_value=0,
    max_value=10000000,
    value=5000,
    step=100
)

is_verified = st.sidebar.checkbox("Verified Account")

# Post features
st.sidebar.subheader("📝 Post Features")
word_count = st.sidebar.slider("Word Count", 0, 500, 50)
hashtag_count = st.sidebar.slider("Hashtag Count", 0, 30, 3)

# Time features
st.sidebar.subheader("🕐 Timing")
post_hour = st.sidebar.slider("Post Hour (0-23)", 0, 23, 12)
post_day = st.sidebar.selectbox(
    "Day of Week",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)

day_mapping = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}

is_weekend = 1 if post_day in ["Saturday", "Sunday"] else 0

# Sentiment
sentiment = st.sidebar.slider("Sentiment (-1 to 1)", -1.0, 1.0, 0.0, 0.1)

# Prepare features
features = pd.DataFrame({
    'user_follower_count': [follower_count],
    'user_is_verified': [1 if is_verified else 0],
    'post_word_count': [word_count],
    'post_hashtag_count': [hashtag_count],
    'post_hour': [post_hour],
    'post_day_of_week': [day_mapping[post_day]],
    'post_sentiment': [sentiment],
    'post_is_weekend': [is_weekend],
    'platform_encoded': [platform_mapping[platform]],
    'post_type_encoded': [post_type_mapping[post_type]],
    'topic_encoded': [topic_mapping.get(topic, 10)]
})

# Main area - Prediction
st.header("🎯 Engagement Prediction")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Summary")
    st.write(f"**Platform:** {platform}")
    st.write(f"**Post Type:** {post_type}")
    st.write(f"**Topic:** {topic}")
    st.write(f"**Followers:** {follower_count:,}")
    st.write(f"**Verified:** {'Yes' if is_verified else 'No'}")
    st.write(f"**Words:** {word_count}")
    st.write(f"**Hashtags:** {hashtag_count}")
    st.write(f"**Time:** {post_day} at {post_hour}:00")
    st.write(f"**Sentiment:** {sentiment:.1f}")

with col2:
    # Make prediction
    prediction = model.predict(features)[0]
    prediction_proba = model.predict_proba(features)[0]
    
    # Map prediction to category
    categories = ["Low", "Medium", "High"]
    predicted_category = categories[prediction]
    
    st.subheader("Predicted Engagement")
    
    # Display prediction with color
    if predicted_category == "High":
        st.success(f"### 🔥 {predicted_category} Engagement")
    elif predicted_category == "Medium":
        st.info(f"### 📊 {predicted_category} Engagement")
    else:
        st.warning(f"### 📉 {predicted_category} Engagement")
    
    # Show probabilities
    st.write("**Confidence:**")
    for i, cat in enumerate(categories):
        prob = prediction_proba[i] * 100
        st.progress(prob/100)
        st.write(f"{cat}: {prob:.1f}%")

# Recommendations
st.markdown("---")
st.header("💡 Recommendations")

recommendations = []

if follower_count < 1000:
    recommendations.append("📈 **Grow your audience** - Focus on building followers to increase reach")

if hashtag_count < 3:
    recommendations.append("🏷️ **Add more hashtags** - Use 5-10 relevant hashtags for better discovery")

if word_count < 20:
    recommendations.append("✍️ **Add more content** - Longer posts tend to drive more engagement")

if post_hour < 9 or post_hour > 18:
    recommendations.append("🕐 **Post during peak hours** - Try posting between 9 AM and 6 PM")

if not is_weekend and post_day in ["Monday", "Tuesday"]:
    recommendations.append("📅 **Try weekend posting** - Engagement is often higher on weekends")

if post_type == "Text":
    recommendations.append("🖼️ **Add visuals** - Image and video posts get more engagement")

if sentiment < 0:
    recommendations.append("😊 **Use positive tone** - Positive content tends to perform better")

if recommendations:
    for rec in recommendations:
        st.write(rec)
else:
    st.success("✅ Your post is well-optimized for engagement!")

# Footer
st.markdown("---")
st.caption(f"Model loaded from: {source} | Last prediction: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Add cloud status in sidebar
st.sidebar.markdown("---")
st.sidebar.caption("☁️ **Cloud Status**")
if AZURE_AVAILABLE:
    st.sidebar.caption("✅ Azure SDK Available")
    if source == "Azure Blob Storage":
        st.sidebar.caption("✅ Using Cloud Model")
    else:
        st.sidebar.caption("⚠️ Using Local Model")
else:
    st.sidebar.caption("⚠️ Azure SDK Not Installed")
    st.sidebar.caption("📦 Install: `pip install azure-storage-blob`")
