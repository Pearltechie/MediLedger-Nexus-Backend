#!/usr/bin/env python3
"""
Generate secure AES-256 encryption key for MediLedger Nexus

This script generates a cryptographically secure AES-256 encryption key
for encrypting sensitive health data in the MediLedger Nexus platform.
"""

import secrets
import base64
import hashlib
import os
from datetime import datetime


def generate_aes256_key():
    """Generate a secure AES-256 encryption key"""
    # Generate 32 random bytes (256 bits) for AES-256
    key_bytes = secrets.token_bytes(32)
    
    # Encode as base64 for easy storage in environment variables
    key_base64 = base64.b64encode(key_bytes).decode('utf-8')
    
    # Also generate a hex version
    key_hex = key_bytes.hex()
    
    return {
        'key_bytes': key_bytes,
        'key_base64': key_base64,
        'key_hex': key_hex,
        'key_length': len(key_bytes),
        'generated_at': datetime.utcnow().isoformat()
    }


def generate_derived_keys(master_key: str):
    """Generate additional derived keys for different purposes"""
    # Create different keys for different purposes
    purposes = {
        'health_data': 'health_data_encryption',
        'consent_data': 'consent_data_encryption', 
        'research_data': 'research_data_encryption',
        'emergency_data': 'emergency_data_encryption',
        'user_credentials': 'user_credentials_encryption'
    }
    
    derived_keys = {}
    for purpose, salt in purposes.items():
        # Use PBKDF2 to derive keys
        derived_key = hashlib.pbkdf2_hmac('sha256', 
                                        master_key.encode('utf-8'),
                                        salt.encode('utf-8'),
                                        100000)  # 100,000 iterations
        
        derived_keys[purpose] = {
            'key_base64': base64.b64encode(derived_key).decode('utf-8'),
            'key_hex': derived_key.hex(),
            'salt': salt
        }
    
    return derived_keys


def update_env_file(encryption_key: str, env_file: str = ".env"):
    """Update .env file with the new encryption key"""
    try:
        # Read existing .env file
        env_content = ""
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # Update or add ENCRYPTION_KEY
        lines = env_content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('ENCRYPTION_KEY='):
                lines[i] = f'ENCRYPTION_KEY="{encryption_key}"'
                updated = True
                break
        
        if not updated:
            # Add new line if not found
            if lines and lines[-1].strip():
                lines.append('')
            lines.append(f'ENCRYPTION_KEY="{encryption_key}"')
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Updated {env_file} with new encryption key")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {env_file}: {e}")
        return False


def create_key_backup(key_info: dict, backup_file: str = "encryption_keys_backup.json"):
    """Create a backup of the encryption keys"""
    try:
        backup_data = {
            'generated_at': key_info['generated_at'],
            'master_key': {
                'base64': key_info['key_base64'],
                'hex': key_info['key_hex'],
                'length': key_info['key_length']
            },
            'security_notes': [
                'Store this file securely and separately from your application',
                'Never commit this file to version control',
                'Use different keys for different environments (dev/staging/prod)',
                'Rotate keys regularly for enhanced security',
                'Backup keys in multiple secure locations'
            ]
        }
        
        with open(backup_file, 'w') as f:
            import json
            json.dump(backup_data, f, indent=2)
        
        print(f"✅ Created key backup: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False


def main():
    """Main function"""
    print("🔐 MediLedger Nexus - AES-256 Encryption Key Generator")
    print("=" * 60)
    
    # Generate master encryption key
    print("🔑 Generating AES-256 encryption key...")
    key_info = generate_aes256_key()
    
    print(f"✅ Generated secure AES-256 key")
    print(f"📅 Generated at: {key_info['generated_at']}")
    print(f"📏 Key length: {key_info['key_length']} bytes (256 bits)")
    print(f"🔤 Base64 format: {key_info['key_base64']}")
    print(f"🔢 Hex format: {key_info['key_hex']}")
    
    # Generate derived keys
    print(f"\n🔗 Generating derived keys for different purposes...")
    derived_keys = generate_derived_keys(key_info['key_base64'])
    
    for purpose, key_data in derived_keys.items():
        print(f"   {purpose}: {key_data['key_base64'][:20]}...")
    
    # Update .env file
    print(f"\n📝 Updating environment configuration...")
    success = update_env_file(key_info['key_base64'])
    
    if success:
        print(f"✅ Environment file updated successfully")
    else:
        print(f"❌ Failed to update environment file")
    
    # Create backup
    print(f"\n💾 Creating key backup...")
    backup_success = create_key_backup(key_info)
    
    # Security recommendations
    print(f"\n🛡️ Security Recommendations:")
    print(f"   • Store the backup file securely and separately")
    print(f"   • Never commit encryption keys to version control")
    print(f"   • Use different keys for different environments")
    print(f"   • Rotate keys regularly (every 6-12 months)")
    print(f"   • Backup keys in multiple secure locations")
    print(f"   • Use hardware security modules (HSM) in production")
    
    # Show the key for immediate use
    print(f"\n🎯 Your AES-256 Encryption Key:")
    print(f"ENCRYPTION_KEY=\"{key_info['key_base64']}\"")
    
    print(f"\n🎉 Encryption key generation complete!")
    print(f"🔐 Your MediLedger Nexus platform is now ready with secure encryption")


if __name__ == "__main__":
    main()
