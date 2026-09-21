"""
Encryption service for MediLedger Nexus
"""

import json
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from ..core.config import get_settings

settings = get_settings()


class EncryptionService:
    """Encryption service for data protection"""
    
    @staticmethod
    def _get_fernet_key() -> Fernet:
        """Get Fernet encryption key from settings"""
        # Decode the base64 key
        key = base64.b64decode(settings.ENCRYPTION_KEY)
        return Fernet(key)
    
    @staticmethod
    def encrypt_data(data: Dict[str, Any]) -> str:
        """Encrypt data dictionary"""
        try:
            # Convert data to JSON string
            json_data = json.dumps(data)
            
            # Encrypt the data
            fernet = EncryptionService._get_fernet_key()
            encrypted_data = fernet.encrypt(json_data.encode())
            
            # Return base64 encoded encrypted data
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> Dict[str, Any]:
        """Decrypt data string"""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt the data
            fernet = EncryptionService._get_fernet_key()
            decrypted_data = fernet.decrypt(encrypted_bytes)
            
            # Convert back to dictionary
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def generate_data_hash(data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash of data"""
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, sort_keys=True)
            
            # Generate hash
            digest = hashes.Hash(hashes.SHA256())
            digest.update(json_data.encode())
            hash_bytes = digest.finalize()
            
            # Return hex string
            return hash_bytes.hex()
        except Exception as e:
            raise ValueError(f"Hash generation failed: {str(e)}")
    
    @staticmethod
    def verify_data_integrity(data: Dict[str, Any], expected_hash: str) -> bool:
        """Verify data integrity using hash"""
        try:
            actual_hash = EncryptionService.generate_data_hash(data)
            return actual_hash == expected_hash
        except Exception as e:
            return False
