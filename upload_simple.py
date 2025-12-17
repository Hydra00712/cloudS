"""
Simple Azure Blob Upload - Using Account Key
"""

import os
import subprocess

STORAGE_ACCOUNT = "stengml707"
RESOURCE_GROUP = "rg-engagement-ml"

def get_account_key():
    """Get storage account key"""
    print("🔑 Getting storage account key...")
    result = subprocess.run(
        [
            "py", "-m", "azure.cli", "storage", "account", "keys", "list",
            "--account-name", STORAGE_ACCOUNT,
            "--resource-group", RESOURCE_GROUP,
            "--output", "json"
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return None
    
    import json
    keys = json.loads(result.stdout)
    return keys[0]['value'] if keys else None

def upload_file(local_path, container, blob_name, account_key):
    """Upload file using Azure CLI"""
    print(f"📤 Uploading {local_path} to {container}/{blob_name}...")
    
    result = subprocess.run(
        [
            "py", "-m", "azure.cli", "storage", "blob", "upload",
            "--account-name", STORAGE_ACCOUNT,
            "--account-key", account_key,
            "--container-name", container,
            "--name", blob_name,
            "--file", local_path,
            "--overwrite"
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Uploaded successfully!")
        return True
    else:
        print(f"❌ Upload failed: {result.stderr}")
        return False

def main():
    print("\n" + "="*70)
    print("AZURE BLOB STORAGE - DATA UPLOAD")
    print("="*70 + "\n")
    
    # Get account key
    account_key = get_account_key()
    if not account_key:
        print("❌ Could not retrieve storage account key")
        return
    
    print("✅ Account key retrieved\n")
    
    # Upload cleaned data
    if os.path.exists("data/processed/cleaned_data.csv"):
        upload_file("data/processed/cleaned_data.csv", "cleaned-data", "cleaned_data.csv", account_key)
    else:
        print("⚠️  Cleaned data not found")
    
    # Upload model
    if os.path.exists("models/model.pkl"):
        upload_file("models/model.pkl", "models", "model.pkl", account_key)
    else:
        print("⚠️  Model file not found")
    
    print("\n✅ Upload complete!")

if __name__ == "__main__":
    main()
