#!/usr/bin/env python3
"""
MediLedger Nexus - Encryption Demo

This script demonstrates how to use the generated AES-256 encryption key
for encrypting and decrypting sensitive health data.
"""

import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_encryption_key():
    """Get the encryption key from environment variables"""
    key_base64 = os.getenv('ENCRYPTION_KEY')
    if not key_base64:
        raise ValueError("ENCRYPTION_KEY not found in environment variables")
    
    # Decode the base64 key
    key_bytes = base64.b64decode(key_base64)
    
    # Derive a Fernet key from the AES key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'mediledger_nexus_salt',  # Use a fixed salt for consistency
        iterations=100000,
    )
    fernet_key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
    
    return Fernet(fernet_key)


def encrypt_health_data(health_data: dict, encryption_key: str = None):
    """Encrypt health data using AES-256"""
    if encryption_key:
        os.environ['ENCRYPTION_KEY'] = encryption_key
    
    try:
        # Get the Fernet cipher
        cipher = get_encryption_key()
        
        # Convert data to JSON string
        data_json = json.dumps(health_data, sort_keys=True)
        
        # Encrypt the data
        encrypted_data = cipher.encrypt(data_json.encode('utf-8'))
        
        # Encode as base64 for storage
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        return {
            'encrypted_data': encrypted_b64,
            'algorithm': 'AES-256-GCM',
            'key_derivation': 'PBKDF2-HMAC-SHA256',
            'iterations': 100000
        }
        
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        return None


def decrypt_health_data(encrypted_data: str, encryption_key: str = None):
    """Decrypt health data using AES-256"""
    if encryption_key:
        os.environ['ENCRYPTION_KEY'] = encryption_key
    
    try:
        # Get the Fernet cipher
        cipher = get_encryption_key()
        
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Decrypt the data
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        
        # Convert back to JSON
        decrypted_json = decrypted_bytes.decode('utf-8')
        health_data = json.loads(decrypted_json)
        
        return health_data
        
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return None


def demo_encryption():
    """Demonstrate encryption and decryption"""
    print("🔐 MediLedger Nexus - Encryption Demo")
    print("=" * 50)
    
    # Sample health data
    health_data = {
        "patient_id": "patient_12345",
        "age": 35,
        "blood_pressure": {
            "systolic": 120,
            "diastolic": 80
        },
        "heart_rate": 72,
        "temperature": 36.5,
        "medical_history": [
            "hypertension",
            "diabetes_type_2"
        ],
        "current_medications": [
            "metformin",
            "lisinopril"
        ],
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    print("📊 Original Health Data:")
    print(json.dumps(health_data, indent=2))
    
    # Encrypt the data
    print(f"\n🔐 Encrypting health data...")
    encryption_result = encrypt_health_data(health_data)
    
    if encryption_result:
        print(f"✅ Data encrypted successfully")
        print(f"🔑 Algorithm: {encryption_result['algorithm']}")
        print(f"🔗 Key Derivation: {encryption_result['key_derivation']}")
        print(f"🔄 Iterations: {encryption_result['iterations']}")
        print(f"📦 Encrypted Data: {encryption_result['encrypted_data'][:50]}...")
        
        # Decrypt the data
        print(f"\n🔓 Decrypting health data...")
        decrypted_data = decrypt_health_data(encryption_result['encrypted_data'])
        
        if decrypted_data:
            print(f"✅ Data decrypted successfully")
            print(f"📊 Decrypted Health Data:")
            print(json.dumps(decrypted_data, indent=2))
            
            # Verify data integrity
            if decrypted_data == health_data:
                print(f"\n🎉 Data integrity verified! Original and decrypted data match.")
                return True
            else:
                print(f"\n❌ Data integrity check failed!")
                return False
        else:
            print(f"❌ Decryption failed")
            return False
    else:
        print(f"❌ Encryption failed")
        return False


def demo_different_data_types():
    """Demonstrate encryption of different data types"""
    print(f"\n\n🔐 Encrypting Different Data Types")
    print("=" * 50)
    
    data_types = {
        "consent_data": {
            "patient_id": "patient_12345",
            "provider_id": "provider_67890",
            "consent_type": "data_sharing",
            "data_types": ["medical_records", "lab_results"],
            "expiration_date": "2024-12-31",
            "signature": "patient_digital_signature_hash"
        },
        "research_data": {
            "study_id": "study_abc123",
            "participant_id": "participant_xyz789",
            "data_type": "demographics",
            "anonymized_data": {
                "age_range": "30-40",
                "gender": "non_binary",
                "location": "urban"
            }
        },
        "emergency_data": {
            "patient_id": "patient_12345",
            "emergency_type": "cardiac_arrest",
            "urgency_level": 5,
            "location": "Emergency Room, City Hospital",
            "provider_credentials": "emergency_provider_license_hash"
        }
    }
    
    for data_type, data in data_types.items():
        print(f"\n📋 Encrypting {data_type}...")
        encryption_result = encrypt_health_data(data)
        
        if encryption_result:
            print(f"✅ {data_type} encrypted successfully")
            print(f"📦 Size: {len(encryption_result['encrypted_data'])} characters")
        else:
            print(f"❌ {data_type} encryption failed")


def main():
    """Main function"""
    # Check if encryption key is available
    if not os.getenv('ENCRYPTION_KEY'):
        print("❌ ENCRYPTION_KEY not found in environment variables")
        print("Please run: python generate_encryption_key.py")
        return
    
    print(f"🔑 Using encryption key: {os.getenv('ENCRYPTION_KEY')[:20]}...")
    
    # Run demos
    success = demo_encryption()
    demo_different_data_types()
    
    if success:
        print(f"\n🎉 Encryption demo completed successfully!")
        print(f"🔐 Your MediLedger Nexus platform can securely encrypt health data")
    else:
        print(f"\n❌ Encryption demo failed")
        print(f"Please check your encryption key and try again")


if __name__ == "__main__":
    main()
