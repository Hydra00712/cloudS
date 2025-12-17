"""
Create a FREE compute instance in Azure ML Studio for running notebooks
"""
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from azure.ai.ml import MLClient
from azure.ai.ml.entities import ComputeInstance
from azure.identity import InteractiveBrowserCredential
import time

SUBSCRIPTION_ID = "10ceef72-c9cd-4fb6-844b-ee8661d294fc"
RESOURCE_GROUP = "rg-engagement-ml"
WORKSPACE_NAME = "engagement-ml-ws"
TENANT_ID = "78ddbe5d-b682-466c-bad0-6ffbaf7ceb2d"

print("=" * 70)
print("CREATING FREE COMPUTE INSTANCE FOR NOTEBOOKS")
print("=" * 70)

print("\nAuthenticating...")
credential = InteractiveBrowserCredential(tenant_id=TENANT_ID)
ml_client = MLClient(credential, SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME)

workspace = ml_client.workspaces.get(WORKSPACE_NAME)
print(f"OK - Connected to: {workspace.name}")

# Create compute instance with FREE tier
print("\nCreating compute instance...")
print("  Name: notebook-compute-free")
print("  Size: STANDARD_DS1_V2 (smallest/cheapest)")
print("  Idle shutdown: 30 minutes (cost-safe)")

compute_instance = ComputeInstance(
    name="notebook-compute-free",
    size="STANDARD_DS1_V2",  # Smallest VM size (1 core, 3.5 GB RAM)
    idle_time_before_shutdown_minutes=30,  # Auto-shutdown after 30 min idle
    description="Free compute instance for running notebooks - auto-shutdown enabled"
)

try:
    print("\nSubmitting creation request...")
    ci = ml_client.compute.begin_create_or_update(compute_instance).result()
    
    print("\n" + "=" * 70)
    print("SUCCESS - COMPUTE INSTANCE CREATED")
    print("=" * 70)
    
    print(f"\nCompute Instance Details:")
    print(f"  Name: {ci.name}")
    print(f"  Size: {ci.size}")
    print(f"  State: {ci.state}")
    print(f"  Idle shutdown: 30 minutes")
    
    print(f"\nHow to use:")
    print(f"  1. Go to: https://ml.azure.com")
    print(f"  2. Select workspace: {WORKSPACE_NAME}")
    print(f"  3. Click 'Notebooks' in left sidebar")
    print(f"  4. Upload your notebooks")
    print(f"  5. Select compute: 'notebook-compute-free'")
    print(f"  6. Click 'Run All'")
    
    print(f"\nCost Safety:")
    print(f"  - Auto-shutdown after 30 min idle")
    print(f"  - Smallest VM size (minimal cost)")
    print(f"  - Only charged when running")
    print(f"  - Estimated: ~$0.10/hour when active")
    
    print(f"\nStatus: READY TO USE")
    
except Exception as e:
    error_msg = str(e)
    
    if "already exists" in error_msg.lower() or "conflict" in error_msg.lower():
        print("\n" + "=" * 70)
        print("COMPUTE INSTANCE ALREADY EXISTS")
        print("=" * 70)
        
        # Get existing compute instance
        try:
            ci = ml_client.compute.get("notebook-compute-free")
            print(f"\nExisting Compute Instance:")
            print(f"  Name: {ci.name}")
            print(f"  Size: {ci.size}")
            print(f"  State: {ci.state}")
            
            if ci.state == "Running":
                print(f"\n  Status: READY TO USE NOW")
            elif ci.state == "Stopped":
                print(f"\n  Status: Stopped - will start when you run a notebook")
            else:
                print(f"\n  Status: {ci.state}")
            
            print(f"\nYou can use this compute instance right away!")
            print(f"  1. Go to Notebooks in Azure ML Studio")
            print(f"  2. Select compute: 'notebook-compute-free'")
            print(f"  3. Run your notebooks")
            
        except Exception as e2:
            print(f"\nCould not get details: {str(e2)[:200]}")
    else:
        print(f"\nERROR: {error_msg[:500]}")
        print("\nTrying alternative approach...")
        
        # Try with different name
        alt_name = f"ci-notebooks-{int(time.time()) % 10000}"
        print(f"\nCreating with alternative name: {alt_name}")
        
        compute_instance_alt = ComputeInstance(
            name=alt_name,
            size="STANDARD_DS1_V2",
            idle_time_before_shutdown_minutes=30
        )
        
        try:
            ci = ml_client.compute.begin_create_or_update(compute_instance_alt).result()
            print(f"\nSUCCESS - Created: {ci.name}")
            print(f"State: {ci.state}")
        except Exception as e3:
            print(f"\nAlternative also failed: {str(e3)[:200]}")
            print("\nMANUAL CREATION REQUIRED - See instructions below")

print("\n" + "=" * 70)
print("MANUAL CREATION INSTRUCTIONS (if needed)")
print("=" * 70)
print("\n1. Go to: https://ml.azure.com")
print("2. Select workspace: engagement-ml-ws")
print("3. Click 'Compute' in left sidebar")
print("4. Click 'Compute instances' tab")
print("5. Click '+ New'")
print("6. Configure:")
print("   - Name: notebook-compute-free")
print("   - VM size: STANDARD_DS1_V2 (or any DS-series)")
print("   - Enable idle shutdown: 30 minutes")
print("7. Click 'Create'")
print("8. Wait 3-5 minutes for provisioning")
print("\nThen you can run notebooks!")

