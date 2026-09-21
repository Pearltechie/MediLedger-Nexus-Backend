"""
Unit tests for security modules
"""

import pytest
from unittest.mock import Mock, patch
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa

from src.mediledger_nexus.security.encryption import EncryptionService


class TestEncryptionService:
    """Test EncryptionService class"""
    
    @pytest.fixture
    def encryption_service(self):
        """Create encryption service instance"""
        return EncryptionService()
    
    def test_generate_key(self, encryption_service):
        """Test symmetric key generation"""
        key = encryption_service.generate_key()
        
        assert key is not None
        assert isinstance(key, bytes)
        assert len(key) > 0
        
        # Test that generated keys are different
        key2 = encryption_service.generate_key()
        assert key != key2
    
    def test_encrypt_decrypt_data(self, encryption_service):
        """Test symmetric encryption and decryption"""
        original_data = "Sensitive medical information"
        key = encryption_service.generate_key()
        
        # Encrypt data
        encrypted_data = encryption_service.encrypt_data(original_data, key)
        
        assert encrypted_data != original_data
        assert isinstance(encrypted_data, str)
        assert len(encrypted_data) > len(original_data)
        
        # Decrypt data
        decrypted_data = encryption_service.decrypt_data(encrypted_data, key)
        
        assert decrypted_data == original_data
        assert isinstance(decrypted_data, str)
    
    def test_encrypt_decrypt_with_wrong_key(self, encryption_service):
        """Test decryption with wrong key fails"""
        original_data = "Sensitive data"
        key1 = encryption_service.generate_key()
        key2 = encryption_service.generate_key()
        
        encrypted_data = encryption_service.encrypt_data(original_data, key1)
        
        # Decryption with wrong key should fail
        with pytest.raises(Exception):
            encryption_service.decrypt_data(encrypted_data, key2)
    
    def test_encrypt_decrypt_empty_data(self, encryption_service):
        """Test encryption of empty data"""
        empty_data = ""
        key = encryption_service.generate_key()
        
        encrypted_data = encryption_service.encrypt_data(empty_data, key)
        decrypted_data = encryption_service.decrypt_data(encrypted_data, key)
        
        assert decrypted_data == empty_data
    
    def test_encrypt_decrypt_large_data(self, encryption_service):
        """Test encryption of large data"""
        large_data = "A" * 10000  # 10KB of data
        key = encryption_service.generate_key()
        
        encrypted_data = encryption_service.encrypt_data(large_data, key)
        decrypted_data = encryption_service.decrypt_data(encrypted_data, key)
        
        assert decrypted_data == large_data
    
    def test_generate_rsa_key_pair(self, encryption_service):
        """Test RSA key pair generation"""
        private_key, public_key = encryption_service.generate_rsa_key_pair()
        
        assert private_key is not None
        assert public_key is not None
        assert private_key != public_key
        
        # Test that keys are in PEM format
        assert isinstance(private_key, str)
        assert isinstance(public_key, str)
        assert "-----BEGIN PRIVATE KEY-----" in private_key
        assert "-----BEGIN PUBLIC KEY-----" in public_key
    
    def test_generate_rsa_key_pair_different_sizes(self, encryption_service):
        """Test RSA key pair generation with different key sizes"""
        # Test with 2048-bit keys
        private_key_2048, public_key_2048 = encryption_service.generate_rsa_key_pair(key_size=2048)
        
        # Test with 4096-bit keys
        private_key_4096, public_key_4096 = encryption_service.generate_rsa_key_pair(key_size=4096)
        
        # 4096-bit keys should be longer than 2048-bit keys
        assert len(private_key_4096) > len(private_key_2048)
        assert len(public_key_4096) > len(public_key_2048)
    
    def test_rsa_encrypt_decrypt(self, encryption_service):
        """Test RSA encryption and decryption"""
        original_data = "Small sensitive data"
        private_key, public_key = encryption_service.generate_rsa_key_pair()
        
        # Encrypt with public key
        encrypted_data = encryption_service.rsa_encrypt(original_data, public_key)
        
        assert encrypted_data != original_data
        assert isinstance(encrypted_data, str)
        assert len(encrypted_data) > len(original_data)
        
        # Decrypt with private key
        decrypted_data = encryption_service.rsa_decrypt(encrypted_data, private_key)
        
        assert decrypted_data == original_data
    
    def test_rsa_encrypt_decrypt_with_wrong_key(self, encryption_service):
        """Test RSA decryption with wrong key fails"""
        original_data = "Sensitive data"
        private_key1, public_key1 = encryption_service.generate_rsa_key_pair()
        private_key2, public_key2 = encryption_service.generate_rsa_key_pair()
        
        encrypted_data = encryption_service.rsa_encrypt(original_data, public_key1)
        
        # Decryption with wrong private key should fail
        with pytest.raises(Exception):
            encryption_service.rsa_decrypt(encrypted_data, private_key2)
    
    def test_rsa_encrypt_large_data_fails(self, encryption_service):
        """Test that RSA encryption fails with data too large"""
        # RSA can only encrypt small amounts of data
        large_data = "A" * 1000  # Too large for RSA
        private_key, public_key = encryption_service.generate_rsa_key_pair()
        
        with pytest.raises(Exception):
            encryption_service.rsa_encrypt(large_data, public_key)
    
    def test_hash_data(self, encryption_service):
        """Test data hashing"""
        data1 = "Data to hash"
        data2 = "Different data to hash"
        
        hash1 = encryption_service.hash_data(data1)
        hash2 = encryption_service.hash_data(data1)  # Same data
        hash3 = encryption_service.hash_data(data2)  # Different data
        
        # Same data should produce same hash
        assert hash1 == hash2
        
        # Different data should produce different hash
        assert hash1 != hash3
        
        # Hash should be hex string of specific length (SHA256 = 64 chars)
        assert isinstance(hash1, str)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)
    
    def test_hash_empty_data(self, encryption_service):
        """Test hashing empty data"""
        empty_data = ""
        hash_result = encryption_service.hash_data(empty_data)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64
    
    def test_create_access_key(self, encryption_service):
        """Test access key creation"""
        user_id = "user_123"
        resource_id = "resource_456"
        permissions = ["read", "write"]
        
        access_key = encryption_service.create_access_key(user_id, resource_id, permissions)
        
        assert access_key is not None
        assert isinstance(access_key, str)
        assert len(access_key) > 0
        
        # Test that different parameters produce different keys
        access_key2 = encryption_service.create_access_key("user_456", resource_id, permissions)
        assert access_key != access_key2
    
    def test_create_access_key_with_expiry(self, encryption_service):
        """Test access key creation with expiry"""
        user_id = "user_123"
        resource_id = "resource_456"
        permissions = ["read"]
        expires_in = 3600  # 1 hour
        
        access_key = encryption_service.create_access_key(
            user_id, resource_id, permissions, expires_in
        )
        
        assert access_key is not None
        assert isinstance(access_key, str)
    
    def test_validate_access_key(self, encryption_service):
        """Test access key validation"""
        user_id = "user_123"
        resource_id = "resource_456"
        permissions = ["read", "write"]
        
        # Create access key
        access_key = encryption_service.create_access_key(user_id, resource_id, permissions)
        
        # Validate with correct parameters
        is_valid = encryption_service.validate_access_key(access_key, user_id, resource_id)
        assert is_valid is True
        
        # Validate with wrong user_id
        is_valid = encryption_service.validate_access_key(access_key, "wrong_user", resource_id)
        assert is_valid is False
        
        # Validate with wrong resource_id
        is_valid = encryption_service.validate_access_key(access_key, user_id, "wrong_resource")
        assert is_valid is False
        
        # Validate with invalid key
        is_valid = encryption_service.validate_access_key("invalid_key", user_id, resource_id)
        assert is_valid is False
    
    def test_validate_expired_access_key(self, encryption_service):
        """Test validation of expired access key"""
        user_id = "user_123"
        resource_id = "resource_456"
        permissions = ["read"]
        expires_in = -1  # Already expired
        
        access_key = encryption_service.create_access_key(
            user_id, resource_id, permissions, expires_in
        )
        
        # Should be invalid due to expiry
        is_valid = encryption_service.validate_access_key(access_key, user_id, resource_id)
        assert is_valid is False
    
    def test_encrypt_medical_record(self, encryption_service):
        """Test medical record encryption"""
        medical_record = {
            "patient_id": "patient_123",
            "diagnosis": "Hypertension",
            "medications": ["lisinopril", "hydrochlorothiazide"],
            "test_results": {
                "blood_pressure": "140/90",
                "heart_rate": 75
            },
            "notes": "Patient shows signs of improvement"
        }
        
        encrypted_record = encryption_service.encrypt_medical_record(medical_record)
        
        assert "encrypted_data" in encrypted_record
        assert "encryption_key" in encrypted_record
        assert "metadata" in encrypted_record
        
        # Encrypted data should be different from original
        assert encrypted_record["encrypted_data"] != json.dumps(medical_record)
        
        # Metadata should contain useful information
        metadata = encrypted_record["metadata"]
        assert "timestamp" in metadata
        assert "algorithm" in metadata
        assert "record_hash" in metadata
    
    def test_decrypt_medical_record(self, encryption_service):
        """Test medical record decryption"""
        medical_record = {
            "patient_id": "patient_456",
            "diagnosis": "Diabetes Type 2",
            "medications": ["metformin"],
            "test_results": {"glucose": "180 mg/dL"}
        }
        
        # Encrypt record
        encrypted_record = encryption_service.encrypt_medical_record(medical_record)
        
        # Decrypt record
        decrypted_record = encryption_service.decrypt_medical_record(
            encrypted_record["encrypted_data"],
            encrypted_record["encryption_key"]
        )
        
        assert decrypted_record == medical_record
    
    def test_decrypt_medical_record_with_wrong_key(self, encryption_service):
        """Test medical record decryption with wrong key fails"""
        medical_record = {"patient_id": "patient_789", "diagnosis": "Flu"}
        
        # Encrypt record
        encrypted_record = encryption_service.encrypt_medical_record(medical_record)
        
        # Try to decrypt with wrong key
        wrong_key = encryption_service.generate_key()
        
        with pytest.raises(Exception):
            encryption_service.decrypt_medical_record(
                encrypted_record["encrypted_data"],
                wrong_key
            )
    
    def test_encrypt_medical_record_with_custom_key(self, encryption_service):
        """Test medical record encryption with custom key"""
        medical_record = {"patient_id": "patient_custom", "diagnosis": "Custom test"}
        custom_key = encryption_service.generate_key()
        
        encrypted_record = encryption_service.encrypt_medical_record(
            medical_record, 
            encryption_key=custom_key
        )
        
        # Should use the provided key
        assert encrypted_record["encryption_key"] == custom_key
        
        # Should be able to decrypt with the same key
        decrypted_record = encryption_service.decrypt_medical_record(
            encrypted_record["encrypted_data"],
            custom_key
        )
        
        assert decrypted_record == medical_record
    
    def test_medical_record_integrity_verification(self, encryption_service):
        """Test medical record integrity verification"""
        medical_record = {
            "patient_id": "patient_integrity",
            "diagnosis": "Test diagnosis",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        encrypted_record = encryption_service.encrypt_medical_record(medical_record)
        
        # Verify integrity using hash
        original_hash = encrypted_record["metadata"]["record_hash"]
        
        # Decrypt and re-encrypt to verify hash
        decrypted_record = encryption_service.decrypt_medical_record(
            encrypted_record["encrypted_data"],
            encrypted_record["encryption_key"]
        )
        
        # Hash should match
        new_hash = encryption_service.hash_data(json.dumps(decrypted_record, sort_keys=True))
        assert original_hash == new_hash
    
    def test_key_derivation_consistency(self, encryption_service):
        """Test that key derivation is consistent"""
        password = "user_password_123"
        salt = b"consistent_salt"
        
        # Derive key multiple times with same parameters
        key1 = encryption_service.derive_key_from_password(password, salt)
        key2 = encryption_service.derive_key_from_password(password, salt)
        
        assert key1 == key2
        
        # Different password should produce different key
        key3 = encryption_service.derive_key_from_password("different_password", salt)
        assert key1 != key3
        
        # Different salt should produce different key
        key4 = encryption_service.derive_key_from_password(password, b"different_salt")
        assert key1 != key4
    
    def test_secure_random_generation(self, encryption_service):
        """Test secure random number generation"""
        # Generate multiple random values
        random_values = [encryption_service.generate_secure_random(32) for _ in range(10)]
        
        # All values should be different
        assert len(set(random_values)) == len(random_values)
        
        # All values should be the correct length
        for value in random_values:
            assert len(value) == 32
            assert isinstance(value, bytes)
    
    def test_encryption_performance(self, encryption_service):
        """Test encryption performance with various data sizes"""
        import time
        
        data_sizes = [100, 1000, 10000]  # bytes
        
        for size in data_sizes:
            data = "A" * size
            key = encryption_service.generate_key()
            
            # Measure encryption time
            start_time = time.time()
            encrypted_data = encryption_service.encrypt_data(data, key)
            encryption_time = time.time() - start_time
            
            # Measure decryption time
            start_time = time.time()
            decrypted_data = encryption_service.decrypt_data(encrypted_data, key)
            decryption_time = time.time() - start_time
            
            # Verify correctness
            assert decrypted_data == data
            
            # Performance should be reasonable (less than 1 second for test data)
            assert encryption_time < 1.0
            assert decryption_time < 1.0
