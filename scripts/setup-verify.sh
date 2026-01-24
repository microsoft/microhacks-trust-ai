#!/bin/bash
# =============================================================================
# Microhacks Trust AI - Prerequisites Setup & Verification Script
# =============================================================================
# Usage:
#   ./scripts/setup-verify.sh           # Verify only (no installation)
#   ./scripts/setup-verify.sh --install # Verify and install missing tools
#   ./scripts/setup-verify.sh --help    # Show help
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
INSTALL_MODE=false
VERBOSE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --install|-i)
            INSTALL_MODE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Microhacks Trust AI - Prerequisites Setup & Verification Script"
            echo ""
            echo "Usage:"
            echo "  $0              Verify prerequisites only"
            echo "  $0 --install    Verify and install missing tools"
            echo "  $0 --verbose    Show detailed output"
            echo "  $0 --help       Show this help message"
            exit 0
            ;;
    esac
done

# Track overall status
ALL_PASSED=true
declare -A STATUS

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}=============================================="
    echo -e "🔍 $1"
    echo -e "==============================================${NC}"
}

print_check() {
    local name=$1
    local status=$2
    local version=$3
    
    if [ "$status" = "PASS" ]; then
        echo -e "  ${GREEN}✅ $name${NC} - $version"
        STATUS[$name]="PASS"
    elif [ "$status" = "WARN" ]; then
        echo -e "  ${YELLOW}⚠️  $name${NC} - $version"
        STATUS[$name]="WARN"
    else
        echo -e "  ${RED}❌ $name${NC} - NOT INSTALLED"
        STATUS[$name]="FAIL"
        ALL_PASSED=false
    fi
}

install_tool() {
    local name=$1
    local install_cmd=$2
    
    if [ "$INSTALL_MODE" = true ]; then
        echo -e "${YELLOW}📦 Installing $name...${NC}"
        eval "$install_cmd"
        echo -e "${GREEN}✅ $name installed successfully${NC}"
    else
        echo -e "${YELLOW}   Run with --install to auto-install${NC}"
    fi
}

# =============================================================================
# Verification Functions
# =============================================================================

check_python() {
    print_header "Checking Python"
    
    if command -v python3 &> /dev/null; then
        version=$(python3 --version 2>&1 | awk '{print $2}')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        
        if [ "$major" -ge 3 ] && [ "$minor" -ge 13 ]; then
            print_check "Python" "PASS" "v$version"
        elif [ "$major" -ge 3 ] && [ "$minor" -ge 12 ]; then
            print_check "Python" "WARN" "v$version (3.13+ recommended, but 3.12 should work)"
        else
            print_check "Python" "WARN" "v$version (3.13+ required)"
        fi
    else
        print_check "Python" "FAIL"
        install_tool "Python" "sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv"
    fi
}

check_pip() {
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        version=$(pip3 --version 2>&1 | awk '{print $2}' || pip --version 2>&1 | awk '{print $2}')
        print_check "pip" "PASS" "v$version"
    else
        print_check "pip" "FAIL"
        install_tool "pip" "python3 -m ensurepip --upgrade"
    fi
}

check_python_venv() {
    if python3 -c "import venv" &> /dev/null 2>&1; then
        print_check "python3-venv" "PASS" "Available"
    else
        print_check "python3-venv" "FAIL"
        install_tool "python3-venv" "sudo apt-get update && sudo apt-get install -y python3-venv"
    fi
}

check_azure_cli() {
    print_header "Checking Azure Tools"
    
    if command -v az &> /dev/null; then
        version=$(az version --output tsv 2>/dev/null | head -1 | cut -f1)
        print_check "Azure CLI (az)" "PASS" "v$version"
        
        # Check if logged in
        if az account show &> /dev/null; then
            account=$(az account show --query name -o tsv 2>/dev/null)
            echo -e "     ${GREEN}Logged in:${NC} $account"
        else
            echo -e "     ${YELLOW}Not logged in - run 'az login'${NC}"
        fi
    else
        print_check "Azure CLI (az)" "FAIL"
        install_tool "Azure CLI" "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    fi
}

check_azd() {
    if command -v azd &> /dev/null; then
        version=$(azd version 2>&1 | head -1)
        print_check "Azure Developer CLI (azd)" "PASS" "$version"
        
        # Check if logged in
        if azd auth login --check-status &> /dev/null; then
            echo -e "     ${GREEN}Authenticated${NC}"
        else
            echo -e "     ${YELLOW}Not authenticated - run 'azd auth login'${NC}"
        fi
    else
        print_check "Azure Developer CLI (azd)" "FAIL"
        install_tool "Azure Developer CLI" "curl -fsSL https://aka.ms/install-azd.sh | bash"
    fi
}

check_git() {
    print_header "Checking Development Tools"
    
    if command -v git &> /dev/null; then
        version=$(git --version | awk '{print $3}')
        print_check "Git" "PASS" "v$version"
    else
        print_check "Git" "FAIL"
        install_tool "Git" "sudo apt-get update && sudo apt-get install -y git"
    fi
}

check_powershell() {
    if command -v pwsh &> /dev/null; then
        version=$(pwsh --version | awk '{print $2}')
        print_check "PowerShell 7" "PASS" "v$version"
    else
        print_check "PowerShell 7" "WARN" "Optional - not installed"
        if [ "$INSTALL_MODE" = true ]; then
            echo -e "${YELLOW}   Skipping PowerShell install (optional on Linux)${NC}"
        fi
    fi
}

check_azure_subscription() {
    print_header "Checking Azure Subscription"
    
    if command -v az &> /dev/null; then
        if az account show &> /dev/null 2>&1; then
            subscription=$(az account show --query name -o tsv 2>/dev/null)
            subscription_id=$(az account show --query id -o tsv 2>/dev/null)
            print_check "Azure Subscription" "PASS" "$subscription"
            echo -e "     ${BLUE}Subscription ID:${NC} $subscription_id"
        else
            print_check "Azure Subscription" "WARN" "Not logged in - run 'az login'"
        fi
    else
        print_check "Azure Subscription" "WARN" "Azure CLI not installed"
    fi
}

check_python_packages() {
    print_header "Checking Python Packages (from requirements.txt)"
    
    # All packages from code/0_challenge/requirements.txt
    # Format: "pip-package-name:import-module-name"
    local packages=(
        "dotenv-azd:dotenv_azd"
        "rich:rich"
        "ragas:ragas"
        "rapidfuzz:rapidfuzz"
        "langchain:langchain"
        "azure-ai-projects:azure.ai.projects"
        "azure-identity:azure.identity"
        "azure-ai-evaluation:azure.ai.evaluation"
    )
    
    local missing_packages=()
    
    for pkg_info in "${packages[@]}"; do
        pkg_name="${pkg_info%%:*}"
        import_name="${pkg_info##*:}"
        
        if python3 -c "import ${import_name}" &> /dev/null 2>&1; then
            version=$(pip3 show "$pkg_name" 2>/dev/null | grep Version | awk '{print $2}')
            print_check "$pkg_name" "PASS" "v$version"
        else
            print_check "$pkg_name" "WARN" "Not installed"
            missing_packages+=("$pkg_name")
        fi
    done
    
    # Check for ai-rag-chat-evaluator (git package)
    if python3 -c "import scripts" &> /dev/null 2>&1; then
        print_check "ai-rag-chat-evaluator" "PASS" "git package"
    else
        print_check "ai-rag-chat-evaluator" "WARN" "Not installed (git package)"
        missing_packages+=("ai-rag-chat-evaluator")
    fi
    
    # Offer to install all packages if any are missing
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo ""
        echo -e "  ${YELLOW}${#missing_packages[@]} package(s) missing${NC}"
        install_tool "Python packages" "pip install -r code/0_challenge/requirements.txt"
    fi
}

check_workspace() {
    print_header "Checking Workspace Files"
    
    # Check if we're in the right directory
    if [ -f "code/0_challenge/README.md" ]; then
        print_check "Microhack workspace" "PASS" "Found"
    else
        print_check "Microhack workspace" "WARN" "Not in workspace root"
        echo -e "     ${YELLOW}Run from: /workspaces/microhacks-trust-ai${NC}"
        return
    fi
    
    # Check for required files from 0_challenge
    echo ""
    echo -e "  ${BLUE}Required files:${NC}"
    local files=(
        "code/0_challenge/requirements.txt"
        "code/0_challenge/evaluatemh.py"
        "code/0_challenge/redteammh.py"
        "code/0_challenge/safety_evaluationmh.py"
        "code/0_challenge/ground_truth_test.jsonl"
        "code/0_challenge/evaluate.yaml"
    )
    
    local all_files_present=true
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "    ${GREEN}✅${NC} $file"
        else
            echo -e "    ${RED}❌${NC} $file - MISSING"
            all_files_present=false
        fi
    done
    
    if [ "$all_files_present" = true ]; then
        STATUS["Workspace Files"]="PASS"
    else
        STATUS["Workspace Files"]="WARN"
    fi
}

check_ragchat_repo() {
    print_header "Checking RAG Chat Demo Repository"
    
    # Check if azure-search-openai-demo is cloned
    if [ -d "../azure-search-openai-demo" ] || [ -d "azure-search-openai-demo" ]; then
        print_check "azure-search-openai-demo" "PASS" "Found"
        
        # Check for evals directory
        local repo_path="../azure-search-openai-demo"
        [ -d "azure-search-openai-demo" ] && repo_path="azure-search-openai-demo"
        
        if [ -d "$repo_path/evals" ]; then
            echo -e "     ${GREEN}evals/ directory exists${NC}"
        else
            echo -e "     ${YELLOW}evals/ directory not found${NC}"
        fi
    else
        print_check "azure-search-openai-demo" "WARN" "Not cloned yet"
        echo -e "     ${YELLOW}Clone with: git clone https://github.com/Azure-Samples/azure-search-openai-demo.git${NC}"
    fi
}

# =============================================================================
# Summary
# =============================================================================

print_summary() {
    print_header "Summary"
    
    local pass_count=0
    local fail_count=0
    local warn_count=0
    
    for key in "${!STATUS[@]}"; do
        case ${STATUS[$key]} in
            PASS) ((pass_count++)) ;;
            FAIL) ((fail_count++)) ;;
            WARN) ((warn_count++)) ;;
        esac
    done
    
    echo -e "  ${GREEN}Passed:${NC}   $pass_count"
    echo -e "  ${YELLOW}Warnings:${NC} $warn_count"
    echo -e "  ${RED}Failed:${NC}   $fail_count"
    echo ""
    
    if [ "$ALL_PASSED" = true ]; then
        echo -e "${GREEN}=============================================="
        echo -e "🎉 All prerequisites are satisfied!"
        echo -e "==============================================${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Clone azure-search-openai-demo repo"
        echo "  2. Run 'azd auth login' to authenticate"
        echo "  3. Follow code/0_challenge/README.md"
    else
        echo -e "${YELLOW}=============================================="
        echo -e "⚠️  Some prerequisites are missing"
        echo -e "==============================================${NC}"
        echo ""
        if [ "$INSTALL_MODE" = false ]; then
            echo "Run with --install flag to auto-install missing tools:"
            echo "  ./scripts/setup-verify.sh --install"
        fi
    fi
    echo ""
}

# =============================================================================
# Main
# =============================================================================

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗"
echo -e "║     🔐 Microhacks Trust AI - Prerequisites Verification      ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"

if [ "$INSTALL_MODE" = true ]; then
    echo -e "${YELLOW}Running in INSTALL mode - missing tools will be installed${NC}"
fi

check_python
check_pip
check_python_venv
check_azure_cli
check_azd
check_azure_subscription
check_git
check_powershell
check_python_packages
check_workspace
check_ragchat_repo
print_summary

exit 0
