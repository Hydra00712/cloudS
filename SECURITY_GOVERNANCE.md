# 🔐 10️⃣ SECURITY & GOVERNANCE STRATEGY

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Layer 1: IDENTITY & ACCESS (Azure Entra ID + RBAC)      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ • Your User Account: Contributor role (full access)     │   │
│  │ • Function App Managed Identity: Key Vault Reader       │   │
│  │ • ML Workspace Identity: Storage Blob Data Reader       │   │
│  │ • App Service Identity: Secrets Reader (no hardcodes)   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Layer 2: SECRETS MANAGEMENT (Azure Key Vault)           │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ Stored Secrets:                                          │   │
│  │ • storage-account-key (read-only)                       │   │
│  │ • sql-connection-string (encrypted)                     │   │
│  │ • ml-endpoint-key (API authentication)                  │   │
│  │ • github-actions-secret (CI/CD automation)              │   │
│  │                                                          │   │
│  │ Rotation Policy: 90 days                                │   │
│  │ Audit: All access logged in Azure Monitor              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Layer 3: NETWORK SECURITY                               │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ • SQL Firewall: Only Azure services access allowed      │   │
│  │ • Storage Account: Private endpoint (optional)          │   │
│  │ • API Endpoints: Authentication required                │   │
│  │ • HTTPS only (TLS 1.2 minimum)                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Layer 4: DATA PROTECTION                                │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ • Encryption at Rest: Storage (AES-256)                 │   │
│  │ • Encryption in Transit: HTTPS/TLS                      │   │
│  │ • Database: TDE (Transparent Data Encryption)           │   │
│  │ • Backups: Geo-redundant (automatic)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Layer 5: AUDIT & COMPLIANCE                             │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ • Activity Log: All resource changes tracked            │   │
│  │ • Access Review: Who accessed what, when                │   │
│  │ • Data Lineage: Source → Processing → Storage          │   │
│  │ • Model Versioning: Every model registered w/ timestamp │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Step 1: Create Managed Identities

```bash
# Function App Managed Identity (auto-created, no manual step)
# Enable it:
az functionapp identity assign \
  --resource-group rg-engagement-ml \
  --name func-engagement

# ML Workspace Managed Identity (auto-created)
```

### Step 2: Setup Key Vault Access Policies

```bash
# Get the principal IDs
FUNCTION_PRINCIPAL=$(az functionapp identity show \
  --resource-group rg-engagement-ml \
  --name func-engagement \
  --query principalId -o tsv)

ML_PRINCIPAL=$(az ml workspace show \
  --resource-group rg-engagement-ml \
  --name aml-engagement \
  --query identityPrincipalId -o tsv)

# Grant Function App access to Key Vault
az keyvault set-policy \
  --name kv-engagement-xxxx \
  --object-id $FUNCTION_PRINCIPAL \
  --secret-permissions get list

# Grant ML Workspace access to Key Vault
az keyvault set-policy \
  --name kv-engagement-xxxx \
  --object-id $ML_PRINCIPAL \
  --secret-permissions get list
```

### Step 3: Disable Public Access to Storage (Optional)

```bash
# Restrict to Azure services only
az storage account update \
  --resource-group rg-engagement-ml \
  --name stengagementdata \
  --public-blob-access false
```

### Step 4: Enable SQL Firewall Rules

```bash
# Allow only Azure services
az sql server firewall-rule create \
  --resource-group rg-engagement-ml \
  --server sql-engagement-xxxx \
  --name "AllowAzureServices" \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Your IP (for local testing)
az sql server firewall-rule create \
  --resource-group rg-engagement-ml \
  --server sql-engagement-xxxx \
  --name "MyIPAddress" \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

## Code Patterns (Security Best Practices)

### Pattern 1: Retrieve Secret from Key Vault

**❌ BAD:**
```python
SQL_PASSWORD = "P@ssw0rd123!"  # Hardcoded!
```

**✅ GOOD:**
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
secret_client = SecretClient(
    vault_url="https://kv-engagement.vault.azure.net/",
    credential=credential
)

sql_password = secret_client.get_secret("sql-password").value
```

### Pattern 2: Function App with Managed Identity

**Function code:**
```python
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    # No explicit credentials needed!
    credential = DefaultAzureCredential()
    
    # Authenticate via Managed Identity
    blob_service = BlobServiceClient(
        account_url="https://stengagementdata.blob.core.windows.net/",
        credential=credential
    )
    
    container = blob_service.get_container_client("models")
    blob_list = container.list_blobs()
    
    return func.HttpResponse("✅ Accessed blob storage")
```

### Pattern 3: CI/CD Secret Injection

**GitHub Actions:**
```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy Function
      run: |
        az functionapp config appsettings set \
          --resource-group $RG \
          --name $FUNC_NAME \
          --settings \
            "KeyVaultUri=https://kv-engagement.vault.azure.net/" \
            "StorageAccount=$STORAGE_ACCOUNT" \
            "ManagedIdentityClientId=$CLIENT_ID"
```

## Role-Based Access Control (RBAC)

```
Azure Subscription
│
├─ Resource Group: rg-engagement-ml
│
│  ├─ Role: Contributor (Your Account)
│  │  └─ Permissions: Create, delete, modify all resources
│  │
│  ├─ Role: Storage Blob Data Reader (ML Workspace)
│  │  └─ Permissions: Read training data only
│  │
│  ├─ Role: Key Vault Secrets User (Function App)
│  │  └─ Permissions: Get secrets, no delete
│  │
│  └─ Role: Reader (Auditors/Professors)
│     └─ Permissions: View resources, no modifications
```

## Data Governance Checklist

| Control | Implementation | Verification |
|---|---|---|
| **Data Classification** | PII (none), Non-PII (posts) | Document in README |
| **Access Control** | RBAC roles assigned | Run `az role assignment list` |
| **Encryption** | At-rest (Storage), In-transit (HTTPS) | Check Storage settings |
| **Audit Trail** | Activity Log enabled | Show professor Activity Log |
| **Data Retention** | Auto-delete after 90 days | Set lifecycle policy |
| **Backup** | Geo-redundant storage | Azure handles automatically |
| **Incident Response** | Alert on errors | Monitor dashboard shows alerts |

## Compliance Aspects

### For Academic Projects:

| Requirement | Your Approach |
|---|---|
| **Data Privacy** | No sensitive PII; synthetic social media data |
| **Access Control** | RBAC enforced; audit trail preserved |
| **Data Encryption** | Azure default encryption at rest/transit |
| **Change Management** | Git history + CI/CD pipeline logs |
| **Monitoring** | Application Insights logs all access |

### What to Show Professor:

1. **Key Vault screenshot** - Show stored secrets (not values)
2. **RBAC roles screenshot** - Show who has access
3. **Activity Log** - Show all resource changes
4. **Monitoring dashboard** - Show security alerts (none = healthy)

## Sensitive Information Handling

### Do NOT commit to GitHub:
- ❌ API keys
- ❌ Connection strings
- ❌ Passwords
- ❌ Storage account keys

### How to handle:
```
GitHub Secrets (encrypted)
    ↓
Environment variables
    ↓
Azure Key Vault (encrypted)
    ↓
Application runtime (in-memory only)
```

### `.gitignore` for safety:
```
.env
*.pkl
credentials.json
secrets/
```

## Security Testing Checklist

Before submitting for grading:

- [ ] No hardcoded credentials in code
- [ ] All secrets in Key Vault
- [ ] RBAC roles assigned appropriately
- [ ] Firewall rules configured
- [ ] HTTPS only for endpoints
- [ ] Activity Log shows audit trail
- [ ] No public access to storage
- [ ] GitHub Actions use service principal
- [ ] Monitoring alerts configured

