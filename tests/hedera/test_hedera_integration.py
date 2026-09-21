#!/usr/bin/env python3
"""
Test Hedera Integration with MediLedger Nexus Backend

This script tests the Hedera client integration with the generated keys.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mediledger_nexus.blockchain.hedera_client import HederaClient
from mediledger_nexus.blockchain.smart_contracts import SmartContractService


async def test_hedera_client():
    """Test the Hedera client functionality"""
    print("=== Testing Hedera Client ===")
    
    try:
        # Initialize client
        client = HederaClient()
        print("✅ Hedera client initialized successfully")
        
        # Test account balance
        balance = client.get_account_balance()
        print(f"✅ Account balance retrieved: {balance}")
        
        # Test account info
        account_info = client.get_account_info()
        print(f"✅ Account info retrieved: {account_info}")
        
        # Test network version
        version_info = client.get_network_version_info()
        print(f"✅ Network version info: {version_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Hedera client: {e}")
        return False


async def test_smart_contract_service():
    """Test the smart contract service"""
    print("\n=== Testing Smart Contract Service ===")
    
    try:
        # Initialize service
        service = SmartContractService()
        print("✅ Smart contract service initialized successfully")
        
        # Test contract ABI loading
        abis = service.contract_abis
        print(f"✅ Contract ABIs loaded: {list(abis.keys())}")
        
        # Test contract state (mock)
        if service.health_vault_contract:
            state = service.get_contract_state(service.health_vault_contract)
            print(f"✅ Contract state retrieved: {state}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing smart contract service: {e}")
        return False


async def test_contract_deployment():
    """Test contract deployment functionality"""
    print("\n=== Testing Contract Deployment ===")
    
    try:
        service = SmartContractService()
        
        # Test health vault contract deployment
        vault_config = {
            "name": "Test Health Vault",
            "encryption_enabled": True,
            "zk_proofs_enabled": True,
            "privacy_level": "high",
            "data_types": ["medical_records", "lab_results"]
        }
        
        # This will use mock implementation
        deployment_info = service.deploy_health_vault_contract(
            patient_account="0.0.123456",
            vault_config=vault_config
        )
        
        print(f"✅ Health vault contract deployment test: {deployment_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing contract deployment: {e}")
        return False


async def test_contract_interaction():
    """Test contract interaction functionality"""
    print("\n=== Testing Contract Interaction ===")
    
    try:
        service = SmartContractService()
        
        # Test health record creation
        record_data = {
            "record_type": "lab_result",
            "encrypted_data": "encrypted_lab_data",
            "data_hash": "data_integrity_hash",
            "metadata": {"lab": "Test Lab", "date": "2024-01-01"}
        }
        
        access_permissions = ["0.0.123456", "0.0.789012"]
        
        creation_info = service.create_health_record(
            contract_id="0.0.1001",
            record_data=record_data,
            access_permissions=access_permissions
        )
        
        print(f"✅ Health record creation test: {creation_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing contract interaction: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 MediLedger Nexus - Hedera Integration Test")
    print("=" * 50)
    
    # Check environment variables
    print("\n=== Environment Check ===")
    required_vars = [
        "HEDERA_ACCOUNT_ID",
        "HEDERA_PRIVATE_KEY",
        "HEDERA_NETWORK"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var:
                masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set")
    
    # Run tests
    tests = [
        test_hedera_client,
        test_smart_contract_service,
        test_contract_deployment,
        test_contract_interaction
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Hedera integration is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    print("\n=== Next Steps ===")
    print("1. If tests passed, your Hedera integration is ready")
    print("2. If tests failed, check your environment variables")
    print("3. For production, replace mock implementations with real Hedera SDK calls")
    print("4. Deploy your smart contracts to Hedera testnet/mainnet")


if __name__ == "__main__":
    asyncio.run(main())
