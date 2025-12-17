# Azure App Service Deployment

## Files Deployed:
- app_streamlit.py: Main Streamlit application
- models/model_gb.pkl: Trained Gradient Boosting model
- data/processed/cleaned_data.csv: Preprocessed training data
- data/processed/encoders.pkl: Label encoders for categorical features
- requirements_app.txt: Python dependencies
- startup.sh: App Service startup script

## Deployment Configuration:
- **App Name**: engagement-app-demo.azurewebsites.net
- **Runtime**: Python 3.12
- **Plan**: Azure App Service Free Tier (F1)
- **Port**: 8000 (Streamlit default)
- **Region**: francecentral

## Startup Command:
```bash
bash startup.sh
```

## Environment Variables (to be set in App Service):
- WEBSITES_PORT=8000
- SCM_DO_BUILD_DURING_DEPLOYMENT=true

## Running Locally:
```bash
pip install -r requirements_app.txt
streamlit run app_streamlit.py
```

## Access:
https://engagement-app-demo.azurewebsites.net/

## Features:
- Real-time engagement rate prediction
- Input controls for sentiment, toxicity, user history
- Feature engineering visualization
- Model performance metrics display
