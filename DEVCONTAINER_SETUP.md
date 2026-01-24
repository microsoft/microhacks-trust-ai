# Dev Container Setup Guide

This document describes the automated development environment setup for the Microhacks Trust AI workshop.

## 🚀 Quick Start

### Option 1: GitHub Codespaces (Recommended)

1. Click the **"Code"** button on GitHub
2. Select **"Codespaces"** tab
3. Click **"Create codespace on feature/devcontainer-setup"**
4. Wait for the container to build (~2-3 minutes)
5. Run `verify-setup` to confirm prerequisites

### Option 2: VS Code + Docker

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install [VS Code](https://code.visualstudio.com/)
3. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
4. Clone this repository
5. Open in VS Code → Click "Reopen in Container" when prompted
6. Run `verify-setup` to confirm prerequisites

---

## 📦 What's Included

### Pre-installed Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.13 | Primary language for evaluations |
| Azure CLI | Latest | Azure resource management |
| Azure Developer CLI (azd) | Latest | Infrastructure deployment |
| PowerShell | 7.x | Cross-platform scripting |
| Git | Latest | Version control |

### VS Code Extensions

- **Python** - Python language support
- **Pylance** - Python IntelliSense
- **Azure Functions** - Azure Functions development
- **Bicep** - Infrastructure as Code
- **GitHub Copilot** - AI pair programming
- **Jupyter** - Notebook support
- **YAML** - YAML file support

### Python Packages

All packages from `code/0_challenge/requirements.txt` are pre-installed:

- `azure-ai-evaluation` - AI model evaluation
- `azure-ai-projects` - Azure AI project management
- `azure-identity` - Azure authentication
- `ragas` - RAG evaluation framework
- `langchain` - LLM application framework

---

## 📁 File Structure

```
.devcontainer/
├── devcontainer.json    # Container configuration
└── post-create.sh       # Post-creation setup script

scripts/
├── setup-verify.sh      # Prerequisites verification script
└── README.md            # Scripts documentation
```

---

## 🔧 Configuration Details

### devcontainer.json

```json
{
  "name": "Microhacks Trust AI",
  "image": "mcr.microsoft.com/devcontainers/python:1-3.13-bookworm",
  "features": {
    "azure-cli": "latest",
    "azd": "latest",
    "powershell": "latest"
  }
}
```

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `AZURE_DEV_COLLECT_TELEMETRY` | `no` | Disable azd telemetry |

---

## ✅ Verification

After the container starts, verify your setup:

```bash
# Quick verification (alias)
verify-setup

# Or run the script directly
bash scripts/setup-verify.sh
```

Expected output:
```
🎉 All prerequisites are satisfied!
```

---

## 🔐 Azure Authentication

After verification, authenticate with Azure:

```bash
# Azure CLI login
az login

# Azure Developer CLI login
azd auth login
```

---

## 🛠️ Troubleshooting

### Container fails to build

1. Ensure Docker is running
2. Check Docker has enough resources (4GB+ RAM recommended)
3. Try rebuilding: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"

### Python packages missing

```bash
pip install -r code/0_challenge/requirements.txt
```

### Azure CLI not working

```bash
# Reinstall Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Permission issues

```bash
# Fix script permissions
chmod +x scripts/setup-verify.sh
chmod +x .devcontainer/post-create.sh
```

---

## 📚 Next Steps

1. ✅ Verify prerequisites: `verify-setup`
2. 🔐 Login to Azure: `az login && azd auth login`
3. 📖 Start Challenge 0: [code/0_challenge/README.md](code/0_challenge/README.md)

---

## 🤝 Contributing

To modify the dev container configuration:

1. Edit `.devcontainer/devcontainer.json`
2. Test locally by rebuilding the container
3. Submit a pull request

---

## 📄 Related Documentation

- [Challenge 0 Setup](code/0_challenge/README.md)
- [Scripts Documentation](scripts/README.md)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
