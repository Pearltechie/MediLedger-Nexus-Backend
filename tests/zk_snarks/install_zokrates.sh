#!/bin/bash

# MediLedger Nexus - ZoKrates Installation Script
# This script installs ZoKrates for zk-SNARK circuit compilation

echo "🔐 MediLedger Nexus - ZoKrates Installation"
echo "============================================="

# Check if ZoKrates is already installed
if command -v zokrates &> /dev/null; then
    echo "✅ ZoKrates is already installed"
    zokrates --version
    exit 0
fi

echo "📦 Installing ZoKrates..."

# Detect operating system
OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "Please install ZoKrates manually from: https://github.com/Zokrates/zokrates"
    exit 1
fi

echo "🖥️  Detected OS: $OS"

# Install dependencies
if [[ "$OS" == "linux" ]]; then
    echo "📦 Installing Linux dependencies..."
    sudo apt-get update
    sudo apt-get install -y curl build-essential
elif [[ "$OS" == "macos" ]]; then
    echo "📦 Installing macOS dependencies..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    brew install curl
fi

# Download and install ZoKrates
echo "⬇️  Downloading ZoKrates..."

if [[ "$OS" == "linux" ]]; then
    ZOKRATES_URL="https://github.com/Zokrates/zokrates/releases/latest/download/zokrates-0.8.2-x86_64-unknown-linux-gnu.tar.gz"
elif [[ "$OS" == "macos" ]]; then
    ZOKRATES_URL="https://github.com/Zokrates/zokrates/releases/latest/download/zokrates-0.8.2-x86_64-apple-darwin.tar.gz"
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download ZoKrates
curl -L "$ZOKRATES_URL" -o zokrates.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ Failed to download ZoKrates"
    exit 1
fi

# Extract ZoKrates
echo "📂 Extracting ZoKrates..."
tar -xzf zokrates.tar.gz

# Install ZoKrates
echo "🔧 Installing ZoKrates..."
sudo cp zokrates /usr/local/bin/

if [ $? -ne 0 ]; then
    echo "❌ Failed to install ZoKrates"
    exit 1
fi

# Make executable
sudo chmod +x /usr/local/bin/zokrates

# Clean up
cd /
rm -rf "$TEMP_DIR"

# Verify installation
echo "✅ Verifying installation..."
if command -v zokrates &> /dev/null; then
    echo "🎉 ZoKrates installed successfully!"
    zokrates --version
else
    echo "❌ Installation verification failed"
    exit 1
fi

echo ""
echo "🚀 Next steps:"
echo "1. Run: python setup_zk_snarks.py"
echo "2. Run: python test_zk_snarks.py"
echo ""
echo "📚 Documentation: https://zokrates.github.io/"
