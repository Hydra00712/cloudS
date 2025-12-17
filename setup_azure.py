#!/usr/bin/env python3
"""
Azure Resource Setup using Python SDK
No CLI needed - uses Python Azure libraries
"""

import sys
import json
import subprocess
from pathlib import Path

# Install required packages
print("📦 Installing Azure SDK packages...")
packages = [
    "azure-identity",
    "azure-mgmt-resource",
    "azure-mgmt-storage",
    "azure-mgmt-sql",
    "azure-mgmt-keyvault",
]

for pkg in packages:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

print("✅ Packages installed\n")

# Now import after installation
from azure.identity import AzureCliCredential, InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient

# Configuration
SUBSCRIPTION_ID = "10ceef72-c9cd-4fb6-844b-ee8661d294fc"
RESOURCE_GROUP = "rg-engagement-ml"
LOCATION = "eastus"

print(f"🔐 Authenticating to Azure...")
print(f"📊 Subscription: {SUBSCRIPTION_ID}")
print(f"📍 Location: {LOCATION}\n")

try:
    # Try Azure CLI credentials first
    try:
        credential = AzureCliCredential()
        credential.get_token("https://management.azure.com/")
        print("✅ Using Azure CLI credentials")
    except:
        # Fall back to interactive browser login
        print("🔄 Starting browser login...")
        credential = InteractiveBrowserCredential()
        credential.get_token("https://management.azure.com/")
        print("✅ Authenticated via browser")
    
    # Initialize clients
    resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
    storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
    sql_client = SqlManagementClient(credential, SUBSCRIPTION_ID)
    
    # Step 1: Create Resource Group
    print(f"\n📦 Creating Resource Group: {RESOURCE_GROUP}...")
    rg = resource_client.resource_groups.create_or_update(
        RESOURCE_GROUP,
        {"location": LOCATION}
    )
    print(f"✅ Resource Group created")
    
    # Step 2: Create Storage Account
    storage_account_name = "stengagementdata593"
    print(f"\n💾 Creating Storage Account: {storage_account_name}...")
    
    storage_params = {
        "kind": "BlobStorage",
        "sku": {"name": "Standard_LRS"},
        "location": LOCATION,
        "access_tier": "Hot"
    }
    
    try:
        storage_async_operation = storage_client.storage_accounts.begin_create(
            RESOURCE_GROUP,
            storage_account_name,
            storage_params
        )
        storage_account = storage_async_operation.result()
        print(f"✅ Storage Account created: {storage_account.name}")
        
        # Get connection string
        storage_keys = storage_client.storage_accounts.list_keys(
            RESOURCE_GROUP,
            storage_account_name
        )
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_keys.keys[0].value};EndpointSuffix=core.windows.net"
        print(f"🔑 Connection String: {connection_string[:80]}...")
        
    except Exception as e:
        print(f"⚠️  Storage Account: {str(e)[:150]}")
    
    # Summary
    print("\n" + "="*70)
    print("✅ AZURE SETUP INITIATED")
    print("="*70)
    print(f"\n📋 Resources Created/Updated:")
    print(f"   • Resource Group: {RESOURCE_GROUP}")
    print(f"   • Location: {LOCATION}")
    print(f"   • Storage Account: {storage_account_name}")
    print(f"\n⏭️  Next Steps:")
    print(f"   1. Create Blob containers (raw-data, cleaned-data, models)")
    print(f"   2. Create SQL Database")
    print(f"   3. Create Key Vault")
    print(f"   4. Create ML Workspace")
    print(f"\n📌 See QUICK_AZURE_SETUP.md for manual Portal steps")
    
    print("\n✅ Setup complete!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\n💡 Make sure you're authenticated:")
    print("   az login")
    sys.exit(1)
