"""
STREAMLIT PREDICTION APP - BEGINNER-FRIENDLY VERSION
Interactive UI for social media engagement predictions
Easy 8-question format with helpful explanations
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Page configuration
st.set_page_config(
    page_title="📱 Engagement Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-box { background-color: #111827; color: #e5e7eb; padding: 20px; border-radius: 10px; margin: 10px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.35); }
    .info-box { background-color: #1e3a8a; color: #e5e7eb; padding: 18px; border-radius: 10px; border-left: 6px solid #60a5fa; box-shadow: 0 6px 18px rgba(0,0,0,0.30); }
    .stButton > button { width: 100%; padding: 12px; font-size: 18px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Configuration
MODEL_PATH = "models/model.pkl"
ENCODERS_PATH = "data/processed/encoders.pkl"


def bucketize(val, cuts):
    """Bucketize continuous value into discrete bucket."""
    for i, c in enumerate(cuts):
        if val <= c:
            return i
    return len(cuts)


def safe_encode(encoder, value):
    """Encode value; if unseen, snap to closest known class."""
    try:
        return encoder.transform([value])[0]
    except ValueError:
        known_classes = [int(c) for c in encoder.classes_]
        closest = min(known_classes, key=lambda x: abs(x - value))
        return encoder.transform([str(closest)])[0]



@st.cache_resource
def load_model_and_encoders():
    """Load trained model and encoders (cached)."""
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(ENCODERS_PATH, 'rb') as f:
            encoders = pickle.load(f)
        return model, encoders
    except FileNotFoundError:
        st.error("❌ Model files not found! Please train the model first.")
        st.stop()


def show_welcome():
    """Display welcome banner."""
    st.markdown("""
    <div class="info-box">
    <h2>🎯 Welcome to Engagement Predictor!</h2>
    <p><strong>Predict your social media post's engagement BEFORE posting.</strong></p>
    <p>Just answer 8 simple questions about your post, and our AI model will forecast how well it will perform!</p>
    </div>
    """, unsafe_allow_html=True)


def get_user_inputs(encoders):
    """Get 8 inputs from user with better organization."""
    
    st.markdown("## 📝 Tell Us About Your Post")
    st.write("Answer these 8 simple questions about your post:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 When & Where")
        
        # Q1: Day
        day = st.selectbox(
            "1️⃣ What day will you post?",
            options=encoders['day_of_week'].classes_,
            help="Choose the day of the week (affects visibility)",
            key="day_select"
        )
        
        # Q2: Platform
        platform = st.selectbox(
            "2️⃣ Which platform?",
            options=encoders['platform'].classes_,
            help="Different platforms have different engagement patterns",
            key="platform_select"
        )
        
        # Q3: Location
        location = st.selectbox(
            "3️⃣ Where are you posting from?",
            options=encoders['location'].classes_,
            help="Location affects engagement patterns",
            key="location_select"
        )
        
        st.markdown("### 📚 Content")
        
        # Q4: Topic
        topic = st.selectbox(
            "4️⃣ What's your post topic?",
            options=encoders['topic_category'].classes_,
            help="Choose the main topic category",
            key="topic_select"
        )
    
    with col2:
        st.markdown("### 💭 Tone & Style")
        
        # Q5: Language
        language = st.selectbox(
            "5️⃣ What language is your post?",
            options=encoders['language'].classes_,
            help="Language affects audience reach",
            key="language_select"
        )
        
        # Q6: Sentiment
        sentiment = st.slider(
            "6️⃣ What's the tone?",
            min_value=-1.0, max_value=1.0, step=0.1, value=0.0,
            help="← Negative | Positive →"
        )
        
        # Q7: Emotion
        emotion = st.selectbox(
            "7️⃣ What emotion does it express?",
            options=encoders['emotion_type'].classes_,
            help="Primary emotion in the post",
            key="emotion_select"
        )
        
        st.markdown("### ⚡ Context")
        
        # Q8: Toxicity
        toxicity = st.slider(
            "8️⃣ How controversial is it?",
            min_value=0.0, max_value=1.0, step=0.1, value=0.0,
            help="← Family-friendly | Controversial →"
        )
    
    # Bottom row for remaining questions
    st.markdown("### 📊 Your Track Record")
    col3, col4 = st.columns(2)
    
    with col3:
        # Q9: Past Performance
        past_perf = st.slider(
            "9️⃣ Your typical post performance:",
            min_value=-1.0, max_value=1.0, step=0.1, value=0.0,
            help="← Usually underperforms | Usually outperforms →"
        )
    
    with col4:
        # Q10: Growth
        growth = st.slider(
            "🔟 Your engagement growth trend:",
            min_value=-1.0, max_value=1.0, step=0.1, value=0.0,
            help="← Declining | Growing →"
        )
    
    return {
        'day_of_week': day,
        'platform': platform,
        'location': location,
        'topic_category': topic,
        'language': language,
        'sentiment_score': sentiment,
        'emotion_type': emotion,
        'toxicity_score': toxicity,
        'user_past_sentiment_avg': past_perf,
        'user_engagement_growth': growth
    }


def encode_inputs(inputs, encoders):
    """Convert user inputs to model-ready format with exact column order."""
    
    sentiment_bucket = bucketize(inputs['sentiment_score'], [-0.4, -0.1, 0.1, 0.4])
    toxicity_bucket = bucketize(inputs['toxicity_score'], [0.2, 0.4, 0.6, 0.8])
    past_perf_bucket = bucketize(inputs['user_past_sentiment_avg'], [-0.2, 0.0, 0.2, 0.5])
    growth_bucket = bucketize(inputs['user_engagement_growth'], [-0.2, 0.0, 0.2, 0.5])

    # Compute interaction features (same as training)
    sentiment_toxicity_interaction = inputs['sentiment_score'] * inputs['toxicity_score']
    abs_sentiment = abs(inputs['sentiment_score'])
    perf_momentum = inputs['user_past_sentiment_avg'] * inputs['user_engagement_growth']
    toxicity_squared = inputs['toxicity_score'] ** 2
    sentiment_squared = inputs['sentiment_score'] ** 2

    # Build dict in exact order: encoded categoricals, numericals, raw buckets, interactions
    encoded = {
        'day_of_week_encoded': encoders['day_of_week'].transform([inputs['day_of_week']])[0],
        'platform_encoded': encoders['platform'].transform([inputs['platform']])[0],
        'topic_category_encoded': encoders['topic_category'].transform([inputs['topic_category']])[0],
        'emotion_type_encoded': encoders['emotion_type'].transform([inputs['emotion_type']])[0],
        'location_encoded': encoders['location'].transform([inputs['location']])[0],
        'language_encoded': encoders['language'].transform([inputs['language']])[0],
        'sentiment_bucket_encoded': safe_encode(encoders['sentiment_bucket'], sentiment_bucket),
        'toxicity_bucket_encoded': safe_encode(encoders['toxicity_bucket'], toxicity_bucket),
        'past_perf_bucket_encoded': safe_encode(encoders['past_perf_bucket'], past_perf_bucket),
        'growth_bucket_encoded': safe_encode(encoders['growth_bucket'], growth_bucket),
        'sentiment_score': inputs['sentiment_score'],
        'toxicity_score': inputs['toxicity_score'],
        'user_past_sentiment_avg': inputs['user_past_sentiment_avg'],
        'user_engagement_growth': inputs['user_engagement_growth'],
        'sentiment_bucket': sentiment_bucket,
        'toxicity_bucket': toxicity_bucket,
        'past_perf_bucket': past_perf_bucket,
        'growth_bucket': growth_bucket,
        'sentiment_toxicity_interaction': sentiment_toxicity_interaction,
        'abs_sentiment': abs_sentiment,
        'perf_momentum': perf_momentum,
        'toxicity_squared': toxicity_squared,
        'sentiment_squared': sentiment_squared,
    }
    
    # Return DataFrame with columns in exact order expected by model (23 features)
    cols = ['day_of_week_encoded', 'platform_encoded', 'topic_category_encoded', 'emotion_type_encoded', 'location_encoded', 'language_encoded',
            'sentiment_bucket_encoded', 'toxicity_bucket_encoded', 'past_perf_bucket_encoded', 'growth_bucket_encoded',
            'sentiment_score', 'toxicity_score', 'user_past_sentiment_avg', 'user_engagement_growth',
            'sentiment_bucket', 'toxicity_bucket', 'past_perf_bucket', 'growth_bucket',
            'sentiment_toxicity_interaction', 'abs_sentiment', 'perf_momentum', 'toxicity_squared', 'sentiment_squared']
    
    return pd.DataFrame([encoded])[cols]


def get_engagement_level(rate):
    """Categorize engagement rate with emojis and descriptions."""
    if rate < 0.3:
        return "🔴 LOW", "Needs improvement - consider optimizations", "#ff6b6b"
    elif rate < 0.6:
        return "🟡 MODERATE", "Good performance - decent reach expected", "#ffd93d"
    else:
        return "🟢 HIGH", "Excellent! Expect strong engagement", "#51cf66"


def get_recommendations(inputs):
    """Generate personalized recommendations."""
    recs = []
    
    if inputs['sentiment_score'] <= -0.5:
        recs.append("💡 Try more positive language - people engage more with uplifting content")
    elif inputs['sentiment_score'] < 0:
        recs.append("💡 Add some positivity to boost engagement")
    
    if inputs['toxicity_score'] > 0.7:
        recs.append("⚠️ Very controversial - consider toning it down for wider appeal")
    elif inputs['toxicity_score'] > 0.5:
        recs.append("⚠️ Moderately controversial - some audiences may be put off")
    
    platform_tips = {
        'Instagram': "📸 Instagram tip: Use high-quality images and trending hashtags",
        'Facebook': "👥 Facebook tip: Ask engaging questions to encourage comments",
        'Twitter': "🐦 Twitter tip: Use trending hashtags for better visibility",
        'LinkedIn': "💼 LinkedIn tip: Share professional insights and expertise",
        'TikTok': "🎵 TikTok tip: Use trending sounds and keep videos under 60 seconds"
    }
    if inputs['platform'] in platform_tips:
        recs.append(platform_tips[inputs['platform']])
    
    if inputs['user_engagement_growth'] < -0.5:
        recs.append("📈 Try new content formats or posting times to reverse the trend")
    elif inputs['user_engagement_growth'] < 0:
        recs.append("📈 Your engagement is declining - experiment with fresh content")
    
    if inputs['emotion_type'] in ['Anger', 'Fear', 'Disgust']:
        recs.append("😊 Negative emotions get attention but positive emotions get shares")
    
    return recs if recs else ["✅ Your post looks great - keep doing what you're doing!"]



def display_results(prediction, inputs, recommendations):
    """Display prediction results in an attractive format."""
    level, description, color = get_engagement_level(prediction)
    
    st.markdown("---")
    st.markdown("## 🎯 Your Prediction Results")
    
    # Main prediction display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 5px solid {color};">
        <h3>Engagement Rate</h3>
        <h1 style="color: {color};">{prediction*100:.0f}%</h1>
        <p><strong>{level}</strong></p>
        <p style="font-size: 14px;">{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
        <h3>What This Means</h3>
        <p>Out of 100 people who see this post,</p>
        <h2>{prediction*100:.0f}</h2>
        <p>are expected to like, comment, or share it</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-box">
        <h3>Quick Tips</h3>
        <p>✅ Your predictions are based on 12,000+ real posts</p>
        <p>✅ Model accuracy: 63%</p>
        <p>✅ Always test and measure results!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("### 💡 Personalized Recommendations")
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Input summary
    with st.expander("📋 View Your Answers (for verification)"):
        summary_data = {
            'Question': [
                'When will you post?',
                'Where will you post?',
                'Post topic?',
                'Tone of post?',
                'Primary emotion?',
                'How controversial?',
                'Your past performance?',
                'Your growth trend?'
            ],
            'Your Answer': [
                inputs['day_of_week'],
                inputs['platform'],
                inputs['topic_category'],
                f"{inputs['sentiment_score']:.1f}",
                inputs['emotion_type'],
                f"{inputs['toxicity_score']:.1f}",
                f"{inputs['user_past_sentiment_avg']:.1f}",
                f"{inputs['user_engagement_growth']:.1f}"
            ]
        }
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)


def main():
    """Main Streamlit app."""
    
    # Show welcome message once
    show_welcome()
    
    # Load model
    model, encoders = load_model_and_encoders()

    st.markdown("### 🔮 Predict Engagement")

    # Get user inputs
    inputs = get_user_inputs(encoders)

    if st.button("🔮 Get My Prediction", type="primary", use_container_width=True, key="predict_btn"):

        X = encode_inputs(inputs, encoders)
        prediction = model.predict(X)[0]
        prediction = np.clip(prediction, 0, 1)  # Valid range

        display_results(prediction, inputs, get_recommendations(inputs))

    # Sidebar with info
    with st.sidebar:
        st.markdown("### ℹ️ About This App")
        st.write("""
        This app uses a machine learning model trained on 12,000+ real social media posts 
        to predict engagement rates.
        
        **Model Details:**
        - Algorithm: RandomForest
        - Accuracy: 63% on test data
        - Features: 8 post characteristics
        
        **How It Works:**
        Your answers are analyzed to predict what percentage of viewers will engage 
        (like, comment, or share).
        """)
        
        st.markdown("---")
        st.markdown("### 📚 Learn More")
        if st.button("📖 Read Full Documentation"):
            st.info("""
            For detailed information about this model and how it works, 
            see PROJECT_REPORT.md in the project folder.
            """)


if __name__ == "__main__":
    main()
