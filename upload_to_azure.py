"""
Cloud-Enabled Data Upload Script
Upload raw data and cleaned data to Azure Blob Storage
"""

import pandas as pd
import os
from azure.storage.blob import BlobServiceClient
from azure.identity import InteractiveBrowserCredential
from azure_config import (
    STORAGE_ACCOUNT_NAME, 
    TENANT_ID,
    CONTAINER_RAW_DATA, 
    CONTAINER_CLEANED_DATA,
    get_storage_account_key
)

def upload_to_blob(local_path, container_name, blob_name):
    """Upload file to Azure Blob Storage"""
    print(f"📤 Uploading {local_path} to {container_name}/{blob_name}...")
    
    # Get storage account key
    account_key = get_storage_account_key()
    
    if not account_key:
        print("❌ Could not retrieve storage account key")
        return False
    
    # Create connection string
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={STORAGE_ACCOUNT_NAME};"
        f"AccountKey={account_key};"
        f"EndpointSuffix=core.windows.net"
    )
    
    try:
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        # Upload file
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        print(f"✅ Uploaded successfully!")
        print(f"   URL: https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{blob_name}")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def download_from_blob(container_name, blob_name, local_path):
    """Download file from Azure Blob Storage"""
    print(f"📥 Downloading {container_name}/{blob_name} to {local_path}...")
    
    # Get storage account key
    account_key = get_storage_account_key()
    
    if not account_key:
        print("❌ Could not retrieve storage account key")
        return False
    
    # Create connection string
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={STORAGE_ACCOUNT_NAME};"
        f"AccountKey={account_key};"
        f"EndpointSuffix=core.windows.net"
    )
    
    try:
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        # Create directory if needed
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download file
        with open(local_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        print(f"✅ Downloaded successfully to {local_path}")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def main():
    """Upload data files to Azure"""
    print("\n" + "="*70)
    print("AZURE BLOB STORAGE - DATA UPLOAD")
    print("="*70 + "\n")
    
    # Upload raw dataset
    raw_data_path = "archive (1)/Social Media Engagement Dataset.csv"
    if os.path.exists(raw_data_path):
        upload_to_blob(raw_data_path, CONTAINER_RAW_DATA, "Social_Media_Engagement_Dataset.csv")
    else:
        print(f"⚠️  Raw data file not found: {raw_data_path}")
    
    # Upload cleaned dataset
    cleaned_data_path = "data/processed/cleaned_data.csv"
    if os.path.exists(cleaned_data_path):
        upload_to_blob(cleaned_data_path, CONTAINER_CLEANED_DATA, "cleaned_data.csv")
    else:
        print(f"⚠️  Cleaned data file not found: {cleaned_data_path}")
    
    # Upload model if exists
    model_path = "models/model.pkl"
    if os.path.exists(model_path):
        from azure_config import CONTAINER_MODELS
        upload_to_blob(model_path, CONTAINER_MODELS, "model.pkl")
    else:
        print(f"⚠️  Model file not found: {model_path}")
    
    print("\n✅ Upload process complete!")

if __name__ == "__main__":
    main()
