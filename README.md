# 🏥 MediLedger Nexus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Hedera](https://img.shields.io/badge/Hedera-Hashgraph-purple.svg)](https://hedera.com/)
[![AI Powered](https://img.shields.io/badge/AI-Groq%20Powered-orange.svg)](https://groq.com/)
[![Tests](https://img.shields.io/badge/tests-pytest-red.svg)](https://pytest.org/)

> **Revolutionizing Healthcare Through Decentralized AI and Blockchain Technology**

MediLedger Nexus is a cutting-edge decentralized health data ecosystem built on Hedera Hashgraph, featuring zero-knowledge health vaults, AI-powered diagnostics, and a tokenized consent economy. Experience the future of healthcare where patients control their data, AI agents collaborate securely, and medical insights are generated through privacy-preserving federated learning.

---

## 🌟 Key Features

### 🔐 **Zero-Knowledge Health Vaults**
- **End-to-End Encryption**: AES-256 + RSA hybrid encryption
- **zk-SNARKs Privacy**: Prove data validity without revealing content
- **Granular Access Control**: Fine-tuned permissions for different data types
- **Immutable Audit Trail**: Every access logged on Hedera Consensus Service

### 💰 **Tokenized Consent Economy**
- **$HEAL Token Rewards**: Earn tokens for data sharing consent
- **Smart Contract Automation**: Automated compensation distribution
- **Dynamic Pricing**: Market-driven data valuation
- **Transparent Governance**: Community-driven protocol decisions

### 🤖 **AI Diagnostic Co-Pilot**
- **Ultra-Fast Inference**: Powered by Groq AI for millisecond responses
- **HCS-10 OpenConvAI**: AI agents communicate via Hedera Consensus Service
- **Federated Learning**: Collaborative AI training without data sharing
- **Multi-Modal Analysis**: Text, imaging, genomics, and sensor data

### 🚨 **Emergency Response Protocol**
- **Instant Access**: Critical health data available in emergencies
- **Smart Triage**: AI-powered emergency severity assessment
- **Global Interoperability**: HL7 FHIR standard compliance
- **Automated Notifications**: Real-time alerts to emergency contacts

### 🌍 **Global Health Interoperability**
- **HL7 FHIR Integration**: Seamless healthcare system integration
- **Cross-Border Data Exchange**: Secure international health records
- **Multi-Language Support**: Global accessibility
- **Regulatory Compliance**: HIPAA, GDPR, and regional standards

---

## 🏗️ Enterprise-Grade Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React Dashboard] --> B[Mobile App]
        B --> C[Provider Portal]
    end
    
    subgraph "API Gateway"
        D[FastAPI Server] --> E[Authentication]
        E --> F[Rate Limiting]
        F --> G[Request Validation]
    end
    
    subgraph "Core Services"
        H[Health Vault Service] --> I[AI Diagnostics Service]
        I --> J[Consent Management]
        J --> K[Emergency Service]
        K --> L[Research Service]
    end
    
    subgraph "AI & ML Layer"
        M[Groq AI Engine] --> N[Federated Learning]
        N --> O[HCS-10 AI Agents]
        O --> P[Diagnostic Models]
    end
    
    subgraph "Security Layer"
        Q[AES-256 Encryption] --> R[zk-SNARKs]
        R --> S[Access Control]
        S --> T[Audit Logging]
    end
    
    subgraph "Blockchain Layer"
        U[Hedera Consensus Service] --> V[Hedera Token Service]
        V --> W[Smart Contracts]
        W --> X[Mirror Node API]
    end
    
    subgraph "Storage Layer"
        Y[SQLite Database] --> Z[IPFS Storage]
        Z --> AA[Arweave Archive]
    end
    
    A --> D
    D --> H
    H --> M
    M --> Q
    Q --> U
    U --> Y
```

### 🔄 **HCS-10 OpenConvAI Integration**

```mermaid
sequenceDiagram
    participant P as Patient
    participant AI1 as Diagnostic AI
    participant HCS as Hedera Consensus
    participant AI2 as Research AI
    participant FL as Federated Learning
    
    P->>AI1: Request Health Analysis
    AI1->>HCS: Register on HCS-2 Registry
    AI1->>HCS: Publish to Outbound Topic
    HCS->>AI2: Discover via Registry
    AI2->>HCS: Connection Request
    AI1->>HCS: Accept Connection
    AI1->>AI2: Share Anonymized Insights
    AI2->>FL: Contribute to Learning
    FL->>P: Enhanced Diagnosis
```

---

## 🚀 Modern Tech Stack

| Category | Technology | Purpose | Status |
|----------|------------|---------|---------|
| **Backend** | FastAPI 0.104+ | High-performance async API framework | 🔄 Deploying |
| **AI Engine** | Groq AI | Ultra-fast LLM inference (1000+ tokens/sec) | ✅ Integrated |
| **Blockchain** | Hedera Hashgraph | Consensus, tokens, and smart contracts | ✅ Deployed |
| **Smart Contracts** | Solidity 0.8.19 | HealthVault, Consent, Research, Emergency | ✅ Deployed |
| **Database** | SQLite + aiosqlite | Lightweight, async-compatible database | ✅ Configured |
| **Encryption** | AES-256 + RSA-2048 | Military-grade data protection | ✅ Implemented |
| **Privacy** | zk-SNARKs | Zero-knowledge proof system | ✅ Ready |
| **ML Framework** | PyTorch | Federated learning and model training | ✅ Integrated |
| **Storage** | IPFS + Arweave | Decentralized and permanent storage | ✅ Configured |
| **Testing** | pytest + httpx | Comprehensive test coverage | 🔄 In Progress |
| **Standards** | HL7 FHIR + HCS-10 | Healthcare and AI interoperability | ✅ Implemented |
| **Deployment** | Foundry + Render | Smart contracts + Backend deployment | ✅ Contracts Deployed |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Mediledger-Nexus/MediLedgerNexus.git
cd MediLedgerNexus/backend
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
# or
pip install -e .
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 5. Initialize Database
```bash
python -m alembic upgrade head
```

### 6. Start Development Server
```bash
uvicorn src.mediledger_nexus.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Run API Demo
```bash
python api_demo.py
```

🎉 **Success!** Your MediLedger Nexus backend is now running at `http://localhost:8000`

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src/mediledger_nexus --cov-report=html
```

### Run Integration Tests
```bash
pytest tests/integration/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/ -v

# AI service tests
pytest tests/unit/test_ai_services.py -v

# Blockchain integration tests
pytest tests/integration/test_hedera.py -v
```

---

## 📚 API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### 🔐 Authentication
```http
POST /api/v1/auth/register    # User registration
POST /api/v1/auth/token       # Login & get JWT token
GET  /api/v1/auth/me          # Get current user
POST /api/v1/auth/refresh     # Refresh JWT token
```

#### 🏥 Health Vault Management
```http
POST /api/v1/vault/create           # Create health vault
GET  /api/v1/vault/                 # Get user vaults
GET  /api/v1/vault/{vault_id}       # Get specific vault
PUT  /api/v1/vault/{vault_id}       # Update vault
POST /api/v1/vault/{vault_id}/upload # Upload medical record
```

#### 🤖 AI Diagnostics & HCS-10
```http
POST /api/v1/ai/register-agent      # Register AI agent
POST /api/v1/ai/diagnose           # Request AI diagnosis
GET  /api/v1/ai/insights           # Get health insights
POST /api/v1/ai/federated-learning/join # Join FL study
POST /api/v1/ai/connect/{agent_id} # Connect to AI agent
```

#### 📋 Consent Management
```http
POST /api/v1/consent/grant         # Grant data access consent
GET  /api/v1/consent/              # Get user consents
PUT  /api/v1/consent/{consent_id}  # Update consent
DELETE /api/v1/consent/{consent_id} # Revoke consent
```

#### 🚨 Emergency Access
```http
POST /api/v1/emergency/access      # Emergency data access
GET  /api/v1/emergency/profile     # Get emergency profile
PUT  /api/v1/emergency/profile     # Update emergency profile
```

---

## 🛠️ Development Guidelines

### Code Style
- **Formatter**: Black with 88-character line length
- **Linter**: Ruff for fast Python linting
- **Type Hints**: Mandatory for all functions
- **Docstrings**: Google-style documentation

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new health vault encryption"

# Push and create PR
git push origin feature/your-feature-name
```

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./mediledger.db

# Hedera Configuration
HEDERA_NETWORK=testnet
HEDERA_ACCOUNT_ID=0.0.123456
HEDERA_PRIVATE_KEY=your_private_key

# Smart Contract Addresses (Deployed on Hedera Testnet)
HEALTH_VAULT_CONTRACT=0x96CDd936E361a48e45Fd5c368c309E4EFC5401A1
CONSENT_MANAGER_CONTRACT=0xC3C4500BEB39684704eaF6F3698D4fcCec672DFf
RESEARCH_STUDY_CONTRACT=0xd4955d4D7A13345D9704CdCc6682A3229cA2159A
EMERGENCY_ACCESS_CONTRACT=0x441EC1726c23863597ae45aB92f1cD27fEd2f9ef

# AI Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-70b-8192

# Security
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_encryption_key
```

---

## 🚀 Deployment Status

### ✅ Smart Contracts - DEPLOYED
**Status**: Successfully deployed to Hedera Testnet  
**Network**: Hedera Testnet  
**Deployer**: `0x37D46c1dCA719D71C656153d933B3bC6765c3518`

#### Deployed Contract Addresses:
- **HealthVault**: `0x96CDd936E361a48e45Fd5c368c309E4EFC5401A1`
- **ConsentManager**: `0xC3C4500BEB39684704eaF6F3698D4fcCec672DFf`
- **ResearchStudy**: `0xd4955d4D7A13345D9704CdCc6682A3229cA2159A`
- **EmergencyAccess**: `0x441EC1726c23863597ae45aB92f1cD27fEd2f9ef`

### 🔄 Backend API - IN PROGRESS
**Status**: Deployment in progress on Render  
**Issues Resolved**: 
- ✅ pydantic-settings import issues
- ✅ Configuration validation errors
- ✅ Python path configuration

**Current Status**: Backend deployment being optimized for Render platform

### Smart Contract Deployment Instructions
```bash
# Navigate to contracts directory
cd contracts

# Install Foundry (if not already installed)
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc
foundryup

# Set up environment variables
export HEDERA_PRIVATE_KEY="<set-from-your-secret-manager>"

# Deploy contracts to Hedera Testnet
forge script script/Deploy.s.sol --rpc-url https://testnet.hashio.io/api --broadcast --verify --via-ir

# Verify deployment
cast code 0x96CDd936E361a48e45Fd5c368c309E4EFC5401A1 --rpc-url https://testnet.hashio.io/api
```

**Deployment Files**:
- `contracts/script/Deploy.s.sol` - Deployment script
- `contracts/deployment.env` - Environment configuration
- `contracts/deployed_addresses.env` - Contract addresses

### Docker Deployment
```bash
# Build image
docker build -t mediledger-nexus .

# Run container
docker run -p 8000:8000 --env-file .env mediledger-nexus
```

### Production Checklist
- [x] Set strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [x] Configure production database (SQLite for development)
- [x] Set up Hedera testnet accounts and keys
- [x] Deploy smart contracts to Hedera testnet
- [ ] Configure CORS for your frontend domain
- [ ] Set up monitoring and logging
- [ ] Enable HTTPS/TLS encryption
- [ ] Configure backup strategies
- [ ] Set up CI/CD pipelines
- [ ] Deploy backend to production platform

---

## 📊 Current Project Status

### ✅ Completed Components
- **Smart Contracts**: All 4 contracts deployed to Hedera Testnet
- **Contract Architecture**: HealthVault, ConsentManager, ResearchStudy, EmergencyAccess
- **Deployment Infrastructure**: Foundry setup, deployment scripts, environment configuration
- **Backend Core**: FastAPI application with authentication, database models, API endpoints
- **AI Integration**: Groq AI integration for diagnostics and insights
- **Security Layer**: AES-256 encryption, JWT authentication, input validation

### 🔄 In Progress
- **Backend Deployment**: Optimizing for Render platform deployment
- **API Integration**: Connecting backend to deployed smart contracts
- **Testing**: Comprehensive test suite for all components

### 📋 Next Steps
1. **Complete Backend Deployment**: Resolve remaining Render deployment issues
2. **Contract Integration**: Connect backend API to deployed smart contracts
3. **Frontend Development**: Build React dashboard and mobile app
4. **Testing & QA**: Comprehensive testing of full system integration
5. **Documentation**: Complete API documentation and user guides
6. **Production Deployment**: Deploy to mainnet and production infrastructure

### 🎯 Milestones Achieved
- ✅ Smart contract development and deployment
- ✅ Backend API architecture and core functionality
- ✅ AI integration with Groq
- ✅ Security and encryption implementation
- ✅ Database models and API endpoints
- ✅ Development environment setup

---

## 🔒 Security Considerations

### Data Protection
- **Encryption at Rest**: All sensitive data encrypted with AES-256
- **Encryption in Transit**: TLS 1.3 for all communications
- **Key Management**: Hardware Security Modules (HSM) recommended
- **Access Logging**: Comprehensive audit trails on Hedera

### Privacy Compliance
- **HIPAA Compliance**: Healthcare data protection standards
- **GDPR Compliance**: European data protection regulations
- **Zero-Knowledge**: Prove data validity without revealing content
- **Data Minimization**: Collect only necessary information

### Blockchain Security
- **Hedera Consensus**: Byzantine fault-tolerant consensus
- **Smart Contract Audits**: Regular security assessments
- **Multi-Signature**: Required for critical operations
- **Rate Limiting**: Protection against abuse

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Reporting Issues
- Use GitHub Issues for bug reports
- Include detailed reproduction steps
- Provide environment information
- Add relevant logs and error messages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Hedera Hashgraph** - For the revolutionary DLT platform
- **Groq** - For ultra-fast AI inference capabilities
- **FastAPI** - For the excellent async web framework
- **OpenAI** - For advancing AI research and development
- **Healthcare Community** - For inspiring this project

---

## 📞 Support & Contact

- **Documentation**: [docs.mediledger-nexus.com](https://docs.mediledger-nexus.com)
- **Discord**: [Join our community](https://discord.gg/mediledger-nexus)
- **Email**: support@mediledger-nexus.com
- **Twitter**: [@MediLedgerNexus](https://twitter.com/MediLedgerNexus)

---

<div align="center">

**Built with ❤️ for the future of healthcare**

[🌟 Star us on GitHub](https://github.com/Mediledger-Nexus/MediLedgerNexus) | [🐦 Follow on Twitter](https://twitter.com/MediLedgerNexus) | [💬 Join Discord](https://discord.gg/mediledger-nexus)

</div>
