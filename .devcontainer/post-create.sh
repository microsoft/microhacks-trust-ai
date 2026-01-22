#!/bin/bash
# Post-create script for Microhacks Trust AI Dev Container
# This script runs automatically after the container is created

set -e

echo "=============================================="
echo "🚀 Microhacks Trust AI - Post-Create Setup"
echo "=============================================="

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies from 0_challenge
if [ -f "code/0_challenge/requirements.txt" ]; then
    echo "📦 Installing Python dependencies from 0_challenge..."
    pip install -r code/0_challenge/requirements.txt
else
    echo "⚠️  requirements.txt not found in code/0_challenge/"
fi

# Create a convenient alias for the setup script
echo "🔧 Setting up convenience aliases..."
echo 'alias verify-setup="bash scripts/setup-verify.sh"' >> ~/.bashrc
echo 'alias setup-prereqs="bash scripts/setup-verify.sh --install"' >> ~/.bashrc

echo ""
echo "=============================================="
echo "✅ Post-create setup complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Run 'verify-setup' to check prerequisites"
echo "  2. Run 'azd auth login' to authenticate with Azure"
echo "  3. Follow the instructions in code/0_challenge/README.md"
echo ""
