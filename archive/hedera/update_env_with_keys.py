#!/usr/bin/env python3
"""
Update .env file with generated Hedera keys

This script reads generated keys and updates the .env file with the new credentials.
"""

import json
import os
import re
from datetime import datetime


def load_generated_keys(filename: str = "hedera_keys.json") -> dict:
    """Load generated keys from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File {filename} not found. Run generate_hedera_keys.py first.")
        return {}
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {filename}")
        return {}


def update_env_file(keys: dict, env_file: str = ".env"):
    """Update .env file with new keys"""
    if not keys:
        print("❌ No keys to update")
        return
    
    # Read existing .env file
    env_content = ""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
    else:
        print(f"⚠️  {env_file} not found, creating new one")
    
    # Update or add Hedera key variables
    updates = {
        'HEDERA_PRIVATE_KEY': keys.get('private_key_der', ''),
        'HEDERA_PUBLIC_KEY': keys.get('public_key_der', ''),
        'HEDERA_PRIVATE_KEY_RAW': keys.get('private_key_raw', ''),
        'HEDERA_PUBLIC_KEY_RAW': keys.get('public_key_raw', ''),
        'HEDERA_KEY_TYPE': keys.get('key_type', 'ED25519'),
        'HEDERA_KEY_GENERATED_AT': keys.get('generated_at', datetime.utcnow().isoformat())
    }
    
    # Update existing variables or add new ones
    for key, value in updates.items():
        pattern = rf'^{key}=.*$'
        replacement = f'{key}={value}'
        
        if re.search(pattern, env_content, re.MULTILINE):
            # Update existing variable
            env_content = re.sub(pattern, replacement, env_content, flags=re.MULTILINE)
            print(f"✅ Updated {key}")
        else:
            # Add new variable
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f'{replacement}\n'
            print(f"✅ Added {key}")
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Updated {env_file} with new Hedera keys")


def create_test_accounts_config(keys: dict, filename: str = "test_accounts.json"):
    """Create a test accounts configuration file"""
    if not keys:
        return
    
    test_accounts = {
        "test_accounts": [
            {
                "name": "Primary Test Account",
                "private_key": keys.get('private_key_der', ''),
                "public_key": keys.get('public_key_der', ''),
                "key_type": keys.get('key_type', 'ED25519'),
                "generated_at": keys.get('generated_at', ''),
                "purpose": "Development and testing"
            }
        ],
        "network": "testnet",
        "created_at": datetime.utcnow().isoformat()
    }
    
    with open(filename, 'w') as f:
        json.dump(test_accounts, f, indent=2)
    
    print(f"✅ Created {filename} with test account configuration")


def main():
    """Main function"""
    print("=== Updating Environment with Generated Keys ===")
    
    # Load generated keys
    keys = load_generated_keys()
    if not keys:
        return
    
    print(f"📋 Loaded keys generated at: {keys.get('generated_at', 'Unknown')}")
    
    # Update .env file
    update_env_file(keys)
    
    # Create test accounts config
    create_test_accounts_config(keys)
    
    print("\n=== Next Steps ===")
    print("1. Review the updated .env file")
    print("2. Create a Hedera account using the generated keys")
    print("3. Update HEDERA_ACCOUNT_ID in .env with your account ID")
    print("4. Test the integration with your MediLedger Nexus backend")
    
    print("\n=== Security Reminder ===")
    print("⚠️  Keep your private keys secure!")
    print("⚠️  Never commit private keys to version control!")
    print("⚠️  Use environment variables in production!")


if __name__ == "__main__":
    main()
