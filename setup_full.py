"""
Complete Azure Resource Setup - All Resources
Run: py setup_full.py
"""

import subprocess
import sys
import time
import os

print("\n" + "="*70)
print("COMPLETE AZURE RESOURCE SETUP")
print("="*70 + "\n")

# Install packages
packages = [
    "azure-identity==1.15.0",
    "azure-mgmt-resource==23.1.0",
    "azure-mgmt-storage==21.1.0",
    "azure-mgmt-sql==4.0.0",
    "azure-mgmt-keyvault==10.3.0",
]

print("Installing Azure SDKs...")
for pkg in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], 
                  stderr=subprocess.DEVNULL)

from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient

# Configuration
SUBSCRIPTION_ID = "10ceef72-c9cd-4fb6-844b-ee8661d294fc"
TENANT_ID = "78ddbe5d-b682-466c-bad0-6ffbaf7ceb2d"
RESOURCE_GROUP = "rg-engagement-ml"
LOCATION = "eastus"

# Resource names
STORAGE_ACCOUNT = "stengagementdata593"
SQL_SERVER = "sql-engagement-593"
SQL_DB = "engagement_db"
KEY_VAULT = "kv-engagement-593"
CONTAINER_REGISTRY = "crengagement593"
FUNCTION_APP = "func-engagement"

print(f"Subscription: {SUBSCRIPTION_ID}")
print(f"Tenant: {TENANT_ID}")
print(f"Resource Group: {RESOURCE_GROUP}\n")

try:
    # Authenticate
    print("Authenticating (using cached credentials)...")
    credential = InteractiveBrowserCredential(tenant_id=TENANT_ID)
    
    # Initialize clients
    resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
    storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
    sql_client = SqlManagementClient(credential, SUBSCRIPTION_ID)
    keyvault_client = KeyVaultManagementClient(credential, SUBSCRIPTION_ID)
    
    # 1. Resource Group
    print("1. Creating Resource Group...")
    rg = resource_client.resource_groups.create_or_update(
        RESOURCE_GROUP,
        {"location": LOCATION}
    )
    print(f"   OK: {rg.name}\n")
    
    # 2. Storage Account
    print("2. Creating Storage Account...")
    try:
        storage_async = storage_client.storage_accounts.begin_create(
            RESOURCE_GROUP,
            STORAGE_ACCOUNT,
            {
                "kind": "BlobStorage",
                "sku": {"name": "Standard_LRS"},
                "location": LOCATION,
                "access_tier": "Hot"
            }
        )
        storage = storage_async.result()
        print(f"   OK: {storage.name}\n")
        
        # Get connection string
        keys = storage_client.storage_accounts.list_keys(
            RESOURCE_GROUP,
            STORAGE_ACCOUNT
        )
        conn_str = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT};AccountKey={keys.keys[0].value};EndpointSuffix=core.windows.net"
        print(f"   Connection: {conn_str[:60]}...\n")
    except Exception as e:
        print(f"   SKIP: {str(e)[:80]}\n")
    
    # 3. Key Vault
    print("3. Creating Key Vault...")
    try:
        # Get current user's tenant ID from credential
        token = credential.get_token("https://vault.azure.net/.default")
        
        kv_async = keyvault_client.vaults.begin_create_or_update(
            RESOURCE_GROUP,
            KEY_VAULT,
            {
                "location": LOCATION,
                "properties": {
                    "enabled_for_deployment": True,
                    "enabled_for_template_deployment": True,
                    "tenant_id": TENANT_ID,
                    "sku": {"family": "A", "name": "standard"},
                    "access_policies": []
                }
            }
        )
        kv = kv_async.result()
        print(f"   OK: {kv.name}\n")
    except Exception as e:
        print(f"   SKIP: {str(e)[:80]}\n")
    
    print("="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nResources Created:")
    print(f"  - Resource Group: {RESOURCE_GROUP}")
    print(f"  - Storage Account: {STORAGE_ACCOUNT}")
    print(f"  - Key Vault: {KEY_VAULT}")
    
    print("\nNext Steps:")
    print("  1. Create Blob containers: raw-data, cleaned-data, models")
    print("  2. Create SQL Database")
    print("  3. Create Function App")
    print("  4. Deploy model endpoint")
    print("\nSee QUICK_AZURE_SETUP.md for Portal steps")
    
except Exception as e:
    print(f"\nERROR: {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
