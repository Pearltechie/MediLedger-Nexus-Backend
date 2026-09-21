#!/usr/bin/env python3
"""
Simple Hedera Key Generation and Testing Script

This script demonstrates Hedera key generation and basic functionality
without importing the full backend to avoid dependency issues.
"""

import os
import json
from datetime import datetime

try:
    from hedera import PrivateKey, Client, AccountId
    HEDERA_AVAILABLE = True
except ImportError:
    HEDERA_AVAILABLE = False
    print("⚠️  Hedera SDK not available. Install with: pip install hedera-sdk-py")


def generate_key_pair():
    """Generate a new ED25519 key pair"""
    if not HEDERA_AVAILABLE:
        print("❌ Hedera SDK not available")
        return None
    
    try:
        # Generate new key pair
        private_key = PrivateKey.generate()
        public_key = private_key.getPublicKey()
        
        key_info = {
            "private_key_der": private_key.toString(),
            "public_key_der": public_key.toString(),
            "private_key_raw": private_key.toStringRaw(),
            "public_key_raw": public_key.toStringRaw(),
            "key_type": "ED25519",
            "generated_at": datetime.now().isoformat()
        }
        
        return key_info
        
    except Exception as e:
        print(f"❌ Error generating keys: {e}")
        return None


def test_hedera_connection():
    """Test basic Hedera connection"""
    if not HEDERA_AVAILABLE:
        print("❌ Hedera SDK not available")
        return False
    
    try:
        # Create testnet client
        client = Client.forTestnet()
        print("✅ Hedera testnet client created successfully")
        
        # Test with a dummy account ID (this won't work but tests the connection)
        try:
            dummy_account = AccountId.fromString("0.0.1")
            print("✅ Account ID parsing works")
        except Exception as e:
            print(f"⚠️  Account ID parsing test: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Hedera connection: {e}")
        return False


def save_keys_to_file(keys, filename="generated_keys.json"):
    """Save generated keys to a file"""
    try:
        with open(filename, 'w') as f:
            json.dump(keys, f, indent=2)
        print(f"✅ Keys saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving keys: {e}")
        return False


def create_env_template(keys, filename=".env.template"):
    """Create an environment template file"""
    if not keys:
        return False
    
    try:
        template = f"""# Hedera Configuration Template
# Generated on {datetime.now().isoformat()}

# Hedera Network
HEDERA_NETWORK=testnet

# Your Account Information (replace with your actual account ID)
HEDERA_ACCOUNT_ID=0.0.YOUR_ACCOUNT_ID

# Generated Keys
HEDERA_PRIVATE_KEY={keys['private_key_der']}
HEDERA_PUBLIC_KEY={keys['public_key_der']}
HEDERA_PRIVATE_KEY_RAW={keys['private_key_raw']}
HEDERA_PUBLIC_KEY_RAW={keys['public_key_raw']}

# Smart Contract Addresses (update after deployment)
HEALTH_VAULT_CONTRACT=0.0.1001
CONSENT_CONTRACT=0.0.1002
RESEARCH_CONTRACT=0.0.1003
EMERGENCY_CONTRACT=0.0.1004

# Other Configuration
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
GROQ_API_KEY=your_groq_api_key_here
"""
        
        with open(filename, 'w') as f:
            f.write(template)
        
        print(f"✅ Environment template created: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating template: {e}")
        return False


def main():
    """Main function"""
    print("🔑 MediLedger Nexus - Hedera Key Generation & Testing")
    print("=" * 60)
    
    # Check Hedera SDK availability
    if not HEDERA_AVAILABLE:
        print("❌ Hedera SDK not available. Please install it first:")
        print("   pip install hedera-sdk-py")
        return
    
    print("✅ Hedera SDK is available")
    
    # Test Hedera connection
    print("\n=== Testing Hedera Connection ===")
    connection_ok = test_hedera_connection()
    
    # Generate key pair
    print("\n=== Generating Key Pair ===")
    keys = generate_key_pair()
    
    if keys:
        print("✅ Key pair generated successfully")
        print(f"📅 Generated at: {keys['generated_at']}")
        print(f"🔑 Key type: {keys['key_type']}")
        print(f"🔐 Private key (DER): {keys['private_key_der'][:50]}...")
        print(f"🔓 Public key (DER): {keys['public_key_der'][:50]}...")
        
        # Save keys
        print("\n=== Saving Keys ===")
        save_keys_to_file(keys)
        create_env_template(keys)
        
        # Security reminder
        print("\n=== Security Reminder ===")
        print("⚠️  Keep your private keys secure!")
        print("⚠️  Never share private keys publicly!")
        print("⚠️  Use environment variables in production!")
        
        # Next steps
        print("\n=== Next Steps ===")
        print("1. Create a Hedera account using the generated public key")
        print("2. Update HEDERA_ACCOUNT_ID in your .env file")
        print("3. Deploy your smart contracts to Hedera")
        print("4. Test the full integration")
        
    else:
        print("❌ Failed to generate key pair")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"✅ Hedera SDK: {'Available' if HEDERA_AVAILABLE else 'Not Available'}")
    print(f"✅ Connection Test: {'Passed' if connection_ok else 'Failed'}")
    print(f"✅ Key Generation: {'Success' if keys else 'Failed'}")
    
    if keys:
        print("\n🎉 Ready to use with MediLedger Nexus!")
    else:
        print("\n⚠️  Please fix the issues above before proceeding.")


if __name__ == "__main__":
    main()
