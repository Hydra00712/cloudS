"""
List existing Azure resources in your account
"""

import subprocess
import sys
import os

packages = ["azure-identity==1.15.0", "azure-mgmt-resource==23.3.0"]
for pkg in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], 
                  stderr=subprocess.DEVNULL)

from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient

SUBSCRIPTION_ID = "10ceef72-c9cd-4fb6-844b-ee8661d294fc"
TENANT_ID = "78ddbe5d-b682-466c-bad0-6ffbaf7ceb2d"

print("\nListing your Azure resources...\n")
print("Note: Browser auth will cache credentials for future use.\n")

try:
    credential = InteractiveBrowserCredential(tenant_id=TENANT_ID)
    client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
    
    print("Resource Groups:")
    for rg in client.resource_groups.list():
        print(f"  - {rg.name} ({rg.location})")
    
    print("\nAll Resources:")
    for resource in client.resources.list():
        print(f"  - {resource.name} ({resource.type})")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
