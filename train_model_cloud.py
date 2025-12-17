"""
Cloud-Enabled Model Training with MLflow Tracking
Train model locally but track experiments in MLflow
"""

import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')

# Optional MLflow import - will work without it
try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("⚠️  MLflow not installed. Running without experiment tracking.")

def train_model(data_path="data/processed/cleaned_data.csv", use_mlflow=False):
    """
    Train Random Forest model with optional MLflow tracking
    
    Args:
        data_path: Path to cleaned data CSV
        use_mlflow: Whether to use MLflow tracking
    """
    print("\n" + "="*70)
    print("MODEL TRAINING - Cloud-Enabled")
    print("="*70 + "\n")
    
    # Load data
    print("📂 Loading data...")
    df = pd.read_csv(data_path)
    print(f"✅ Loaded: {len(df)} rows")
    
    # Prepare features
    feature_cols = [
        'user_follower_count', 'user_is_verified', 'post_word_count',
        'post_hashtag_count', 'post_hour', 'post_day_of_week',
        'post_sentiment', 'post_is_weekend', 'platform_encoded',
        'post_type_encoded', 'topic_encoded'
    ]
    
    X = df[feature_cols]
    y = df['engagement_category_encoded']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📊 Train: {len(X_train)} | Test: {len(X_test)}")
    
    # Model parameters
    params = {
        'n_estimators': 100,
        'max_depth': 15,
        'min_samples_split': 10,
        'min_samples_leaf': 4,
        'random_state': 42,
        'n_jobs': -1
    }
    
    # Start MLflow run if available
    if use_mlflow and MLFLOW_AVAILABLE:
        mlflow.set_experiment("social-media-engagement")
        mlflow.start_run(run_name=f"rf_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        mlflow.log_params(params)
    
    # Train model
    print("\n🤖 Training Random Forest...")
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    print("✅ Training complete!")
    
    # Evaluate
    print("\n📊 Evaluating model...")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"\n🎯 Accuracy:  {accuracy:.4f}")
    print(f"🎯 Precision: {precision:.4f}")
    print(f"🎯 Recall:    {recall:.4f}")
    print(f"🎯 F1-Score:  {f1:.4f}")
    
    # Log metrics to MLflow
    if use_mlflow and MLFLOW_AVAILABLE:
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Log feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        mlflow.log_text(feature_importance.to_string(), "feature_importance.txt")
        
        print("\n✅ Logged to MLflow")
    
    # Save model locally
    os.makedirs("models", exist_ok=True)
    model_path = "models/model.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\n💾 Model saved: {model_path}")
    
    # Save metrics
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'timestamp': datetime.now().isoformat()
    }
    
    metrics_path = "models/metrics.txt"
    with open(metrics_path, 'w') as f:
        for key, value in metrics.items():
            f.write(f"{key}: {value}\n")
    
    print(f"📊 Metrics saved: {metrics_path}")
    
    # End MLflow run
    if use_mlflow and MLFLOW_AVAILABLE:
        mlflow.end_run()
    
    print("\n✅ Training complete!")
    return model, metrics

if __name__ == "__main__":
    # Train with MLflow if available
    model, metrics = train_model(use_mlflow=MLFLOW_AVAILABLE)
