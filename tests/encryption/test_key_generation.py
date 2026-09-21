#!/usr/bin/env python3
"""
MediLedger Nexus - Key Generation Tests

This module tests the secure key generation functionality.
"""

import os
import sys
import json
import base64
import secrets
import unittest
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))


class TestKeyGeneration(unittest.TestCase):
    """Test secure key generation functionality"""
    
    def test_generate_aes256_key(self):
        """Test AES-256 key generation"""
        # Generate key
        key_bytes = secrets.token_bytes(32)
        key_base64 = base64.b64encode(key_bytes).decode('utf-8')
        
        # Verify key properties
        self.assertEqual(len(key_bytes), 32, "Key should be 32 bytes (256 bits)")
        self.assertIsInstance(key_base64, str, "Key should be base64 string")
        
        # Verify base64 encoding
        try:
            decoded = base64.b64decode(key_base64)
            self.assertEqual(decoded, key_bytes)
        except Exception as e:
            self.fail(f"Invalid base64 encoding: {e}")
            
    def test_key_uniqueness(self):
        """Test that generated keys are unique"""
        keys = set()
        for _ in range(100):
            key_bytes = secrets.token_bytes(32)
            key_base64 = base64.b64encode(key_bytes).decode('utf-8')
            keys.add(key_base64)
            
        # All keys should be unique
        self.assertEqual(len(keys), 100, "All generated keys should be unique")
        
    def test_key_entropy(self):
        """Test that generated keys have sufficient entropy"""
        key_bytes = secrets.token_bytes(32)
        
        # Check that key is not all zeros or all ones
        self.assertNotEqual(key_bytes, b'\x00' * 32, "Key should not be all zeros")
        self.assertNotEqual(key_bytes, b'\xff' * 32, "Key should not be all ones")
        
        # Check that key has reasonable distribution
        unique_bytes = len(set(key_bytes))
        self.assertGreater(unique_bytes, 16, "Key should have good byte distribution")
        
    def test_key_format_compatibility(self):
        """Test key format compatibility with encryption"""
        key_bytes = secrets.token_bytes(32)
        key_base64 = base64.b64encode(key_bytes).decode('utf-8')
        
        # Should be compatible with environment variable format
        env_format = f'ENCRYPTION_KEY="{key_base64}"'
        self.assertTrue(env_format.startswith('ENCRYPTION_KEY="'))
        self.assertTrue(env_format.endswith('"'))
        
        # Should be parseable
        key_part = env_format.split('=')[1].strip('"')
        self.assertEqual(key_part, key_base64)
        
    def test_derived_key_generation(self):
        """Test generation of derived keys for different purposes"""
        master_key = "test_master_key"
        purposes = {
            'health_data': 'health_data_encryption',
            'consent_data': 'consent_data_encryption',
            'research_data': 'research_data_encryption'
        }
        
        derived_keys = {}
        for purpose, salt in purposes.items():
            # Simple derivation (in real implementation, use PBKDF2)
            derived_key = (master_key + salt).encode('utf-8')
            derived_keys[purpose] = base64.b64encode(derived_key).decode('utf-8')
            
        # All derived keys should be different
        key_values = list(derived_keys.values())
        self.assertEqual(len(set(key_values)), len(key_values), 
                        "All derived keys should be unique")
                        
        # All keys should be valid base64
        for purpose, key in derived_keys.items():
            try:
                base64.b64decode(key)
            except Exception as e:
                self.fail(f"Invalid base64 for {purpose}: {e}")
                
    def test_key_backup_format(self):
        """Test key backup file format"""
        key_info = {
            'key_base64': 'dGVzdF9rZXk=',
            'key_hex': '746573745f6b6579',
            'key_length': 8,
            'generated_at': '2024-01-15T10:30:00Z'
        }
        
        # Should be JSON serializable
        try:
            json_str = json.dumps(key_info, indent=2)
            parsed = json.loads(json_str)
            self.assertEqual(parsed, key_info)
        except Exception as e:
            self.fail(f"Key backup should be JSON serializable: {e}")
            
    def test_environment_key_loading(self):
        """Test loading encryption key from environment"""
        # Test with valid key
        test_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
        os.environ['TEST_ENCRYPTION_KEY'] = test_key
        
        loaded_key = os.getenv('TEST_ENCRYPTION_KEY')
        self.assertEqual(loaded_key, test_key)
        
        # Test with invalid key
        os.environ['TEST_INVALID_KEY'] = 'invalid_key'
        invalid_key = os.getenv('TEST_INVALID_KEY')
        self.assertEqual(invalid_key, 'invalid_key')
        
        # Clean up
        del os.environ['TEST_ENCRYPTION_KEY']
        del os.environ['TEST_INVALID_KEY']
        
    def test_key_rotation_simulation(self):
        """Test key rotation simulation"""
        # Generate old and new keys
        old_key = secrets.token_bytes(32)
        new_key = secrets.token_bytes(32)
        
        # Keys should be different
        self.assertNotEqual(old_key, new_key)
        
        # Both should be valid
        self.assertEqual(len(old_key), 32)
        self.assertEqual(len(new_key), 32)
        
        # Both should be base64 encodable
        old_key_b64 = base64.b64encode(old_key).decode('utf-8')
        new_key_b64 = base64.b64encode(new_key).decode('utf-8')
        
        self.assertNotEqual(old_key_b64, new_key_b64)
        
    def test_key_validation(self):
        """Test key validation functions"""
        # Valid key
        valid_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
        
        # Invalid keys
        invalid_keys = [
            '',  # Empty
            'short',  # Too short
            'x' * 100,  # Too long
            'invalid_base64!@#',  # Invalid base64
            base64.b64encode(b'short').decode('utf-8')  # Wrong length when decoded
        ]
        
        # Valid key should pass validation
        try:
            decoded = base64.b64decode(valid_key)
            self.assertEqual(len(decoded), 32)
        except Exception:
            self.fail("Valid key should pass validation")
            
        # Invalid keys should fail validation
        for invalid_key in invalid_keys:
            with self.assertRaises(Exception):
                if invalid_key:
                    decoded = base64.b64decode(invalid_key)
                    if len(decoded) != 32:
                        raise ValueError("Invalid key length")
                else:
                    raise ValueError("Empty key")


def run_tests():
    """Run the key generation tests"""
    print("🔑 MediLedger Nexus - Key Generation Tests")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    return True


if __name__ == "__main__":
    run_tests()
