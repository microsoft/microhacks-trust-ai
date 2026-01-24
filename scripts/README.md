# Scripts Directory

This directory contains automation scripts for the Microhacks Trust AI workshop.

## Available Scripts

### `setup-verify.sh`

A comprehensive prerequisites setup and verification script for the workshop.

#### Usage

```bash
# Verify prerequisites only (no installation)
./scripts/setup-verify.sh

# Verify and install missing tools automatically
./scripts/setup-verify.sh --install

# Show help
./scripts/setup-verify.sh --help
```

#### What It Checks

| Category | Tool/Package | Required |
|----------|--------------|----------|
| **Python** | Python 3.13+ | ✅ Yes |
| **Python** | pip | ✅ Yes |
| **Python** | python3-venv | ✅ Yes |
| **Azure** | Azure CLI (az) | ✅ Yes |
| **Azure** | Azure Developer CLI (azd) | ✅ Yes |
| **Azure** | Azure Subscription (logged in) | ✅ Yes |
| **Dev Tools** | Git | ✅ Yes |
| **Dev Tools** | PowerShell 7 | ⚠️ Optional |
| **Python Packages** | dotenv-azd | ✅ Yes |
| **Python Packages** | rich | ✅ Yes |
| **Python Packages** | ragas | ✅ Yes |
| **Python Packages** | rapidfuzz | ✅ Yes |
| **Python Packages** | langchain | ✅ Yes |
| **Python Packages** | azure-ai-projects | ✅ Yes |
| **Python Packages** | azure-identity | ✅ Yes |
| **Python Packages** | azure-ai-evaluation | ✅ Yes |
| **Python Packages** | ai-rag-chat-evaluator | ✅ Yes |
| **Workspace** | Microhack files | ✅ Yes |
| **Workspace** | azure-search-openai-demo repo | ✅ Yes |

#### Example Output

```
╔══════════════════════════════════════════════════════════════╗
║     🔐 Microhacks Trust AI - Prerequisites Verification      ║
╚══════════════════════════════════════════════════════════════╝

==============================================
🔍 Checking Python
==============================================
  ✅ Python - v3.13.0
  ✅ pip - v24.0

==============================================
🔍 Checking Azure Tools
==============================================
  ✅ Azure CLI (az) - v2.60.0
     Logged in: My-Subscription
  ✅ Azure Developer CLI (azd) - azd version 1.9.0
     Authenticated

==============================================
🔍 Summary
==============================================
  Passed:   8
  Warnings: 1
  Failed:   0

🎉 All prerequisites are satisfied!
```

## Dev Container Integration

When using the Dev Container, the `post-create.sh` script automatically:

1. Installs Python dependencies
2. Sets up convenience aliases:
   - `verify-setup` - Runs verification script
   - `setup-prereqs` - Runs verification with auto-install

## Quick Start

1. **Verify your environment:**
   ```bash
   bash scripts/setup-verify.sh
   ```

2. **Install missing prerequisites:**
   ```bash
   bash scripts/setup-verify.sh --install
   ```

3. **Follow Challenge 0:**
   ```bash
   cat code/0_challenge/README.md
   ```

## Troubleshooting

### Permission Denied
```bash
chmod +x scripts/setup-verify.sh
```

### Azure CLI Installation Fails
Try manual installation:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Azure Developer CLI Installation Fails
Try manual installation:
```bash
curl -fsSL https://aka.ms/install-azd.sh | bash
```
