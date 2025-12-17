# 5️⃣ MLFLOW EXPERIMENT TRACKING SETUP

## What MLflow Does
- **Tracks experiments** (versioning, hyperparameters, metrics)
- **Logs artifacts** (models, plots, data)
- **Registers models** (versioning, staging, production)
- **UI dashboard** (compare runs, visualize metrics)

## Azure ML + MLflow Integration

```
Local Training Job
      ↓
MLflow Tracking Client
      ↓
Azure Blob Storage (artifact backend)
      ↓
Azure ML Studio (UI dashboard)
```

## Implementation Files

### File: `mlflow_config.py`
```python
"""MLflow configuration for Azure ML backend"""

import os
import mlflow
from azure.identity import DefaultAzureCredential

def setup_mlflow():
    """Configure MLflow to use Azure ML as tracking backend"""
    
    # === SET TRACKING URI TO AZURE ML ===
    # This tells MLflow to store all data in Azure ML workspace
    mlflow.set_tracking_uri("azureml://")
    
    # === SET EXPERIMENT ===
    # Each experiment is a project (like version control branches)
    mlflow.set_experiment("social-media-engagement")
    
    # === ENABLE AUTOLOG ===
    # Auto-captures sklearn metrics, parameters, models
    mlflow.sklearn.autolog()
    mlflow.xgboost.autolog()
    
    print("✅ MLflow configured for Azure ML backend")


def log_model_comparison(models_dict, X_test, y_test):
    """
    Log multiple models to MLflow for comparison
    
    Args:
        models_dict: {"model_name": model_object}
        X_test, y_test: Test data
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    import numpy as np
    
    for name, model in models_dict.items():
        with mlflow.start_run(run_name=f"{name}-tuned"):
            
            # === Predictions ===
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # === Compute metrics ===
            metrics = {
                f"{name}_mae_train": mean_absolute_error(y_train, y_pred_train),
                f"{name}_mae_test": mean_absolute_error(y_test, y_pred_test),
                f"{name}_rmse_train": np.sqrt(mean_squared_error(y_train, y_pred_train)),
                f"{name}_rmse_test": np.sqrt(mean_squared_error(y_test, y_pred_test)),
                f"{name}_r2_train": r2_score(y_train, y_pred_train),
                f"{name}_r2_test": r2_score(y_test, y_pred_test),
            }
            
            # === Log to MLflow ===
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, artifact_path=f"model_{name}")
            
            print(f"✅ Logged {name} run")


def register_best_model(run_id, model_name="engagement-predictor"):
    """
    Register best model to Model Registry
    
    Args:
        run_id: MLflow run ID of best model
        model_name: Name in registry
    """
    
    model_uri = f"runs:/{run_id}/model_XGBoost"
    
    # Register in Model Registry
    mv = mlflow.register_model(model_uri, model_name)
    
    print(f"✅ Registered model: {model_name} version {mv.version}")
    
    # Transition to Staging (for review before production)
    client = mlflow.tracking.MlflowClient()
    client.transition_model_version_stage(
        name=model_name,
        version=mv.version,
        stage="Staging"
    )
    
    return mv
```

### File: `train_with_mlflow.py` (Modified train_model_clean.py)
```python
"""
Training script with MLflow integration for Azure ML
Modified version of train_model_clean.py
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import pickle
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from mlflow_config import setup_mlflow
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import logging

# === CONFIGURE LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === SETUP MLFLOW ===
setup_mlflow()

# === AZURE STORAGE CLIENT ===
credential = DefaultAzureCredential()
blob_service = BlobServiceClient(
    account_url="https://{STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=credential
)
processed_container = blob_service.get_container_client("processed-data")
models_container = blob_service.get_container_client("models")


def load_cleaned_data():
    """Load data from Azure Blob Storage"""
    logger.info("📥 Loading cleaned data from Azure Blob...")
    
    blob_client = processed_container.get_blob_client("cleaned_data.csv")
    with open("temp_cleaned.csv", "wb") as f:
        f.write(blob_client.download_blob().readall())
    
    df = pd.read_csv("temp_cleaned.csv")
    logger.info(f"✅ Loaded {len(df)} samples, {df.shape[1]} features")
    return df


def prepare_data(df):
    """Separate features and target"""
    X = df.drop(columns=['engagement_rate'])
    y = df['engagement_rate']
    return X, y


def split_data(X, y, test_size=0.2, random_state=42):
    """Split with stratification for balanced test set"""
    y_binned = pd.cut(y, bins=5, labels=False)  # Stratify by engagement quintiles
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y_binned
    )
    return X_train, X_test, y_train, y_test


def _search(model, params, X_train, y_train, name):
    """Generic hyperparameter search"""
    search = RandomizedSearchCV(
        model, params, cv=3, n_iter=10, n_jobs=-1, verbose=1
    )
    search.fit(X_train, y_train)
    logger.info(f"✅ {name} best params: {search.best_params_}")
    return search.best_estimator_, search.best_params_, search.best_score_


def train_model(X_train, y_train):
    """Train all 4 models with hyperparameter tuning"""
    
    logger.info("🔧 Training models with hyperparameter tuning...")
    
    models = {}
    
    # === START MLFLOW PARENT RUN ===
    with mlflow.start_run(run_name="full-training-pipeline"):
        
        # === LOG DATASET INFO ===
        mlflow.log_param("dataset_size", len(X_train))
        mlflow.log_param("n_features", X_train.shape[1])
        mlflow.log_param("cv_folds", 3)
        
        # 1. RandomForest
        logger.info("1️⃣ RandomForest...")
        with mlflow.start_run(run_name="RandomForest", nested=True):
            rf_params = {
                'n_estimators': [500, 700, 900],
                'max_depth': [15, 20, 25],
                'min_samples_split': [2, 5],
            }
            rf_best, rf_params_best, rf_mae = _search(
                RandomForestRegressor(random_state=42, n_jobs=-1), rf_params, X_train, y_train, "RF"
            )
            models['RandomForest'] = rf_best
            mlflow.log_params({"rf_" + k: v for k, v in rf_params_best.items()})
            models['RandomForest'] = rf_best
        
        # 2. ExtraTrees
        logger.info("2️⃣ ExtraTrees...")
        with mlflow.start_run(run_name="ExtraTrees", nested=True):
            et_params = {
                'n_estimators': [600, 800, 1000],
                'max_depth': [15, 20, 25],
                'min_samples_split': [2, 5],
            }
            et_best, et_params_best, et_mae = _search(
                ExtraTreesRegressor(random_state=42, n_jobs=-1), et_params, X_train, y_train, "ET"
            )
            models['ExtraTrees'] = et_best
            mlflow.log_params({"et_" + k: v for k, v in et_params_best.items()})
        
        # 3. HistGradientBoosting
        logger.info("3️⃣ HistGradientBoosting...")
        with mlflow.start_run(run_name="HistGradientBoosting", nested=True):
            hgb_params = {
                'learning_rate': [0.02, 0.04, 0.06],
                'max_iter': [100, 150, 200],
            }
            hgb_best, hgb_params_best, hgb_mae = _search(
                HistGradientBoostingRegressor(random_state=42), hgb_params, X_train, y_train, "HGB"
            )
            models['HistGradientBoosting'] = hgb_best
            mlflow.log_params({"hgb_" + k: v for k, v in hgb_params_best.items()})
        
        # 4. XGBoost
        logger.info("4️⃣ XGBoost...")
        with mlflow.start_run(run_name="XGBoost", nested=True):
            xgb_params = {
                'n_estimators': [400, 600, 800],
                'max_depth': [5, 7, 9],
                'learning_rate': [0.01, 0.05, 0.1],
            }
            xgb_best, xgb_params_best, xgb_mae = _search(
                xgb.XGBRegressor(random_state=42, n_jobs=-1), xgb_params, X_train, y_train, "XGB"
            )
            models['XGBoost'] = xgb_best
            mlflow.log_params({"xgb_" + k: v for k, v in xgb_params_best.items()})
        
        return models


def evaluate(model, X_train, y_train, X_test, y_test, model_name="Model"):
    """Compute and log evaluation metrics"""
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    mae_train = mean_absolute_error(y_train, y_pred_train)
    mae_test = mean_absolute_error(y_test, y_pred_test)
    rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    
    metrics = {
        'mae_train': mae_train,
        'mae_test': mae_test,
        'rmse_train': rmse_train,
        'rmse_test': rmse_test,
        'r2_train': r2_train,
        'r2_test': r2_test,
    }
    
    # === LOG TO MLFLOW ===
    for metric_name, value in metrics.items():
        mlflow.log_metric(f"{model_name}_{metric_name}", value)
    
    logger.info(f"✅ {model_name} - MAE: {mae_test:.4f}, RMSE: {rmse_test:.4f}, R²: {r2_test:.4f}")
    
    return metrics


def select_best_model(models_dict, X_test, y_test):
    """Select best model based on test MAE"""
    best_name, best_model = None, None
    best_mae = float('inf')
    
    for name, model in models_dict.items():
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        if mae < best_mae:
            best_mae = mae
            best_name, best_model = name, model
    
    logger.info(f"🏆 Best model: {best_name} (MAE: {best_mae:.4f})")
    return best_name, best_model


def save_model_to_blob(model, best_name):
    """Save model to Azure Blob Storage"""
    logger.info(f"💾 Saving {best_name} to Azure Blob...")
    
    model_bytes = pickle.dumps(model)
    models_container.upload_blob(
        name=f"model_{best_name}.pkl",
        data=model_bytes,
        overwrite=True
    )
    
    logger.info(f"✅ Saved to Azure: model_{best_name}.pkl")


def train_and_evaluate():
    """Main training pipeline"""
    
    logger.info("=" * 60)
    logger.info("🚀 STARTING TRAINING PIPELINE WITH MLFLOW")
    logger.info("=" * 60)
    
    # Load data
    df = load_cleaned_data()
    X, y = prepare_data(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Train models
    models = train_model(X_train, y_train)
    
    # Evaluate models
    for name, model in models.items():
        evaluate(model, X_train, y_train, X_test, y_test, name)
    
    # Select best
    best_name, best_model = select_best_model(models, X_test, y_test)
    
    # === LOG BEST MODEL TO MLFLOW ===
    with mlflow.start_run(run_name="best-model-final"):
        mlflow.sklearn.log_model(best_model, artifact_path="model")
        mlflow.log_param("best_model_type", best_name)
        
        # Register in Model Registry
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"
        mv = mlflow.register_model(model_uri, "engagement-predictor")
        logger.info(f"✅ Registered: {mv.name} v{mv.version}")
    
    # Save to Blob
    save_model_to_blob(best_model, best_name)
    
    logger.info("=" * 60)
    logger.info("✅ TRAINING COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    train_and_evaluate()
```

## Viewing Experiments in Azure ML Studio

After running `train_with_mlflow.py`:

1. Go to [Azure ML Studio](https://ml.azure.com)
2. Select workspace: `aml-engagement`
3. Left sidebar → **Experiments**
4. Click **social-media-engagement**
5. View:
   - All runs (RandomForest, ExtraTrees, etc.)
   - Metrics comparison chart
   - Hyperparameters for each run
   - Artifacts (models, logs)

## Model Registry

After best model selected:

1. **Experiments** → Best run → **Register Model**
2. Creates entry in **Models** section
3. Version stages: `None` → `Staging` → `Production`
4. Can deploy directly from registry

