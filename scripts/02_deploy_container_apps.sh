#!/bin/bash
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
#   ./06_deploy_container_apps.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
WEBAPP_DIR="$ROOT_DIR/app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Deploying to Azure Container Apps${NC}"
echo -e "${GREEN}============================================${NC}"

# Load environment variables from azd
AZURE_DIR="$ROOT_DIR/.azure"
if [ -f "$AZURE_DIR/config.json" ]; then
    ENV_NAME=$(python3 -c "import json; print(json.load(open('$AZURE_DIR/config.json'))['defaultEnvironment'])")
    ENV_FILE="$AZURE_DIR/$ENV_NAME/.env"
    
    if [ -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}Loading environment from: $ENV_FILE${NC}"
        set -a
        source "$ENV_FILE"
        set +a
    fi
fi

# Validate required environment variables
if [ -z "$AZURE_CONTAINER_REGISTRY_NAME" ]; then
    echo -e "${RED}Error: AZURE_CONTAINER_REGISTRY_NAME not set. Run 'azd up' first to provision infrastructure.${NC}"
    exit 1
fi

if [ -z "$AZURE_RESOURCE_GROUP" ]; then
    echo -e "${RED}Error: AZURE_RESOURCE_GROUP not set.${NC}"
    exit 1
fi

if [ -z "$AZURE_CONTAINER_APP_NAME" ]; then
    echo -e "${RED}Error: AZURE_CONTAINER_APP_NAME not set.${NC}"
    exit 1
fi

if [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo -e "${RED}Error: AZURE_OPENAI_ENDPOINT not set.${NC}"
    exit 1
fi

if [ -z "$AZURE_AI_SEARCH_ENDPOINT" ]; then
    echo -e "${RED}Error: AZURE_AI_SEARCH_ENDPOINT not set.${NC}"
    exit 1
fi

if [ -z "$AZURE_APPINSIGHTS_CONNECTION_STRING" ]; then
    echo -e "${YELLOW}Warning: AZURE_APPINSIGHTS_CONNECTION_STRING not set. Tracing will be disabled.${NC}"
fi

echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Resource Group:     $AZURE_RESOURCE_GROUP"
echo "  Container Registry: $AZURE_CONTAINER_REGISTRY_NAME"
echo "  Container App:      $AZURE_CONTAINER_APP_NAME"
echo "  OpenAI Endpoint:    $AZURE_OPENAI_ENDPOINT"
echo "  Search Endpoint:    $AZURE_AI_SEARCH_ENDPOINT"
echo "  Chat Model:         ${AZURE_CHAT_MODEL:-gpt-4o-mini}"
echo "  App Insights:       ${AZURE_APPINSIGHTS_CONNECTION_STRING:-(not configured)}"
echo ""

ACR_LOGIN_SERVER=$(az acr show --name "$AZURE_CONTAINER_REGISTRY_NAME" --query loginServer -o tsv)

# Navigate to app directory
cd "$WEBAPP_DIR"

# Build image using ACR Build Tasks (no local Docker required)
echo ""
echo -e "${YELLOW}Building combined Streamlit + FastAPI image in Azure...${NC}"
az acr build \
    --registry "$AZURE_CONTAINER_REGISTRY_NAME" \
    --image app:latest \
    --file Dockerfile \
    .

# Update Container App with new image and environment variables
echo ""
echo -e "${YELLOW}Updating Container App with environment variables...${NC}"
az containerapp update \
    --name "$AZURE_CONTAINER_APP_NAME" \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --image "$ACR_LOGIN_SERVER/app:latest" \
    --set-env-vars \
        "AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT" \
        "AZURE_AI_SEARCH_ENDPOINT=$AZURE_AI_SEARCH_ENDPOINT" \
        "AZURE_OPENAI_CHAT_DEPLOYMENT=${AZURE_CHAT_MODEL:-gpt-5.4-mini}" \
        "AZURE_SEARCH_INDEX_NAME=${AZURE_SEARCH_INDEX_NAME:-documents}" \
        "APPLICATIONINSIGHTS_CONNECTION_STRING=$AZURE_APPINSIGHTS_CONNECTION_STRING"

# Get the app URL
APP_URL=$(az containerapp show \
    --name "$AZURE_CONTAINER_APP_NAME" \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}Your Application URL:${NC} https://$APP_URL"
echo ""
echo -e "${YELLOW}Available Endpoints:${NC}"
echo "  Streamlit UI:   https://$APP_URL/"
echo "  FastAPI Chat:   https://$APP_URL/chat"
echo "  API Docs:       https://$APP_URL/docs"
echo "  Health Check:   https://$APP_URL/api/health"
echo ""
echo -e "${YELLOW}Note:${NC} It may take a few minutes for the app to start."
echo ""
echo "View logs:"
echo "  az containerapp logs show -n $AZURE_CONTAINER_APP_NAME -g $AZURE_RESOURCE_GROUP --follow"
echo -e "${GREEN}============================================${NC}"
