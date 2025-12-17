#!/bin/bash
# ============================================================================
# AZURE CLOUD DATA-DRIVEN APPLICATION SETUP
# Complete provisioning script for Social Media Engagement ML Project
# ============================================================================

# SET VARIABLES
RESOURCE_GROUP="rg-engagement-ml"
LOCATION="eastus2"  # Free tier availability
STORAGE_ACCOUNT="stengagementdata$(date +%s | tail -c 4)"  # Unique name
SQL_SERVER="sql-engagement-$(date +%s | tail -c 4)"
SQL_DATABASE="engagement_db"
ML_WORKSPACE="aml-engagement"
ACR_NAME="crengagement$(date +%s | tail -c 4)"  # Container Registry
KEY_VAULT="kv-engagement-$(date +%s | tail -c 4)"

# ============================================================================
# 1. CREATE RESOURCE GROUP
# ============================================================================
echo "📦 Creating Resource Group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"

# ============================================================================
# 2. AZURE STORAGE ACCOUNT (Collect & Store)
# ============================================================================
echo "💾 Creating Storage Account..."
az storage account create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$STORAGE_ACCOUNT" \
  --location "$LOCATION" \
  --sku "Standard_LRS" \
  --access-tier "Hot" \
  --kind "StorageV2"

# Get storage account key
STORAGE_KEY=$(az storage account keys list \
  --resource-group "$RESOURCE_GROUP" \
  --account-name "$STORAGE_ACCOUNT" \
  --query "[0].value" -o tsv)

# Create blob containers
echo "📁 Creating Blob Containers..."
for container in raw-data processed-data models; do
  az storage container create \
    --account-name "$STORAGE_ACCOUNT" \
    --account-key "$STORAGE_KEY" \
    --name "$container"
done

# ============================================================================
# 3. AZURE SQL DATABASE (Structured data storage)
# ============================================================================
echo "🗄️ Creating Azure SQL Database..."

# Create SQL Server
az sql server create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SQL_SERVER" \
  --location "$LOCATION" \
  --admin-user "sqladmin" \
  --admin-password "P@ssw0rd123!" \
  --enable-public-endpoint true

# Allow Azure services to access
az sql server firewall-rule create \
  --resource-group "$RESOURCE_GROUP" \
  --server "$SQL_SERVER" \
  --name "AllowAzureServices" \
  --start-ip-address "0.0.0.0" \
  --end-ip-address "0.0.0.0"

# Create database (Free tier: 100 DTUs)
az sql db create \
  --resource-group "$RESOURCE_GROUP" \
  --server "$SQL_SERVER" \
  --name "$SQL_DATABASE" \
  --service-objective "Basic" \
  --edition "Basic"

SQL_CONNECTION_STRING="Server=tcp:${SQL_SERVER}.database.windows.net,1433;Initial Catalog=${SQL_DATABASE};Persist Security Info=False;User ID=sqladmin;Password=P@ssw0rd123!;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"

# ============================================================================
# 4. AZURE KEY VAULT (Security)
# ============================================================================
echo "🔐 Creating Key Vault..."
az keyvault create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$KEY_VAULT" \
  --location "$LOCATION" \
  --sku "standard" \
  --enable-rbac-authorization false

# Store secrets
az keyvault secret set \
  --vault-name "$KEY_VAULT" \
  --name "StorageAccountKey" \
  --value "$STORAGE_KEY"

az keyvault secret set \
  --vault-name "$KEY_VAULT" \
  --name "SqlConnectionString" \
  --value "$SQL_CONNECTION_STRING"

# ============================================================================
# 5. AZURE CONTAINER REGISTRY (For CI/CD)
# ============================================================================
echo "🐳 Creating Container Registry..."
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku "Basic" \
  --location "$LOCATION"

# ============================================================================
# 6. AZURE MACHINE LEARNING WORKSPACE
# ============================================================================
echo "🤖 Creating Machine Learning Workspace..."

# Create default storage & key vault for ML (required)
az storage account create \
  --resource-group "$RESOURCE_GROUP" \
  --name "staml$(date +%s | tail -c 4)" \
  --location "$LOCATION" \
  --sku "Standard_LRS" \
  --kind "StorageV2"

az keyvault create \
  --resource-group "$RESOURCE_GROUP" \
  --name "kvml$(date +%s | tail -c 4)" \
  --location "$LOCATION" \
  --sku "standard"

# Create App Insights
APP_INSIGHTS=$(az monitor app-insights component create \
  --resource-group "$RESOURCE_GROUP" \
  --app "ai-engagement" \
  --location "$LOCATION" \
  --query "id" -o tsv)

# Create ML workspace
az ml workspace create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ML_WORKSPACE" \
  --location "$LOCATION" \
  --application-insights "$APP_INSIGHTS"

# ============================================================================
# 7. AZURE FUNCTIONS APP (Inference)
# ============================================================================
echo "⚡ Creating Azure Functions..."

FUNCTION_APP="func-engagement"
FUNCTION_STORAGE="stfunc$(date +%s | tail -c 4)"

az storage account create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$FUNCTION_STORAGE" \
  --location "$LOCATION" \
  --sku "Standard_LRS"

az functionapp create \
  --resource-group "$RESOURCE_GROUP" \
  --consumption-plan-location "$LOCATION" \
  --runtime "python" \
  --runtime-version "3.11" \
  --functions-version "4" \
  --name "$FUNCTION_APP" \
  --storage-account "$FUNCTION_STORAGE"

# ============================================================================
# 8. DISPLAY OUTPUTS FOR CONFIGURATION
# ============================================================================
echo ""
echo "=========================================="
echo "✅ AZURE SETUP COMPLETE"
echo "=========================================="
echo ""
echo "📋 Configuration Details:"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "SQL Server: $SQL_SERVER"
echo "SQL Database: $SQL_DATABASE"
echo "ML Workspace: $ML_WORKSPACE"
echo "Function App: $FUNCTION_APP"
echo "Container Registry: $ACR_NAME"
echo "Key Vault: $KEY_VAULT"
echo ""
echo "🔑 Connection Strings:"
echo "Storage: $STORAGE_ACCOUNT"
echo "SQL: $SQL_CONNECTION_STRING"
echo ""
echo "💾 Save these for your .env file!"
echo "=========================================="
