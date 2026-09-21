"""
Pytest configuration and fixtures for MediLedger Nexus tests
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from mediledger_nexus.core.config import get_settings
from mediledger_nexus.core.database import Base, get_async_session
from mediledger_nexus.main import app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
TEST_DATABASE_URL_SYNC = "sqlite:///./test.db"

# Create test engines
test_engine = create_engine(TEST_DATABASE_URL_SYNC, echo=False)
test_async_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Create session makers
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
TestAsyncSessionLocal = async_sessionmaker(
    test_async_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing"""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session
    
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_async_session(async_session: AsyncSession):
    """Override the get_async_session dependency"""
    async def _override_get_async_session():
        yield async_session
    
    return _override_get_async_session


@pytest.fixture
def client(override_get_async_session) -> TestClient:
    """Create test client with database override"""
    app.dependency_overrides[get_async_session] = override_get_async_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(override_get_async_session) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client"""
    app.dependency_overrides[get_async_session] = override_get_async_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "hedera_account_id": "0.0.123456"
    }


@pytest.fixture
def test_health_vault_data():
    """Test health vault data"""
    return {
        "name": "Test Health Vault",
        "description": "Test vault for medical records",
        "encryption_enabled": True,
        "zk_proofs_enabled": True
    }


@pytest.fixture
def test_ai_agent_data():
    """Test AI agent data"""
    return {
        "name": "Test AI Agent",
        "agent_type": "diagnostic_agent",
        "capabilities": ["diagnosis", "federated_learning"],
        "hcs_topic_id": "0.0.789101",
        "profile_metadata": {
            "specialization": "general_medicine",
            "model_version": "v1.0.0"
        }
    }


@pytest.fixture
def test_consent_data():
    """Test consent data"""
    return {
        "provider_account_id": "0.0.654321",
        "record_types": ["lab_results", "imaging"],
        "duration_hours": 24,
        "compensation_rate": 5.0,
        "purpose": "Medical diagnosis"
    }


@pytest.fixture
def mock_hedera_client():
    """Mock Hedera client for testing"""
    class MockHederaClient:
        def __init__(self):
            self.account_id = "0.0.123456"
            self.private_key = None
        
        async def create_topic(self, memo: str):
            return {"topic_id": "0.0.789101"}
        
        async def submit_message(self, topic_id: str, message: str):
            return {"transaction_id": "0.0.123456@1234567890.123456789"}
        
        async def create_token(self, name: str, symbol: str, initial_supply: int):
            return {"token_id": "0.0.345678"}
        
        async def transfer_token(self, token_id: str, from_account: str, to_account: str, amount: int):
            return {"transaction_id": "0.0.123456@1234567890.123456789"}
    
    return MockHederaClient()


@pytest.fixture
def mock_ipfs_client():
    """Mock IPFS client for testing"""
    class MockIPFSClient:
        async def add_data(self, data: bytes):
            return "QmTestHash123456789"
        
        async def get_data(self, hash: str):
            return b"test_data"
    
    return MockIPFSClient()


@pytest.fixture
def mock_encryption_service():
    """Mock encryption service for testing"""
    class MockEncryptionService:
        def encrypt_data(self, data: bytes):
            return b"encrypted_" + data
        
        def decrypt_data(self, encrypted_data: bytes):
            return encrypted_data[10:]  # Remove "encrypted_" prefix
        
        def generate_zk_proof(self, statement: dict):
            return {"proof": "mock_proof", "public_inputs": ["input1", "input2"]}
        
        def verify_zk_proof(self, proof: dict, statement: dict):
            return True
    
    return MockEncryptionService()


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
    os.environ["HEDERA_PRIVATE_KEY"] = "test_hedera_private_key"
    os.environ["ENCRYPTION_KEY"] = "test_encryption_key_32_characters"
    yield
    # Cleanup
    for key in ["TESTING", "DATABASE_URL", "SECRET_KEY", "HEDERA_PRIVATE_KEY", "ENCRYPTION_KEY"]:
        os.environ.pop(key, None)
