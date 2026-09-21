# MediLedger Nexus Smart Contracts

This directory contains the smart contracts for the MediLedger Nexus decentralized health data ecosystem built on Hedera Hashgraph.

## Overview

MediLedger Nexus implements a comprehensive set of smart contracts for managing:

- **Health Vaults**: Encrypted health records with zero-knowledge proofs
- **Consent Management**: Tokenized consent and data sharing agreements
- **Research Studies**: Federated learning and research participation
- **Emergency Access**: Critical health data access during emergencies

## Contract Architecture

### Core Contracts

1. **HealthVault.sol** - Manages encrypted health records with granular access control
2. **ConsentManager.sol** - Handles patient consent and compensation for data sharing
3. **ResearchStudy.sol** - Facilitates research studies and data contribution
4. **EmergencyAccess.sol** - Provides emergency access to critical health data

### Key Features

- **Zero-Knowledge Privacy**: Prove data validity without revealing content
- **Tokenized Consent**: Earn tokens for data sharing consent
- **Emergency Protocols**: Instant access to critical data during emergencies
- **Research Integration**: Federated learning and anonymized data sharing
- **Access Control**: Granular permissions with time-based expiration
- **Audit Trail**: Immutable record of all data access and modifications

## Getting Started

### Prerequisites

- [Foundry](https://book.getfoundry.sh/getting-started/installation)
- [Node.js](https://nodejs.org/) (v16 or higher)
- [Git](https://git-scm.com/)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mediledgernexus/contracts.git
cd contracts
```

2. Install dependencies:
```bash
forge install
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Hedera Configuration
HEDERA_ACCOUNT_ID=0.0.123456
HEDERA_PRIVATE_KEY=your_private_key_here
HEDERA_NETWORK=testnet

# API Keys
ETHERSCAN_API_KEY=your_etherscan_api_key
HEDERA_API_KEY=your_hedera_api_key

# Test Configuration
TEST_ACCOUNT_1=0x...
TEST_ACCOUNT_2=0x...
TEST_ACCOUNT_3=0x...
```

## Development

### Compile Contracts

```bash
forge build
```

### Run Tests

```bash
# Run all tests
forge test

# Run tests with verbose output
forge test -vvv

# Run specific test file
forge test --match-path test/TestHealthVault.sol

# Run tests with gas reporting
forge test --gas-report
```

### Code Coverage

```bash
forge coverage
```

### Linting

```bash
# Format code
forge fmt

# Check formatting
forge fmt --check
```

## Testing

The test suite includes comprehensive tests for all contracts:

- **TestHealthVault.sol** - Tests for health vault functionality
- **TestConsentManager.sol** - Tests for consent management
- **TestResearchStudy.sol** - Tests for research study features
- **TestEmergencyAccess.sol** - Tests for emergency access protocols

### Running Specific Tests

```bash
# Test health vault functionality
forge test --match-contract TestHealthVault

# Test consent management
forge test --match-contract TestConsentManager

# Test research studies
forge test --match-contract TestResearchStudy

# Test emergency access
forge test --match-contract TestEmergencyAccess
```

### Test Coverage

```bash
# Generate coverage report
forge coverage

# Generate HTML coverage report
forge coverage --report html
```

## Deployment

### Testnet Deployment

```bash
# Deploy to Hedera testnet
forge script script/Deploy.s.sol --rpc-url testnet --broadcast

# Verify contracts on testnet
forge verify-contract --chain testnet <CONTRACT_ADDRESS> <CONTRACT_NAME>
```

### Mainnet Deployment

```bash
# Deploy to Hedera mainnet
forge script script/Deploy.s.sol --rpc-url mainnet --broadcast

# Verify contracts on mainnet
forge verify-contract --chain mainnet <CONTRACT_ADDRESS> <CONTRACT_NAME>
```

## Contract Details

### HealthVault Contract

**Purpose**: Manages encrypted health records with granular access control

**Key Functions**:
- `createRecord()` - Create a new health record
- `grantAccess()` - Grant access to a health record
- `revokeAccess()` - Revoke access to a health record
- `grantEmergencyAccess()` - Grant emergency access
- `setEmergencyProfile()` - Set emergency profile data

**Access Levels**:
- `read` - Read-only access
- `write` - Read and write access
- `admin` - Full administrative access

### ConsentManager Contract

**Purpose**: Manages patient consent and compensation for data sharing

**Key Functions**:
- `createConsent()` - Create a new consent agreement
- `activateConsent()` - Activate a consent agreement
- `revokeConsent()` - Revoke a consent agreement
- `grantDataAccess()` - Grant data access to a requester
- `payCompensation()` - Pay compensation for data access

**Features**:
- Time-based consent expiration
- Automatic renewal options
- Compensation tracking
- Granular data type permissions

### ResearchStudy Contract

**Purpose**: Facilitates research studies and data contribution

**Key Functions**:
- `createStudy()` - Create a new research study
- `joinStudy()` - Join a research study
- `contributeData()` - Contribute data to a study
- `validateAndPayContribution()` - Validate and pay for contributions
- `completeStudy()` - Complete a research study

**Features**:
- Participant management
- Data contribution tracking
- Compensation distribution
- Study lifecycle management

### EmergencyAccess Contract

**Purpose**: Provides emergency access to critical health data

**Key Functions**:
- `createEmergencyProfile()` - Create emergency profile
- `requestEmergencyAccess()` - Request emergency access
- `grantEmergencyAccess()` - Grant emergency access
- `revokeEmergencyAccess()` - Revoke emergency access

**Features**:
- Urgency-based access levels
- Automatic approval for high-urgency cases
- Time-limited access
- Emergency contact notifications

## Security Considerations

### Access Control
- Role-based access control with multiple permission levels
- Time-based access expiration
- Emergency access protocols with automatic approval for critical cases

### Data Privacy
- Zero-knowledge proof support for data validation
- Encrypted data storage with IPFS integration
- Granular consent management

### Audit Trail
- Immutable record of all data access
- Comprehensive event logging
- Transaction history tracking

## Gas Optimization

The contracts are optimized for gas efficiency:

- Efficient storage patterns
- Minimal external calls
- Optimized data structures
- Batch operations where possible

## Integration

### Hedera Integration
- HCS (Hedera Consensus Service) for data flow
- HTS (Hedera Token Service) for consent tokens
- Smart Contracts for access control

### IPFS Integration
- Encrypted data storage on IPFS
- Data integrity verification
- Decentralized file access

### AI/ML Integration
- Federated learning support
- Anonymized data sharing
- Research study facilitation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- **Documentation**: [docs.mediledgernexus.com](https://docs.mediledgernexus.com)
- **Discord**: [Join our community](https://discord.gg/mediledgernexus)
- **Email**: support@mediledgernexus.com
- **GitHub Issues**: [Report bugs or request features](https://github.com/mediledgernexus/contracts/issues)

## Acknowledgments

- **Hedera Hashgraph** - For the revolutionary DLT platform
- **OpenZeppelin** - For secure smart contract libraries
- **Foundry** - For the excellent development framework
- **Healthcare Community** - For inspiring this project
