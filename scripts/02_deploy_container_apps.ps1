# Deploy Streamlit + FastAPI to Azure Container Apps
#
# This script builds and deploys the combined container image to Azure Container Apps.
# Uses ACR build tasks (no local Docker required)
#
# Prerequisites:
#   - Azure CLI installed and logged in
#   - azd environment provisioned with Container Apps (run 'azd up' first)
#
# Usage:
#   .\02_deploy_container_apps.ps1

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ROOT_DIR = Split-Path -Parent $SCRIPT_DIR
$WEBAPP_DIR = Join-Path $ROOT_DIR "app"

# Colors for output
$RED = [System.ConsoleColor]::Red
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow

Write-Host "============================================" -ForegroundColor $GREEN
Write-Host "Deploying to Azure Container Apps" -ForegroundColor $GREEN
Write-Host "============================================" -ForegroundColor $GREEN

# Load environment variables from azd
$AZURE_DIR = Join-Path $ROOT_DIR ".azure"
$CONFIG_JSON = Join-Path $AZURE_DIR "config.json"

if (Test-Path $CONFIG_JSON) {
    try {
        $configContent = Get-Content $CONFIG_JSON -Raw | ConvertFrom-Json
        $ENV_NAME = $configContent.defaultEnvironment
        $ENV_FILE = Join-Path $AZURE_DIR $ENV_NAME ".env"
        
        if (Test-Path $ENV_FILE) {
            Write-Host "Loading environment from: $ENV_FILE" -ForegroundColor $YELLOW
            Get-Content $ENV_FILE | ForEach-Object {
                if ($_ -match '^\s*$' -or $_ -match '^\s*#') {
                    return
                }
                $parts = $_ -split '=', 2
                if ($parts.Count -eq 2) {
                    $name = $parts[0].Trim()
                    $value = $parts[1].Trim()
                    [Environment]::SetEnvironmentVariable($name, $value, "Process")
                }
            }
        }
    }
    catch {
        Write-Host "Warning: Could not load environment from config.json" -ForegroundColor $YELLOW
    }
}

# Validate required environment variables
$requiredVars = @(
    "AZURE_CONTAINER_REGISTRY_NAME",
    "AZURE_RESOURCE_GROUP",
    "AZURE_CONTAINER_APP_NAME",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_AI_SEARCH_ENDPOINT"
)

foreach ($var in $requiredVars) {
    if (-not (Test-Path env:$var) -or [string]::IsNullOrEmpty((Get-Item env:$var).Value)) {
        Write-Host "Error: $var not set. Run 'azd up' first to provision infrastructure." -ForegroundColor $RED
        exit 1
    }
}

if (-not (Test-Path env:AZURE_APPINSIGHTS_CONNECTION_STRING) -or [string]::IsNullOrEmpty((Get-Item env:AZURE_APPINSIGHTS_CONNECTION_STRING).Value)) {
    Write-Host "Warning: AZURE_APPINSIGHTS_CONNECTION_STRING not set. Tracing will be disabled." -ForegroundColor $YELLOW
}

Write-Host ""
Write-Host "Configuration:" -ForegroundColor $YELLOW
Write-Host "  Resource Group:     $env:AZURE_RESOURCE_GROUP"
Write-Host "  Container Registry: $env:AZURE_CONTAINER_REGISTRY_NAME"
Write-Host "  Container App:      $env:AZURE_CONTAINER_APP_NAME"
Write-Host "  OpenAI Endpoint:    $env:AZURE_OPENAI_ENDPOINT"
Write-Host "  Search Endpoint:    $env:AZURE_AI_SEARCH_ENDPOINT"
Write-Host "  Chat Model:         $(if ($env:AZURE_CHAT_MODEL) { $env:AZURE_CHAT_MODEL } else { 'gpt-5.1' })"
$appInsights = if ($env:AZURE_APPINSIGHTS_CONNECTION_STRING) { $env:AZURE_APPINSIGHTS_CONNECTION_STRING } else { "(not configured)" }
Write-Host "  App Insights:       $appInsights"
Write-Host ""

# Get ACR login server
$ACR_LOGIN_SERVER = az acr show --name $env:AZURE_CONTAINER_REGISTRY_NAME --query loginServer -o tsv

# Navigate to app directory
Set-Location $WEBAPP_DIR

# Build image using ACR Build Tasks (no local Docker required)
Write-Host ""
Write-Host "Building combined Streamlit + FastAPI image in Azure..." -ForegroundColor $YELLOW
az acr build `
    --registry $env:AZURE_CONTAINER_REGISTRY_NAME `
    --image app:latest `
    --file Dockerfile `
    .

# Update Container App with new image and environment variables
Write-Host ""
Write-Host "Updating Container App with environment variables..." -ForegroundColor $YELLOW

$chatModel = if ($env:AZURE_CHAT_MODEL) { $env:AZURE_CHAT_MODEL } else { "gpt-5.1" }
$searchIndex = if ($env:AZURE_SEARCH_INDEX_NAME) { $env:AZURE_SEARCH_INDEX_NAME } else { "documents" }

az containerapp update `
    --name $env:AZURE_CONTAINER_APP_NAME `
    --resource-group $env:AZURE_RESOURCE_GROUP `
    --image "$ACR_LOGIN_SERVER/app:latest" `
    --set-env-vars `
        "AZURE_OPENAI_ENDPOINT=$env:AZURE_OPENAI_ENDPOINT" `
        "AZURE_AI_SEARCH_ENDPOINT=$env:AZURE_AI_SEARCH_ENDPOINT" `
        "AZURE_OPENAI_CHAT_DEPLOYMENT=$chatModel" `
        "AZURE_SEARCH_INDEX_NAME=$searchIndex" `
        "APPLICATIONINSIGHTS_CONNECTION_STRING=$env:AZURE_APPINSIGHTS_CONNECTION_STRING"

# Get the app URL
$APP_URL = az containerapp show `
    --name $env:AZURE_CONTAINER_APP_NAME `
    --resource-group $env:AZURE_RESOURCE_GROUP `
    --query "properties.configuration.ingress.fqdn" -o tsv

Write-Host ""
Write-Host "============================================" -ForegroundColor $GREEN
Write-Host "Deployment Complete!" -ForegroundColor $GREEN
Write-Host "============================================" -ForegroundColor $GREEN
Write-Host ""
Write-Host "Your Application URL: https://$APP_URL" -ForegroundColor $YELLOW
Write-Host ""
Write-Host "Available Endpoints:" -ForegroundColor $YELLOW
Write-Host "  Streamlit UI:   https://$APP_URL/"
Write-Host "  FastAPI Chat:   https://$APP_URL/chat"
Write-Host "  API Docs:       https://$APP_URL/docs"
Write-Host "  Health Check:   https://$APP_URL/api/health"
Write-Host ""
Write-Host "Note: It may take a few minutes for the app to start." -ForegroundColor $YELLOW
Write-Host ""
Write-Host "View logs:"
Write-Host "  az containerapp logs show -n $env:AZURE_CONTAINER_APP_NAME -g $env:AZURE_RESOURCE_GROUP --follow"
Write-Host "============================================" -ForegroundColor $GREEN
