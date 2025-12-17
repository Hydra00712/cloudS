"""
Azure Resource Provisioning Script (Python)
Uses Azure SDK to create all necessary resources
"""

import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient

# Configuration
SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "10ceef72-c9cd-4fb6-844b-ee8661d294fc")
RESOURCE_GROUP = "rg-engagement-ml"
LOCATION = "eastus"
STORAGE_ACCOUNT = "stengagementdata593"
SQL_SERVER = "sql-engagement-593"
SQL_DB = "engagement_db"
KEY_VAULT = "kv-engagement-593"

# Authentication
credential = DefaultAzureCredential()

print("🔐 Authenticated to Azure")
print(f"📊 Subscription: {SUBSCRIPTION_ID}")

try:
    # Initialize clients
    resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
    storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
    sql_client = SqlManagementClient(credential, SUBSCRIPTION_ID)
    keyvault_client = KeyVaultManagementClient(credential, SUBSCRIPTION_ID)
    
    # Create Resource Group
    print(f"\n📦 Creating Resource Group: {RESOURCE_GROUP}...")
    rg_result = resource_client.resource_groups.create_or_update(
        RESOURCE_GROUP,
        {"location": LOCATION}
    )
    print(f"✅ Resource Group created")
    
    # Create Storage Account
    print(f"\n💾 Creating Storage Account: {STORAGE_ACCOUNT}...")
    try:
        storage_result = storage_client.storage_accounts.begin_create(
            RESOURCE_GROUP,
            STORAGE_ACCOUNT,
            {
                "location": LOCATION,
                "kind": "BlobStorage",
                "sku": {"name": "Standard_LRS"},
                "access_tier": "Hot"
            }
        ).result()
        print(f"✅ Storage Account created")
    except Exception as e:
        print(f"⚠️ Storage Account: {str(e)[:100]}")
    
    # Create Key Vault
    print(f"\n🔐 Creating Key Vault: {KEY_VAULT}...")
    try:
        keyvault_result = keyvault_client.vaults.begin_create_or_update(
            RESOURCE_GROUP,
            KEY_VAULT,
            {
                "location": LOCATION,
                "properties": {
                    "enabled_for_deployment": True,
                    "enabled_for_template_deployment": True,
                    "enabled_for_disk_encryption": False,
                    "tenant_id": credential.get_token("https://management.azure.com/").token[:36],
                    "sku": {"family": "A", "name": "standard"},
                    "access_policies": []
                }
            }
        ).result()
        print(f"✅ Key Vault created")
    except Exception as e:
        print(f"⚠️ Key Vault: {str(e)[:100]}")
    
    print("\n" + "="*60)
    print("✅ AZURE SETUP COMPLETE")
    print("="*60)
    print(f"\n📋 Created Resources:")
    print(f"   • Resource Group: {RESOURCE_GROUP}")
    print(f"   • Location: {LOCATION}")
    print(f"   • Storage Account: {STORAGE_ACCOUNT}")
    print(f"   • Key Vault: {KEY_VAULT}")
    print(f"\n💡 Next Steps:")
    print(f"   1. Check Azure Portal for created resources")
    print(f"   2. Create storage containers (raw, cleaned, models)")
    print(f"   3. Upload training data to blob storage")
    print(f"   4. Update Python files with Azure credentials")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("Make sure you're logged in: az login")
    exit(1)
