"""
Simple Azure Setup - Create resources one by one
Run: python setup_simple.py
"""

import subprocess
import sys

print("\n" + "="*70)
print("AZURE RESOURCE SETUP - Python SDK")
print("="*70 + "\n")

# Install packages silently
print("Setting up Azure SDKs...")
packages = [
    "azure-identity==1.15.0",
    "azure-mgmt-resource==23.1.0",
    "azure-mgmt-storage==21.1.0",
]

for pkg in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], 
                  stderr=subprocess.DEVNULL)

print("SDKs ready.\n")

# Now use the SDK
import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

SUBSCRIPTION_ID = "10ceef72-c9cd-4fb6-844b-ee8661d294fc"
TENANT_ID = "78ddbe5d-b682-466c-bad0-6ffbaf7ceb2d"
RESOURCE_GROUP = "rg-engagement-ml"
LOCATION = "eastus"

print(f"Subscription ID: {SUBSCRIPTION_ID}")
print(f"Tenant ID: {TENANT_ID}")
print(f"Resource Group: {RESOURCE_GROUP}")
print(f"Location: {LOCATION}\n")

try:
    print("Authenticating to Azure (using cached credentials)...")
    os.environ['AZURE_TENANT_ID'] = TENANT_ID
    credential = DefaultAzureCredential()
    
    print("Creating Resource Management client...")
    resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
    
    print(f"Creating resource group '{RESOURCE_GROUP}' in {LOCATION}...")
    rg = resource_client.resource_groups.create_or_update(
        RESOURCE_GROUP,
        {"location": LOCATION}
    )
    
    print("SUCCESS!")
    print(f"\nResource Group Created:")
    print(f"  Name: {rg.name}")
    print(f"  Location: {rg.location}")
    print(f"  ID: {rg.id}")
    
    print("\n" + "="*70)
    print("Next: Create Storage, SQL, Key Vault via Portal or continue scripting")
    print("="*70)
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Make sure you have internet connection")
    print("2. Check if browser login appears")
    print("3. If not, try: python setup_simple.py")
    sys.exit(1)
