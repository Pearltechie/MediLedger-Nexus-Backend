# MediLedger Nexus - Archive

This directory contains archived files and utilities that were used during development and testing of the MediLedger Nexus platform.

## 📁 Directory Structure

```
archive/
├── README.md                    # This file
├── encryption/                  # Encryption utilities and demos
│   ├── generate_encryption_key.py
│   ├── encryption_demo.py
│   └── encryption_keys_backup.json
└── hedera/                      # Hedera blockchain utilities
    ├── generate_hedera_keys.py
    ├── update_env_with_keys.py
    ├── generate_keys.js
    ├── create_hedera_account.js
    └── package.json
```

## 🔐 Encryption Archive (`encryption/`)

### Files Description

#### `generate_encryption_key.py`
- **Purpose**: Generates secure AES-256 encryption keys for the platform
- **Features**:
  - Cryptographically secure key generation using `secrets.token_bytes()`
  - Base64 encoding for environment variable storage
  - Derived key generation for different data types
  - Automatic `.env` file updates
  - Secure key backup creation
  - Security recommendations and best practices

#### `encryption_demo.py`
- **Purpose**: Demonstrates AES-256 encryption/decryption functionality
- **Features**:
  - Health data encryption/decryption
  - Multiple data type support (consent, research, emergency data)
  - Data integrity verification
  - Performance metrics
  - Comprehensive error handling

#### `encryption_keys_backup.json`
- **Purpose**: Secure backup of generated encryption keys
- **Contents**:
  - Master encryption key (base64 and hex formats)
  - Generation timestamp
  - Security notes and recommendations
  - Key length and format information

### Usage

These files were used to:
1. **Generate the production encryption key** for MediLedger Nexus
2. **Test encryption functionality** before integration
3. **Create secure backups** of encryption keys
4. **Demonstrate encryption capabilities** to stakeholders

### Security Notes

⚠️ **Important Security Considerations**:
- The `encryption_keys_backup.json` file contains sensitive encryption keys
- Never commit this file to version control
- Store backup files securely and separately from the application
- Use different keys for different environments (dev/staging/prod)
- Rotate keys regularly for enhanced security

### Integration Status

✅ **Completed Integration**:
- Encryption key generated and stored in `.env` file
- Encryption functionality integrated into backend
- Key management system implemented
- Security best practices documented

## ⛓️ Hedera Archive (`hedera/`)

### Files Description

#### `generate_hedera_keys.py`
- **Purpose**: Generates Hedera ED25519 private and public keys using Python SDK
- **Features**:
  - Secure key generation using `hedera-sdk-py`
  - Multiple key format outputs (DER, raw hex)
  - JSON file export for easy integration
  - Timestamp and metadata tracking

#### `update_env_with_keys.py`
- **Purpose**: Updates environment configuration with generated Hedera keys
- **Features**:
  - Automatic `.env` file updates
  - Test account creation and management
  - Environment variable validation
  - Integration with backend configuration

#### `generate_keys.js`
- **Purpose**: JavaScript utility for Hedera key generation using Node.js SDK
- **Features**:
  - Uses `@hashgraph/sdk` for key generation
  - Multiple output formats (DER, raw)
  - Console output for immediate use
  - Cross-platform compatibility

#### `create_hedera_account.js`
- **Purpose**: Creates Hedera testnet accounts with generated keys
- **Features**:
  - Automatic testnet account creation
  - Key generation and account linking
  - Balance checking and validation
  - Error handling and retry logic

#### `package.json`
- **Purpose**: Node.js package configuration for Hedera utilities
- **Dependencies**:
  - `@hashgraph/sdk`: Official Hedera JavaScript SDK
  - Development and testing dependencies
  - Script definitions for key generation

### Usage

These files were used to:
1. **Generate Hedera keys** for the MediLedger Nexus platform
2. **Create testnet accounts** for development and testing
3. **Configure environment variables** for Hedera integration
4. **Test Hedera SDK functionality** before backend integration

### Integration Status

✅ **Completed Integration**:
- Hedera keys generated and stored in environment
- Backend Hedera client implemented
- Smart contract integration completed
- Testnet account setup for development

## 🔄 Migration to Tests

The functionality from these archived files has been:
1. **Integrated into the main codebase** (backend encryption services)
2. **Converted to comprehensive tests** (see `tests/encryption/`)
3. **Documented in deployment guides** (see `docs/`)

## 📋 Archive Policy

Files are archived when:
- ✅ **Functionality is integrated** into the main codebase
- ✅ **Tests are created** to verify the functionality
- ✅ **Documentation is updated** with the new features
- ✅ **No longer needed** for active development

## 🗑️ Cleanup

These archived files can be safely removed after:
- ✅ **Verifying integration** is complete and working
- ✅ **Confirming tests** cover all functionality
- ✅ **Ensuring documentation** is up to date
- ✅ **Backing up** any critical information

## 📞 Support

For questions about archived files:
- Check the main codebase for integrated functionality
- Review test files for usage examples
- Consult deployment documentation for setup instructions
- Contact the development team for specific questions

---

**Note**: This archive serves as a historical record of development utilities. The actual functionality has been integrated into the main MediLedger Nexus platform.
