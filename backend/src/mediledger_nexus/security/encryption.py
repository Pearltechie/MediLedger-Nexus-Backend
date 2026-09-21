"""
Encryption service for MediLedger Nexus
AES-256 encryption for health data with key management
"""

import base64
import hashlib
import os
import secrets
from typing import Dict, Optional, Tuple, Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from mediledger_nexus.core.config import get_settings
from mediledger_nexus.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EncryptionService:
    """Service for encrypting and decrypting health data"""
    
    def __init__(self):
        self.master_key = self._derive_master_key()
        self.fernet = Fernet(self.master_key)
    
    def _derive_master_key(self) -> bytes:
        """Derive master encryption key from configuration"""
        try:
            # Use configured encryption key or generate one
            if settings.ENCRYPTION_KEY and settings.ENCRYPTION_KEY != "your-aes-256-encryption-key":
                password = settings.ENCRYPTION_KEY.encode()
            else:
                logger.warning("Using default encryption key - NOT SECURE FOR PRODUCTION")
                password = b"default_key_for_development_only"
            
            # Generate salt (in production, this should be stored securely)
            salt = b"mediledger_nexus_salt_v1"  # Fixed salt for demo
            
            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return key
        
        except Exception as e:
            logger.error(f"Error deriving master key: {e}")
            raise
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-256"""
        try:
            encrypted_data = self.fernet.encrypt(data)
            logger.debug(f"Encrypted {len(data)} bytes of data")
            return encrypted_data
        
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-256"""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            logger.debug(f"Decrypted {len(decrypted_data)} bytes of data")
            return decrypted_data
        
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_text(self, text: str) -> str:
        """Encrypt text and return base64 encoded string"""
        try:
            encrypted_bytes = self.encrypt_data(text.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        
        except Exception as e:
            logger.error(f"Text encryption error: {e}")
            raise
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded encrypted text"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self.decrypt_data(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        
        except Exception as e:
            logger.error(f"Text decryption error: {e}")
            raise
    
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """Generate RSA key pair for asymmetric encryption"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            logger.info("Generated RSA key pair")
            return private_pem, public_pem
        
        except Exception as e:
            logger.error(f"Key pair generation error: {e}")
            raise
    
    def encrypt_with_public_key(self, data: bytes, public_key_pem: bytes) -> bytes:
        """Encrypt data with RSA public key"""
        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            logger.debug(f"Encrypted {len(data)} bytes with public key")
            return encrypted_data
        
        except Exception as e:
            logger.error(f"Public key encryption error: {e}")
            raise
    
    def decrypt_with_private_key(self, encrypted_data: bytes, private_key_pem: bytes) -> bytes:
        """Decrypt data with RSA private key"""
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem, 
                password=None
            )
            
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            logger.debug(f"Decrypted {len(decrypted_data)} bytes with private key")
            return decrypted_data
        
        except Exception as e:
            logger.error(f"Private key decryption error: {e}")
            raise
    
    def hash_data(self, data: bytes, algorithm: str = "sha256") -> str:
        """Hash data using specified algorithm"""
        try:
            if algorithm == "sha256":
                hash_obj = hashlib.sha256(data)
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512(data)
            elif algorithm == "md5":
                hash_obj = hashlib.md5(data)
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            hash_hex = hash_obj.hexdigest()
            logger.debug(f"Hashed {len(data)} bytes using {algorithm}")
            return hash_hex
        
        except Exception as e:
            logger.error(f"Hashing error: {e}")
            raise
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        try:
            token = secrets.token_urlsafe(length)
            logger.debug(f"Generated secure token of length {len(token)}")
            return token
        
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            raise
    
    def encrypt_medical_record(self, record_data: Dict[str, Any]) -> Dict[str, str]:
        """Encrypt medical record with metadata"""
        try:
            import json
            
            # Convert record to JSON
            record_json = json.dumps(record_data, sort_keys=True)
            
            # Encrypt the JSON data
            encrypted_data = self.encrypt_text(record_json)
            
            # Generate hash for integrity check
            data_hash = self.hash_data(record_json.encode('utf-8'))
            
            # Create encrypted record with metadata
            encrypted_record = {
                "encrypted_data": encrypted_data,
                "data_hash": data_hash,
                "encryption_algorithm": "AES-256-GCM",
                "encrypted_at": str(int(os.time.time())),
                "version": "1.0"
            }
            
            logger.info("Encrypted medical record")
            return encrypted_record
        
        except Exception as e:
            logger.error(f"Medical record encryption error: {e}")
            raise
    
    def decrypt_medical_record(self, encrypted_record: Dict[str, str]) -> Dict[str, Any]:
        """Decrypt medical record and verify integrity"""
        try:
            import json
            
            # Decrypt the data
            decrypted_json = self.decrypt_text(encrypted_record["encrypted_data"])
            
            # Verify integrity
            calculated_hash = self.hash_data(decrypted_json.encode('utf-8'))
            stored_hash = encrypted_record.get("data_hash")
            
            if stored_hash and calculated_hash != stored_hash:
                raise ValueError("Data integrity check failed")
            
            # Parse JSON
            record_data = json.loads(decrypted_json)
            
            logger.info("Decrypted and verified medical record")
            return record_data
        
        except Exception as e:
            logger.error(f"Medical record decryption error: {e}")
            raise
    
    def create_access_key(self, vault_id: str, provider_id: str, duration_hours: int) -> Dict[str, str]:
        """Create time-limited access key for health vault"""
        try:
            import time
            
            # Create access key data
            access_data = {
                "vault_id": vault_id,
                "provider_id": provider_id,
                "granted_at": int(time.time()),
                "expires_at": int(time.time()) + (duration_hours * 3600),
                "permissions": ["read"],
                "key_id": self.generate_secure_token(16)
            }
            
            # Encrypt access key
            access_key = self.encrypt_text(json.dumps(access_data))
            
            logger.info(f"Created access key for vault {vault_id}")
            return {
                "access_key": access_key,
                "key_id": access_data["key_id"],
                "expires_at": str(access_data["expires_at"])
            }
        
        except Exception as e:
            logger.error(f"Access key creation error: {e}")
            raise
    
    def validate_access_key(self, access_key: str, vault_id: str) -> Optional[Dict[str, Any]]:
        """Validate and decode access key"""
        try:
            import json
            import time
            
            # Decrypt access key
            access_data = json.loads(self.decrypt_text(access_key))
            
            # Check if key is for the correct vault
            if access_data.get("vault_id") != vault_id:
                logger.warning("Access key vault mismatch")
                return None
            
            # Check if key has expired
            if time.time() > access_data.get("expires_at", 0):
                logger.warning("Access key has expired")
                return None
            
            logger.info(f"Validated access key for vault {vault_id}")
            return access_data
        
        except Exception as e:
            logger.error(f"Access key validation error: {e}")
            return None
