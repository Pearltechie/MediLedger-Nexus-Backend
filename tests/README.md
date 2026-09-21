# MediLedger Nexus - Test Suite

This directory contains comprehensive tests for all components of the MediLedger Nexus platform.

## 📁 Directory Structure

```
tests/
├── README.md                    # This file
├── run_all_tests.py            # Master test runner
├── encryption/                 # Encryption and security tests
│   ├── test_aes_encryption.py
│   └── test_key_generation.py
├── zk_snarks/                  # Zero-Knowledge Proof tests
│   ├── test_zk_snarks.py
│   ├── demo_zk_snarks.py
│   ├── setup_zk_snarks.py
│   ├── ZK_SNARKS_SUMMARY.md
│   ├── install_zokrates.sh
│   ├── docker_zokrates.sh
│   └── zokrates
└── hedera/                     # Hedera blockchain tests
    ├── test_hedera_integration.py
    └── simple_hedera_test.py
```

## 🧪 Test Categories

### 1. **Encryption Tests** (`encryption/`)
- **AES-256 Encryption**: Test data encryption/decryption
- **Key Generation**: Test secure key generation
- **Data Integrity**: Verify encryption/decryption integrity
- **Multiple Data Types**: Test different health data types

### 2. **Zero-Knowledge Proof Tests** (`zk_snarks/`)
- **Circuit Compilation**: Test ZoKrates circuit compilation
- **Proof Generation**: Test zk-SNARK proof creation
- **Proof Verification**: Test proof verification
- **Health Data Validation**: Test privacy-preserving validation

### 3. **Hedera Blockchain Tests** (`hedera/`)
- **Integration Testing**: Test Hedera client integration with backend
- **Simple Functionality**: Test basic Hedera SDK operations
- **Smart Contract Integration**: Test contract deployment and interaction
- **Token Operations**: Test HTS token operations

**Note**: Hedera key generation utilities have been moved to `archive/hedera/` as they are development tools that have been integrated into the main codebase.

## 🚀 Running Tests

### Run All Tests
```bash
cd tests
python run_all_tests.py
```

### Run Specific Test Categories
```bash
# Encryption tests
python encryption/test_aes_encryption.py

# ZK-SNARK tests
python zk_snarks/test_zk_snarks.py

# Hedera tests
python hedera/simple_hedera_test.py
```

### Run Individual Tests
```bash
# Test encryption demo
python encryption/test_encryption_demo.py

# Test ZK-SNARK demo
python zk_snarks/demo_zk_snarks.py

# Test Hedera integration
python hedera/test_hedera_integration.py
```

## 📋 Prerequisites

### For Encryption Tests
- Python 3.8+
- `cryptography` library
- `ENCRYPTION_KEY` environment variable

### For ZK-SNARK Tests
- Docker (for ZoKrates)
- Python 3.8+
- ZoKrates circuits in `circuits/` directory

### For Hedera Tests
- Python 3.8+
- `hedera-sdk-py` library
- Hedera testnet account
- Backend integration (for integration tests)

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
# Python dependencies
pip install cryptography hedera-sdk-py

# Note: Hedera key generation utilities are now in archive/hedera/
# For Node.js dependencies, see archive/hedera/package.json
```

### 2. Set Environment Variables
```bash
# Copy from root directory
cp ../../.env .env

# Or set manually
export ENCRYPTION_KEY="your-aes-256-encryption-key"
export HEDERA_ACCOUNT_ID="your-account-id"
export HEDERA_PRIVATE_KEY="your-private-key"
```

### 3. Setup ZK-SNARK Environment
```bash
cd tests/zk_snarks
chmod +x install_zokrates.sh
chmod +x docker_zokrates.sh
./install_zokrates.sh
```

## 📊 Test Results

Tests will output:
- ✅ **PASS**: Test completed successfully
- ❌ **FAIL**: Test failed with error details
- ⚠️ **SKIP**: Test skipped due to missing dependencies
- 📊 **METRICS**: Performance and security metrics

## 🛡️ Security Considerations

- **Never commit test data with real patient information**
- **Use test accounts for Hedera blockchain tests**
- **Store encryption keys securely**
- **Run tests in isolated environments**

## 🔍 Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Load environment variables
   source .env
   ```

2. **Docker Not Running (for ZK-SNARK tests)**
   ```bash
   # Start Docker
   open -a Docker
   
   # Test Docker
   docker --version
   ```

3. **Missing Dependencies**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   npm install
   ```

4. **Hedera Network Issues**
   ```bash
   # Check network connectivity
   ping testnet.mirrornode.hedera.com
   
   # Verify account balance
   python hedera/check_account_balance.py
   ```

## 📈 Performance Benchmarks

### Encryption Performance
- **AES-256 Encryption**: ~1ms per 1KB of data
- **Key Generation**: ~100ms per key
- **Data Integrity Check**: ~0.1ms per operation

### ZK-SNARK Performance
- **Circuit Compilation**: ~2-5 seconds
- **Proof Generation**: ~1-3 seconds
- **Proof Verification**: ~0.1-0.5 seconds

### Hedera Performance
- **Key Generation**: ~50ms
- **Account Creation**: ~2-5 seconds
- **Transaction Submission**: ~1-3 seconds

## 🤝 Contributing

When adding new tests:

1. **Follow naming convention**: `test_*.py` for test files
2. **Add to appropriate category**: encryption, zk_snarks, or hedera
3. **Update this README**: Document new tests and requirements
4. **Add to test runner**: Include in `run_all_tests.py`
5. **Test thoroughly**: Ensure tests pass in clean environment

## 📞 Support

For test-related issues:
- Check the troubleshooting section above
- Review individual test documentation
- Check environment setup and dependencies
- Verify network connectivity for blockchain tests
