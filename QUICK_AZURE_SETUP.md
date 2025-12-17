# ⚡ QUICK AZURE SETUP - Portal Method

Since Azure CLI isn't available, here's the fastest way to provision resources using the Azure Portal UI.

**Estimated time: 15-20 minutes**

## ✅ Subscription Info
- **Subscription:** Azure for Students
- **Subscription ID:** 10ceef72-c9cd-4fb6-844b-ee8661d294fc
- **Region:** East US (eastus) or East US 2 (eastus2)

---

## 🚀 Resource Provisioning Steps

### Step 1: Create Resource Group (2 min)
1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Resource Groups"
3. Click **+ Create**
4. **Name:** `rg-engagement-ml`
5. **Region:** `East US` or `East US 2`
6. Click **Review + Create** → **Create**

---

### Step 2: Create Storage Account (3 min)
1. Search for "Storage Accounts"
2. Click **+ Create**
3. **Resource Group:** `rg-engagement-ml`
4. **Name:** `stengagementdata593` (must be globally unique)
5. **Region:** Same as resource group
6. **Performance:** Standard
7. **Redundancy:** Locally-redundant storage (LRS)
8. Click **Create**

**After creation:**
1. Go to storage account → **Access Keys**
2. Copy `Connection string` → Save for `.env`
3. Go to **Containers** → **+ Container**
   - Create: `raw-data`
   - Create: `cleaned-data`
   - Create: `models`

---

### Step 3: Create SQL Database (5 min)
1. Search for "SQL Databases"
2. Click **+ Create**
3. **Resource Group:** `rg-engagement-ml`
4. **Name:** `engagement_db`
5. **Server:** Click **Create new**
   - **Name:** `sql-engagement-593`
   - **Admin login:** `sqladmin`
   - **Password:** Use a strong one (save it!)
6. **Compute:** Select **Free tier** (if available)
7. Click **Create**

**After creation:**
1. Go to SQL Server → **Connection strings**
2. Copy **ADO.NET** string → Save for `.env`
3. Go to SQL Server → **Firewalls and virtual networks**
4. Turn ON "Allow Azure services and resources"

---

### Step 4: Create Key Vault (3 min)
1. Search for "Key Vaults"
2. Click **+ Create**
3. **Resource Group:** `rg-engagement-ml`
4. **Name:** `kv-engagement-593`
5. **Region:** Same as resource group
6. **Pricing:** Standard
7. Click **Create**

**After creation:**
1. Go to Key Vault → **Secrets** → **+ Generate/Import**
2. Add secrets:
   - **Name:** `StorageConnectionString` → **Value:** (paste from step 2)
   - **Name:** `SqlConnectionString` → **Value:** (paste from step 3)
   - **Name:** `SqlPassword` → **Value:** (your SQL password)

---

### Step 5: Create Container Registry (2 min)
1. Search for "Container Registries"
2. Click **+ Create**
3. **Resource Group:** `rg-engagement-ml`
4. **Name:** `crengagement593`
5. **Region:** Same as resource group
6. **SKU:** Basic (free tier eligible)
7. Click **Create**

---

### Step 6: Create ML Workspace (3 min)
1. Search for "Machine Learning"
2. Click **+ Create**
3. **Resource Group:** `rg-engagement-ml`
4. **Workspace name:** `aml-engagement`
5. **Region:** Same as resource group
6. **Storage account:** Select `stengagementdata593`
7. Click **Review + Create** → **Create**

---

### Step 7: Create Functions App (2 min)
1. Search for "Function App"
2. Click **+ Create**
3. **Resource Group:** `rg-engagement-ml`
4. **Function App name:** `func-engagement`
5. **Runtime:** Python 3.11
6. **Region:** Same as resource group
7. **Storage:** Select `stengagementdata593`
8. **Plan:** Consumption (free)
9. Click **Create**

---

### Step 8: Create Application Insights (2 min)
1. Search for "Application Insights"
2. Click **+ Create**
3. **Name:** `ai-engagement`
4. **Resource Group:** `rg-engagement-ml`
5. **Region:** Same as resource group
6. Click **Create**

---

## 📝 Save Your Configuration

Create a `.env` file with your credentials:

```env
# Azure Subscription
AZURE_SUBSCRIPTION_ID=10ceef72-c9cd-4fb6-844b-ee8661d294fc

# Storage
AZURE_STORAGE_ACCOUNT_NAME=stengagementdata593
AZURE_STORAGE_CONNECTION_STRING=your-connection-string

# SQL Database
AZURE_SQL_SERVER=sql-engagement-593.database.windows.net
AZURE_SQL_DATABASE=engagement_db
AZURE_SQL_USER=sqladmin
AZURE_SQL_PASSWORD=your-password

# Key Vault
AZURE_KEYVAULT_URL=https://kv-engagement-593.vault.azure.net/

# ML & Containers
AZURE_ML_WORKSPACE=aml-engagement
AZURE_CONTAINER_REGISTRY=crengagement593.azurecr.io
AZURE_FUNCTION_APP=func-engagement

# Application Insights
AZURE_APPINSIGHTS_KEY=your-instrumentation-key
```

---

## ✅ Verification Checklist

- [ ] Resource Group `rg-engagement-ml` exists
- [ ] Storage account with 3 containers (raw-data, cleaned-data, models)
- [ ] SQL Database accessible
- [ ] Key Vault with secrets stored
- [ ] Container Registry created
- [ ] ML Workspace created
- [ ] Function App created

---

## 💰 Cost Check

**Total: ~$5-10/month on free tiers**

