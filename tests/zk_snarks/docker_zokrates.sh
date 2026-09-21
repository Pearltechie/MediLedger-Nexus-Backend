#!/bin/bash

# MediLedger Nexus - ZoKrates Docker Setup
# This script sets up ZoKrates using Docker for zk-SNARK circuit compilation

echo "🐳 MediLedger Nexus - ZoKrates Docker Setup"
echo "============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is available"

# Create a wrapper script for ZoKrates
cat > zokrates << 'EOF'
#!/bin/bash
# ZoKrates Docker wrapper script

# Check if we're in a circuit directory
if [ ! -f "circuit.zok" ] && [ ! -f "*.zok" ]; then
    echo "⚠️  No .zok files found in current directory"
    echo "Make sure you're in a directory with ZoKrates circuit files"
fi

# Run ZoKrates in Docker
docker run --rm -v "$(pwd)":/workspace -w /workspace zokrates/zokrates:0.8.2 "$@"
EOF

# Make the wrapper executable
chmod +x zokrates

echo "✅ ZoKrates Docker wrapper created"

# Test the installation
echo "🧪 Testing ZoKrates installation..."
./zokrates --version

if [ $? -eq 0 ]; then
    echo "🎉 ZoKrates Docker setup completed successfully!"
    echo ""
    echo "📋 Usage:"
    echo "  ./zokrates compile -i circuit.zok"
    echo "  ./zokrates setup"
    echo "  ./zokrates compute-witness -a <inputs>"
    echo "  ./zokrates generate-proof"
    echo "  ./zokrates verify"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Run: python setup_zk_snarks.py"
    echo "2. Run: python test_zk_snarks.py"
else
    echo "❌ ZoKrates Docker setup failed"
    exit 1
fi
