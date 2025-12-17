"""
MODEL TRAINING - Simple & Clean
Train RandomForest model and evaluate performance
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor, VotingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

MODEL_DIR = "models"


def load_cleaned_data(filepath="data/processed/cleaned_data.csv"):
    """Load preprocessed data."""
    print("📂 Loading cleaned data...")
    df = pd.read_csv(filepath)
    print(f"✅ Loaded: {len(df)} rows, {len(df.columns)} columns")
    return df


def prepare_data(df):
    """Separate features (X) and target (y)."""
    print("\n🎯 Preparing features and target...")
    
    X = df.drop('engagement_rate', axis=1)
    y = df['engagement_rate']
    
    print(f"   Features: {X.shape[1]}")
    print(f"   Target: {y.shape[0]} samples")
    print(f"   Target range: {y.min():.2f} to {y.max():.2f}")
    
    return X, y


def split_data(X, y, test_size=0.2):
    """Split into train/test sets using stratified bins for balanced class distribution."""
    from sklearn.model_selection import train_test_split as tts
    
    print("\n✂️ Splitting data (80/20) with stratification...")
    
    # Create bins for stratification using balanced thresholds
    def to_bin(val):
        if val < 0.1:
            return 0
        elif val < 0.25:
            return 1
        else:
            return 2
    
    bins = y.apply(to_bin)
    
    X_train, X_test, y_train, y_test = tts(
        X, y, test_size=test_size, random_state=42, stratify=bins
    )
    
    print(f"   Train: {len(X_train)} samples")
    print(f"   Test: {len(X_test)} samples")
    
    return X_train, X_test, y_train, y_test


def _search(estimator, param_dist, X_train, y_train, name: str):
    """Run randomized search for a single estimator."""
    search = RandomizedSearchCV(
        estimator,
        param_distributions=param_dist,
        n_iter=12,
        cv=3,
        scoring="neg_mean_absolute_error",
        n_jobs=-1,
        random_state=42,
        verbose=0,
    )
    print(f"   🔎 Tuning {name}...")
    search.fit(X_train, y_train)
    best_mae = -search.best_score_
    print(f"   ➜ Best CV MAE for {name}: {best_mae:.4f}")
    return search.best_estimator_, search.best_params_, best_mae


def train_model(X_train, y_train):
    """Tune and select the best ensemble/boosting model with aggressive hyperparameter search."""
    print("\n🌲 Training ensemble models with hyperparameter search...")

    rf_params = {
        "n_estimators": [500, 700, 900],
        "max_depth": [None, 20, 30],
        "max_features": ["sqrt", "log2", 0.5],
        "min_samples_split": [2, 3, 5],
        "min_samples_leaf": [1, 2],
    }

    et_params = {
        "n_estimators": [600, 800, 1000],
        "max_depth": [None, 40, 60],
        "max_features": ["sqrt", "log2", 0.6],
        "min_samples_split": [2, 3, 5],
        "min_samples_leaf": [1, 2],
    }

    hgb_params = {
        "learning_rate": [0.02, 0.04, 0.06],
        "max_depth": [10, 15, 20],
        "max_leaf_nodes": [63, 127, 255],
        "min_samples_leaf": [5, 10, 15],
    }

    xgb_params = {
        "n_estimators": [400, 600, 800],
        "max_depth": [8, 10, 12],
        "learning_rate": [0.02, 0.04, 0.06],
        "subsample": [0.85, 0.95, 1.0],
        "colsample_bytree": [0.85, 0.95, 1.0],
        "min_child_weight": [1, 2, 3],
    }

    rf_best, rf_params_best, rf_mae = _search(
        RandomForestRegressor(random_state=42, n_jobs=-1), rf_params, X_train, y_train, "RandomForest"
    )
    et_best, et_params_best, et_mae = _search(
        ExtraTreesRegressor(random_state=42, n_jobs=-1), et_params, X_train, y_train, "ExtraTrees"
    )
    hgb_best, hgb_params_best, hgb_mae = _search(
        HistGradientBoostingRegressor(random_state=42), hgb_params, X_train, y_train, "HistGradientBoosting"
    )
    xgb_best, xgb_params_best, xgb_mae = _search(
        XGBRegressor(random_state=42, n_jobs=-1, verbosity=0), xgb_params, X_train, y_train, "XGBoost"
    )

    # Find best single model
    candidates = [(rf_mae, "RandomForest", rf_best, rf_params_best),
                  (et_mae, "ExtraTrees", et_best, et_params_best),
                  (hgb_mae, "HistGradientBoosting", hgb_best, hgb_params_best),
                  (xgb_mae, "XGBoost", xgb_best, xgb_params_best)]
    
    best = min(candidates, key=lambda x: x[0])
    best_mae, name, model, params = best
    print(f"   ✅ Selected {name} (best CV MAE)")
    return model, {"estimator": name, **params}


def evaluate(model, X_train, y_train, X_test, y_test):
    """Evaluate model on train and test sets."""
    print("\n📊 Evaluating model...")
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Training metrics
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    train_r2 = r2_score(y_train, y_train_pred)
    
    # Test metrics
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    test_r2 = r2_score(y_test, y_test_pred)
    
    print("\n   TRAINING SET:")
    print(f"     MAE:  {train_mae:.4f}")
    print(f"     RMSE: {train_rmse:.4f}")
    print(f"     R²:   {train_r2:.4f}")
    
    print("\n   TEST SET:")
    print(f"     MAE:  {test_mae:.4f}")
    print(f"     RMSE: {test_rmse:.4f}")
    print(f"     R²:   {test_r2:.4f}")
    
    metrics = {
        'train': {'mae': train_mae, 'rmse': train_rmse, 'r2': train_r2},
        'test': {'mae': test_mae, 'rmse': test_rmse, 'r2': test_r2}
    }
    
    return metrics, y_test_pred


def save_model(model, metrics, best_params):
    """Save trained model and metrics."""
    print("\n💾 Saving model...")
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Save model
    with open(f"{MODEL_DIR}/model.pkl", 'wb') as f:
        pickle.dump(model, f)
    print(f"   ✅ {MODEL_DIR}/model.pkl")
    
    # Save metrics
    with open(f"{MODEL_DIR}/metrics.txt", 'w') as f:
        f.write("="*60 + "\n")
        f.write("MODEL PERFORMANCE METRICS\n")
        f.write("="*60 + "\n\n")

        f.write("MODEL SELECTION:\n")
        f.write(f"  Estimator: {best_params.get('estimator', 'n/a')}\n")
        f.write(f"  Best Params: {best_params}\n\n")

        f.write("TRAINING SET:\n")
        f.write(f"  MAE:  {metrics['train']['mae']:.4f}\n")
        f.write(f"  RMSE: {metrics['train']['rmse']:.4f}\n")
        f.write(f"  R²:   {metrics['train']['r2']:.4f}\n\n")

        f.write("TEST SET:\n")
        f.write(f"  MAE:  {metrics['test']['mae']:.4f}\n")
        f.write(f"  RMSE: {metrics['test']['rmse']:.4f}\n")
        f.write(f"  R²:   {metrics['test']['r2']:.4f}\n")
    
    print(f"   ✅ {MODEL_DIR}/metrics.txt")


def train_and_evaluate(data_file="data/processed/cleaned_data.csv"):
    """
    Complete training pipeline:
    1. Load data
    2. Prepare features/target
    3. Split train/test
    4. Train model
    5. Evaluate
    6. Save model
    """
    print("\n" + "="*60)
    print("🚀 MODEL TRAINING & EVALUATION")
    print("="*60)
    
    df = load_cleaned_data(data_file)
    X, y = prepare_data(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    model, best_params = train_model(X_train, y_train)
    metrics, y_pred = evaluate(model, X_train, y_train, X_test, y_test)
    save_model(model, metrics, best_params)
    
    print("\n✅ TRAINING COMPLETE!")
    print("   Model saved and ready for predictions")
    
    return model, metrics


if __name__ == "__main__":
    model, metrics = train_and_evaluate()
