#!/usr/bin/env python3
"""
MediLedger Nexus - AES-256 Encryption Tests

This module tests the AES-256 encryption functionality for health data.
"""

import os
import sys
import json
import base64
import unittest
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class TestAESEncryption(unittest.TestCase):
    """Test AES-256 encryption functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.encryption_key = os.getenv('ENCRYPTION_KEY')
        if not cls.encryption_key:
            raise unittest.SkipTest("ENCRYPTION_KEY not found in environment")
            
        if not CRYPTOGRAPHY_AVAILABLE:
            raise unittest.SkipTest("cryptography library not available")
            
    def setUp(self):
        """Set up each test"""
        self.sample_health_data = {
            "patient_id": "test_patient_123",
            "age": 30,
            "blood_pressure": {
                "systolic": 120,
                "diastolic": 80
            },
            "heart_rate": 72,
            "temperature": 36.5,
            "medical_history": ["hypertension"],
            "current_medications": ["metformin"],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    def get_cipher(self):
        """Get Fernet cipher for encryption/decryption"""
        key_bytes = base64.b64decode(self.encryption_key)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'mediledger_nexus_salt',
            iterations=100000,
        )
        fernet_key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        return Fernet(fernet_key)
        
    def test_encryption_key_format(self):
        """Test that encryption key is in correct format"""
        # Should be base64 encoded
        try:
            decoded = base64.b64decode(self.encryption_key)
            self.assertEqual(len(decoded), 32, "Key should be 32 bytes (256 bits)")
        except Exception as e:
            self.fail(f"Invalid encryption key format: {e}")
            
    def test_encrypt_health_data(self):
        """Test encrypting health data"""
        cipher = self.get_cipher()
        data_json = json.dumps(self.sample_health_data, sort_keys=True)
        encrypted_data = cipher.encrypt(data_json.encode('utf-8'))
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Should be different from original
        self.assertNotEqual(encrypted_b64, data_json)
        
        # Should be valid base64
        try:
            base64.b64decode(encrypted_b64)
        except Exception as e:
            self.fail(f"Encrypted data is not valid base64: {e}")
            
    def test_decrypt_health_data(self):
        """Test decrypting health data"""
        cipher = self.get_cipher()
        data_json = json.dumps(self.sample_health_data, sort_keys=True)
        encrypted_data = cipher.encrypt(data_json.encode('utf-8'))
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Decrypt
        encrypted_bytes = base64.b64decode(encrypted_b64)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_json = decrypted_bytes.decode('utf-8')
        decrypted_data = json.loads(decrypted_json)
        
        # Should match original
        self.assertEqual(decrypted_data, self.sample_health_data)
        
    def test_data_integrity(self):
        """Test data integrity through encryption/decryption cycle"""
        cipher = self.get_cipher()
        data_json = json.dumps(self.sample_health_data, sort_keys=True)
        
        # Encrypt
        encrypted_data = cipher.encrypt(data_json.encode('utf-8'))
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Decrypt
        encrypted_bytes = base64.b64decode(encrypted_b64)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_json = decrypted_bytes.decode('utf-8')
        decrypted_data = json.loads(decrypted_json)
        
        # Verify integrity
        self.assertEqual(decrypted_data, self.sample_health_data)
        
    def test_different_data_types(self):
        """Test encryption of different data types"""
        data_types = {
            "consent_data": {
                "patient_id": "patient_123",
                "provider_id": "provider_456",
                "consent_type": "data_sharing",
                "expiration_date": "2024-12-31"
            },
            "research_data": {
                "study_id": "study_abc",
                "participant_id": "participant_xyz",
                "data_type": "demographics",
                "anonymized_data": {"age_range": "30-40"}
            },
            "emergency_data": {
                "patient_id": "patient_123",
                "emergency_type": "cardiac_arrest",
                "urgency_level": 5,
                "location": "Emergency Room"
            }
        }
        
        cipher = self.get_cipher()
        
        for data_type, data in data_types.items():
            with self.subTest(data_type=data_type):
                data_json = json.dumps(data, sort_keys=True)
                encrypted_data = cipher.encrypt(data_json.encode('utf-8'))
                encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
                
                # Decrypt and verify
                encrypted_bytes = base64.b64decode(encrypted_b64)
                decrypted_bytes = cipher.decrypt(encrypted_bytes)
                decrypted_json = decrypted_bytes.decode('utf-8')
                decrypted_data = json.loads(decrypted_json)
                
                self.assertEqual(decrypted_data, data)
                
    def test_encryption_security(self):
        """Test encryption security properties"""
        cipher = self.get_cipher()
        data_json = json.dumps(self.sample_health_data, sort_keys=True)
        
        # Encrypt same data multiple times
        encrypted_results = []
        for _ in range(5):
            encrypted_data = cipher.encrypt(data_json.encode('utf-8'))
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            encrypted_results.append(encrypted_b64)
            
        # Each encryption should produce different results (due to random IV)
        for i in range(len(encrypted_results)):
            for j in range(i + 1, len(encrypted_results)):
                self.assertNotEqual(encrypted_results[i], encrypted_results[j],
                                  "Encryption should produce different results each time")
                                  
    def test_invalid_key_handling(self):
        """Test handling of invalid encryption keys"""
        # Test with invalid base64
        with self.assertRaises(Exception):
            base64.b64decode("invalid_base64_key")
            
        # Test with wrong key length
        short_key = base64.b64encode(b"short_key").decode('utf-8')
        with self.assertRaises(Exception):
            key_bytes = base64.b64decode(short_key)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'mediledger_nexus_salt',
                iterations=100000,
            )
            fernet_key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
            Fernet(fernet_key)
            
    def test_large_data_encryption(self):
        """Test encryption of large data sets"""
        # Create large health data
        large_data = {
            "patient_id": "patient_large_test",
            "medical_records": [
                {
                    "date": f"2024-01-{i:02d}",
                    "diagnosis": f"Diagnosis {i}",
                    "treatment": f"Treatment {i}",
                    "notes": f"Detailed medical notes for record {i}. " * 100
                }
                for i in range(1, 101)  # 100 records
            ]
        }
        
        cipher = self.get_cipher()
        data_json = json.dumps(large_data, sort_keys=True)
        
        # Should handle large data
        encrypted_data = cipher.encrypt(data_json.encode('utf-8'))
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Decrypt and verify
        encrypted_bytes = base64.b64decode(encrypted_b64)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_json = decrypted_bytes.decode('utf-8')
        decrypted_data = json.loads(decrypted_json)
        
        self.assertEqual(decrypted_data, large_data)


def run_tests():
    """Run the encryption tests"""
    print("🔐 MediLedger Nexus - AES-256 Encryption Tests")
    print("=" * 60)
    
    # Check prerequisites
    if not CRYPTOGRAPHY_AVAILABLE:
        print("❌ cryptography library not available")
        print("Install with: pip install cryptography")
        return False
        
    if not os.getenv('ENCRYPTION_KEY'):
        print("❌ ENCRYPTION_KEY not found in environment")
        print("Set with: export ENCRYPTION_KEY='your-key'")
        return False
        
    # Run tests
    unittest.main(verbosity=2, exit=False)
    return True


if __name__ == "__main__":
    run_tests()
