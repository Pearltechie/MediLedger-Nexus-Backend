#!/usr/bin/env python3
"""
Hedera Key Generation Script for MediLedger Nexus

This script generates Hedera ED25519 key pairs for development and testing.
It can also create accounts on Hedera testnet if proper credentials are provided.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from hedera import (
        Client, 
        PrivateKey, 
        AccountCreateTransaction, 
        Hbar,
        AccountId
    )
    HEDERA_SDK_AVAILABLE = True
except ImportError:
    HEDERA_SDK_AVAILABLE = False
    print("⚠️  Hedera SDK not installed. Install with: pip install hedera-sdk")


def generate_key_pair() -> Dict[str, str]:
    """
    Generate a new ED25519 key pair
    
    Returns:
        Dict containing private and public keys in various formats
    """
    if not HEDERA_SDK_AVAILABLE:
        print("❌ Hedera SDK not available. Cannot generate keys.")
        return {}
    
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
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return key_info
        
    except Exception as e:
        print(f"❌ Error generating keys: {e}")
        return {}


async def create_hedera_account(
    operator_id: str,
    operator_key: str,
    network: str = "testnet",
    initial_balance: int = 1000
) -> Optional[Dict[str, Any]]:
    """
    Create a new Hedera account
    
    Args:
        operator_id: Your operator account ID
        operator_key: Your operator private key
        network: Network to use (testnet/mainnet)
        initial_balance: Initial balance in tinybars
        
    Returns:
        Dict containing account information
    """
    if not HEDERA_SDK_AVAILABLE:
        print("❌ Hedera SDK not available. Cannot create account.")
        return None
    
    try:
        # Create client
        if network == "testnet":
            client = Client.forTestnet()
        elif network == "mainnet":
            client = Client.forMainnet()
        else:
            raise ValueError("Network must be 'testnet' or 'mainnet'")
        
        # Set operator
        client.setOperator(AccountId.fromString(operator_id), PrivateKey.fromString(operator_key))
        
        print(f"=== Creating Hedera Account on {network} ===")
        print(f"Operator Account: {operator_id}")
        
        # Generate new key pair
        new_private_key = PrivateKey.generate()
        new_public_key = new_private_key.getPublicKey()
        
        print("\n=== Generated Key Pair ===")
        print("Private Key (DER):", new_private_key.toString())
        print("Public Key (DER):", new_public_key.toString())
        
        # Create account transaction
        account_create_transaction = AccountCreateTransaction()
        account_create_transaction.setKey(new_public_key)
        account_create_transaction.setInitialBalance(Hbar.fromTinybars(initial_balance))
        account_create_transaction.setAccountMemo("MediLedger Nexus Test Account")
        
        # Execute transaction
        print("\n=== Creating Account ===")
        account_create_response = account_create_transaction.execute(client)
        account_create_receipt = account_create_response.getReceipt(client)
        new_account_id = account_create_receipt.accountId
        
        print("✅ Account created successfully!")
        print("New Account ID:", new_account_id.toString())
        
        # Get account balance
        account_balance = client.getAccountBalance(new_account_id)
        print("Account Balance:", account_balance.toString())
        
        # Prepare account information
        account_info = {
            "account_id": new_account_id.toString(),
            "private_key": new_private_key.toString(),
            "public_key": new_public_key.toString(),
            "private_key_raw": new_private_key.toStringRaw(),
            "public_key_raw": new_public_key.toStringRaw(),
            "network": network,
            "initial_balance": initial_balance,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return account_info
        
    except Exception as e:
        print(f"❌ Error creating account: {e}")
        return None


def save_keys_to_env_file(key_info: Dict[str, str], filename: str = ".env.hedera"):
    """
    Save generated keys to environment file
    
    Args:
        key_info: Dictionary containing key information
        filename: Name of the environment file
    """
    try:
        env_content = f"""# Hedera Keys Generated on {datetime.utcnow().isoformat()}
HEDERA_PRIVATE_KEY={key_info.get('private_key_der', '')}
HEDERA_PUBLIC_KEY={key_info.get('public_key_der', '')}
HEDERA_PRIVATE_KEY_RAW={key_info.get('private_key_raw', '')}
HEDERA_PUBLIC_KEY_RAW={key_info.get('public_key_raw', '')}
HEDERA_KEY_TYPE={key_info.get('key_type', 'ED25519')}
"""
        
        with open(filename, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Keys saved to {filename}")
        
    except Exception as e:
        print(f"❌ Error saving keys: {e}")


def save_account_info(account_info: Dict[str, Any], filename: str = "hedera_account.json"):
    """
    Save account information to JSON file
    
    Args:
        account_info: Dictionary containing account information
        filename: Name of the JSON file
    """
    try:
        with open(filename, 'w') as f:
            json.dump(account_info, f, indent=2)
        
        print(f"✅ Account information saved to {filename}")
        
    except Exception as e:
        print(f"❌ Error saving account info: {e}")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Hedera keys and create accounts")
    parser.add_argument("--create-account", action="store_true", help="Create a new Hedera account")
    parser.add_argument("--operator-id", type=str, help="Operator account ID")
    parser.add_argument("--operator-key", type=str, help="Operator private key")
    parser.add_argument("--network", type=str, default="testnet", choices=["testnet", "mainnet"], help="Network to use")
    parser.add_argument("--initial-balance", type=int, default=1000, help="Initial balance in tinybars")
    parser.add_argument("--save-env", action="store_true", help="Save keys to .env file")
    
    args = parser.parse_args()
    
    if args.create_account:
        if not args.operator_id or not args.operator_key:
            print("❌ --operator-id and --operator-key are required for account creation")
            return
        
        account_info = await create_hedera_account(
            args.operator_id,
            args.operator_key,
            args.network,
            args.initial_balance
        )
        
        if account_info:
            save_account_info(account_info)
            if args.save_env:
                save_keys_to_env_file(account_info)
    else:
        # Generate keys only
        print("=== Generating Hedera Keys ===")
        key_info = generate_key_pair()
        
        if key_info:
            print("\n=== Generated Key Information ===")
            for key, value in key_info.items():
                print(f"{key}: {value}")
            
            if args.save_env:
                save_keys_to_env_file(key_info)
            
            # Save to JSON as well
            save_account_info(key_info, "hedera_keys.json")


if __name__ == "__main__":
    asyncio.run(main())
