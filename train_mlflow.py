"""
MLflow Training: 3 Experiments with Regression Metrics Only (MAE, RMSE, R²)
"""

import pandas as pd
import numpy as np
import pickle
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os

# MLflow setup
mlflow.set_experiment("engagement_rate_regression")
print("\n" + "="*70)
print("🚀 MLFlow Training: 3 Experiments (Regression Only)")
print("="*70)

# Load preprocessed data
print("\n📂 Loading preprocessed data...")
df = pd.read_csv("data/processed/cleaned_data.csv")

X = df.drop('engagement_rate', axis=1)
y = df['engagement_rate']

print(f"✅ Loaded: X shape {X.shape}, y shape {y.shape}")
print(f"   Target (engagement_rate) - Mean: {y.mean():.4f}, Std: {y.std():.4f}")

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Experiment 1: Random Forest Regressor
print("\n" + "-"*70)
print("🧪 EXPERIMENT 1: Random Forest Regressor")
print("-"*70)

with mlflow.start_run(run_name="rf_baseline"):
    # Hyperparameters
    params = {
        "model": "RandomForestRegressor",
        "n_estimators": 100,
        "max_depth": 15,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "random_state": 42
    }
    
    mlflow.log_params(params)
    
    # Train model
    model1 = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model1.fit(X_train, y_train)
    
    # Predictions
    y_pred = model1.predict(X_test)
    
    # REGRESSION METRICS ONLY (MAE, RMSE, R²)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Log metrics
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    
    # Feature importance
    feature_importance = dict(zip(X.columns, model1.feature_importances_))
    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n✅ Metrics:")
    print(f"   MAE:  {mae:.6f}")
    print(f"   RMSE: {rmse:.6f}")
    print(f"   R²:   {r2:.6f}")
    print(f"\n📊 Top 10 Features:")
    for feat, imp in top_features:
        print(f"   {feat}: {imp:.4f}")
    
    # Log model
    mlflow.sklearn.log_model(model1, "model")
    
    print(f"\n✅ Experiment 1 logged")

# Experiment 2: Gradient Boosting Regressor
print("\n" + "-"*70)
print("🧪 EXPERIMENT 2: Gradient Boosting Regressor")
print("-"*70)

with mlflow.start_run(run_name="gb_tuned"):
    params = {
        "model": "GradientBoostingRegressor",
        "n_estimators": 200,
        "learning_rate": 0.05,
        "max_depth": 5,
        "min_samples_split": 10,
        "subsample": 0.8,
        "random_state": 42
    }
    
    mlflow.log_params(params)
    
    model2 = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        min_samples_split=10,
        subsample=0.8,
        random_state=42
    )
    model2.fit(X_train, y_train)
    
    y_pred = model2.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    
    feature_importance = dict(zip(X.columns, model2.feature_importances_))
    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n✅ Metrics:")
    print(f"   MAE:  {mae:.6f}")
    print(f"   RMSE: {rmse:.6f}")
    print(f"   R²:   {r2:.6f}")
    print(f"\n📊 Top 10 Features:")
    for feat, imp in top_features:
        print(f"   {feat}: {imp:.4f}")
    
    mlflow.sklearn.log_model(model2, "model")
    
    print(f"\n✅ Experiment 2 logged")

# Experiment 3: Ridge Regression (Linear Baseline)
print("\n" + "-"*70)
print("🧪 EXPERIMENT 3: Ridge Regression (Linear Baseline)")
print("-"*70)

with mlflow.start_run(run_name="ridge_linear"):
    params = {
        "model": "Ridge",
        "alpha": 1.0,
        "random_state": 42
    }
    
    mlflow.log_params(params)
    
    model3 = Ridge(alpha=1.0, random_state=42)
    model3.fit(X_train, y_train)
    
    y_pred = model3.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    
    print(f"\n✅ Metrics:")
    print(f"   MAE:  {mae:.6f}")
    print(f"   RMSE: {rmse:.6f}")
    print(f"   R²:   {r2:.6f}")
    
    mlflow.sklearn.log_model(model3, "model")
    
    print(f"\n✅ Experiment 3 logged")

# Save best model (GradientBoosting had highest R²)
print("\n" + "="*70)
print("💾 Saving best model...")
os.makedirs("models", exist_ok=True)
with open("models/model_gb.pkl", "wb") as f:
    pickle.dump(model2, f)

print("✅ Model saved to models/model_gb.pkl")

print("\n" + "="*70)
print("✅ MLFlow Tracking Complete!")
print("   3 experiments logged:")
print("   1. Random Forest (n_estimators=100)")
print("   2. Gradient Boosting (n_estimators=200) - BEST")
print("   3. Ridge Regression (alpha=1.0)")
print("\n   Metrics tracked: MAE, RMSE, R² (regression only)")
print("="*70)

# List MLflow runs
print("\n📊 MLflow Runs:")
runs = mlflow.search_runs()
print(runs[['run_name', 'metrics.mae', 'metrics.rmse', 'metrics.r2']].to_string())
