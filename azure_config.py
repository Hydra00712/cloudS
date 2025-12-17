"""
Azure Configuration
Store credentials in environment variables or Azure Key Vault in production
"""

import os

# Azure Storage Configuration
STORAGE_ACCOUNT_NAME = "stengml707"
STORAGE_CONNECTION_STRING = None  # Will be retrieved from Key Vault
CONTAINER_RAW_DATA = "raw-data"
CONTAINER_CLEANED_DATA = "cleaned-data"
CONTAINER_MODELS = "models"

# Azure Key Vault
KEY_VAULT_NAME = "kvengml8449"
KEY_VAULT_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net/"

# Azure Authentication
TENANT_ID = "78ddbe5d-b682-466c-bad0-6ffbaf7ceb2d"
SUBSCRIPTION_ID = "10ceef72-c9cd-4fb6-844b-ee8661d294fc"
RESOURCE_GROUP = "rg-engagement-ml"

# Local Paths
LOCAL_DATA_PATH = "data/processed/cleaned_data.csv"
LOCAL_MODEL_PATH = "models/model.pkl"

def get_storage_connection_string():
    """Get storage connection string from environment or Key Vault"""
    # Try environment variable first
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    if not conn_str:
        # Retrieve from Key Vault
        try:
            from azure.identity import InteractiveBrowserCredential
            from azure.keyvault.secrets import SecretClient
            
            credential = InteractiveBrowserCredential(tenant_id=TENANT_ID)
            client = SecretClient(vault_url=KEY_VAULT_URI, credential=credential)
            secret = client.get_secret("storage-connection-string")
            conn_str = secret.value
        except Exception as e:
            print(f"Warning: Could not retrieve connection string from Key Vault: {e}")
            print("Using account name authentication instead")
            return None
    
    return conn_str

def get_storage_account_key():
    """Get storage account key using Azure CLI"""
    import subprocess
    import json
    
    try:
        result = subprocess.run(
            ["py", "-m", "azure.cli", "storage", "account", "keys", "list", 
             "--account-name", STORAGE_ACCOUNT_NAME, 
             "--resource-group", RESOURCE_GROUP,
             "--query", "[0].value", "-o", "tsv"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error retrieving storage key: {e}")
        return None
