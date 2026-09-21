"""
Unit tests for database models
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.mediledger_nexus.models.user import User
from src.mediledger_nexus.models.health_vault import HealthVault
from src.mediledger_nexus.models import Base


class TestUserModel:
    """Test User model"""
    
    @pytest.fixture
    def user_data(self):
        """Sample user data"""
        return {
            "email": "test@example.com",
            "full_name": "Test User",
            "password_hash": "hashed_password",
            "hedera_account_id": "0.0.123456",
            "user_type": "patient",
            "is_active": True
        }
    
    def test_user_creation(self, user_data):
        """Test user model creation"""
        user = User(**user_data)
        
        assert user.email == user_data["email"]
        assert user.full_name == user_data["full_name"]
        assert user.password_hash == user_data["password_hash"]
        assert user.hedera_account_id == user_data["hedera_account_id"]
        assert user.user_type == user_data["user_type"]
        assert user.is_active == user_data["is_active"]
    
    def test_user_defaults(self):
        """Test user model defaults"""
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password"
        )
        
        assert user.user_type == "patient"  # Default value
        assert user.is_active is True  # Default value
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_string_representation(self, user_data):
        """Test user string representation"""
        user = User(**user_data)
        user.id = 1
        
        str_repr = str(user)
        assert "User" in str_repr
        assert user.email in str_repr or str(user.id) in str_repr
    
    def test_user_emergency_info(self, user_data):
        """Test user emergency information"""
        emergency_info = {
            "blood_type": "O+",
            "allergies": ["penicillin"],
            "emergency_contact": {
                "name": "Jane Doe",
                "phone": "+1234567890"
            }
        }
        
        user_data["emergency_info"] = emergency_info
        user = User(**user_data)
        
        assert user.emergency_info == emergency_info
        assert user.emergency_info["blood_type"] == "O+"
    
    def test_user_profile_metadata(self, user_data):
        """Test user profile metadata"""
        profile_metadata = {
            "preferences": {"language": "en", "timezone": "UTC"},
            "settings": {"notifications": True}
        }
        
        user_data["profile_metadata"] = profile_metadata
        user = User(**user_data)
        
        assert user.profile_metadata == profile_metadata
        assert user.profile_metadata["preferences"]["language"] == "en"
    
    def test_user_timestamps(self, user_data):
        """Test user timestamp handling"""
        user = User(**user_data)
        
        # Should have created_at and updated_at
        assert user.created_at is not None
        assert user.updated_at is not None
        
        # Should be datetime objects
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)


class TestHealthVaultModel:
    """Test HealthVault model"""
    
    @pytest.fixture
    def vault_data(self):
        """Sample vault data"""
        return {
            "name": "Primary Health Vault",
            "description": "Main vault for medical records",
            "user_id": 1,
            "encryption_enabled": True,
            "zk_proofs_enabled": True,
            "privacy_level": "high"
        }
    
    def test_vault_creation(self, vault_data):
        """Test health vault model creation"""
        vault = HealthVault(**vault_data)
        
        assert vault.name == vault_data["name"]
        assert vault.description == vault_data["description"]
        assert vault.user_id == vault_data["user_id"]
        assert vault.encryption_enabled == vault_data["encryption_enabled"]
        assert vault.zk_proofs_enabled == vault_data["zk_proofs_enabled"]
        assert vault.privacy_level == vault_data["privacy_level"]
    
    def test_vault_defaults(self):
        """Test health vault model defaults"""
        vault = HealthVault(
            name="Test Vault",
            user_id=1
        )
        
        assert vault.encryption_enabled is True  # Default value
        assert vault.zk_proofs_enabled is False  # Default value
        assert vault.privacy_level == "medium"  # Default value
        assert vault.is_active is True  # Default value
        assert vault.created_at is not None
        assert vault.updated_at is not None
    
    def test_vault_metadata(self, vault_data):
        """Test vault metadata"""
        metadata = {
            "data_types": ["lab_results", "imaging"],
            "retention_policy": "7_years",
            "backup_enabled": True
        }
        
        vault_data["metadata"] = metadata
        vault = HealthVault(**vault_data)
        
        assert vault.metadata == metadata
        assert "lab_results" in vault.metadata["data_types"]
    
    def test_vault_string_representation(self, vault_data):
        """Test vault string representation"""
        vault = HealthVault(**vault_data)
        vault.id = 1
        
        str_repr = str(vault)
        assert "HealthVault" in str_repr
        assert vault.name in str_repr or str(vault.id) in str_repr


class TestModelIntegration:
    """Test model integration and relationships"""
    
    @pytest.fixture
    def in_memory_db(self):
        """Create in-memory SQLite database for testing"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        yield session
        
        session.close()
    
    def test_user_vault_relationship(self, in_memory_db):
        """Test user-vault relationship"""
        # Create user
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password",
            hedera_account_id="0.0.123456"
        )
        in_memory_db.add(user)
        in_memory_db.commit()
        
        # Create vault for user
        vault = HealthVault(
            name="Test Vault",
            description="Test vault description",
            user_id=user.id,
            encryption_enabled=True
        )
        in_memory_db.add(vault)
        in_memory_db.commit()
        
        # Test relationship
        assert vault.user_id == user.id
    
    def test_model_crud_operations(self, in_memory_db):
        """Test basic CRUD operations"""
        # Create
        user = User(
            email="crud@example.com",
            full_name="CRUD User",
            password_hash="hashed_password"
        )
        in_memory_db.add(user)
        in_memory_db.commit()
        
        user_id = user.id
        assert user_id is not None
        
        # Read
        retrieved_user = in_memory_db.query(User).filter(User.id == user_id).first()
        assert retrieved_user is not None
        assert retrieved_user.email == "crud@example.com"
        
        # Update
        retrieved_user.full_name = "Updated User"
        in_memory_db.commit()
        
        updated_user = in_memory_db.query(User).filter(User.id == user_id).first()
        assert updated_user.full_name == "Updated User"
        
        # Delete
        in_memory_db.delete(updated_user)
        in_memory_db.commit()
        
        deleted_user = in_memory_db.query(User).filter(User.id == user_id).first()
        assert deleted_user is None
