#!/usr/bin/env python3
"""
MediLedger Nexus - zk-SNARK Testing Script

This script demonstrates the zk-SNARK functionality for health data validation,
consent management, and emergency access without revealing sensitive information.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the backend src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from mediledger_nexus.blockchain.zk_proofs import ZKProofManager


def test_health_data_validation():
    """Test health data validation with zk-SNARKs"""
    print("🏥 Testing Health Data Validation with zk-SNARKs")
    print("=" * 60)
    
    # Initialize ZK proof manager
    zk_manager = ZKProofManager()
    
    # Check if circuit is set up
    if not zk_manager.is_circuit_setup("health_data_validator"):
        print("❌ Health data validator circuit not set up")
        print("   Run: python setup_zk_snarks.py")
        return False
    
    # Sample health data
    health_data = {
        "age": 35,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "heart_rate": 72,
        "temperature": 36.5,  # Celsius
        "weight": 70,  # kg
        "height": 175  # cm
    }
    
    # Validation constraints
    constraints = {
        "min_age": 18,
        "max_age": 100,
        "max_systolic": 180,
        "max_diastolic": 120,
        "max_heart_rate": 200,
        "max_temperature": 40.0  # 40°C
    }
    
    patient_id = "patient_12345"
    timestamp = datetime.utcnow().isoformat()
    
    print(f"📊 Health Data: {health_data}")
    print(f"🔒 Patient ID: {patient_id}")
    print(f"⏰ Timestamp: {timestamp}")
    print(f"📏 Constraints: {constraints}")
    
    # Generate proof
    print("\n🔐 Generating zk-SNARK proof...")
    start_time = time.time()
    
    proof = zk_manager.generate_health_data_proof(
        health_data=health_data,
        patient_id=patient_id,
        timestamp=timestamp,
        constraints=constraints
    )
    
    generation_time = time.time() - start_time
    
    if proof:
        print(f"✅ Proof generated successfully in {generation_time:.2f} seconds")
        print(f"🔑 Circuit Type: {proof.get('circuit_type')}")
        print(f"📅 Generated At: {proof.get('generated_at')}")
        print(f"🔒 Patient Hash: {proof.get('patient_id_hash', '')[:16]}...")
        print(f"📊 Data Hash: {proof.get('data_hash', '')[:16]}...")
        
        # Verify proof
        print("\n🔍 Verifying proof...")
        start_time = time.time()
        
        is_valid = zk_manager.verify_proof("health_data_validator", proof)
        verification_time = time.time() - start_time
        
        if is_valid:
            print(f"✅ Proof verified successfully in {verification_time:.2f} seconds")
            print("🎉 Health data is valid without revealing sensitive information!")
            return True
        else:
            print("❌ Proof verification failed")
            return False
    else:
        print("❌ Proof generation failed")
        return False


def test_consent_validation():
    """Test consent validation with zk-SNARKs"""
    print("\n\n📋 Testing Consent Validation with zk-SNARKs")
    print("=" * 60)
    
    zk_manager = ZKProofManager()
    
    if not zk_manager.is_circuit_setup("consent_proof"):
        print("❌ Consent proof circuit not set up")
        return False
    
    # Sample consent data
    consent_data = {
        "consent_timestamp": int(datetime.utcnow().timestamp()),
        "expiration_timestamp": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
        "data_types_consented": 0b1111,  # Binary: all data types consented
        "signature": "patient_digital_signature_hash",
        "min_consent_duration": 3600,  # 1 hour
        "max_consent_duration": 86400 * 365,  # 1 year
        "required_data_types": 0b1010  # Binary: specific data types required
    }
    
    patient_id = "patient_12345"
    provider_id = "provider_67890"
    current_timestamp = int(datetime.utcnow().timestamp())
    
    print(f"📋 Consent Data: {consent_data}")
    print(f"👤 Patient ID: {patient_id}")
    print(f"🏥 Provider ID: {provider_id}")
    print(f"⏰ Current Time: {current_timestamp}")
    
    # Generate proof
    print("\n🔐 Generating consent proof...")
    start_time = time.time()
    
    proof = zk_manager.generate_consent_proof(
        consent_data=consent_data,
        patient_id=patient_id,
        provider_id=provider_id,
        current_timestamp=current_timestamp
    )
    
    generation_time = time.time() - start_time
    
    if proof:
        print(f"✅ Consent proof generated in {generation_time:.2f} seconds")
        print(f"🔑 Circuit Type: {proof.get('circuit_type')}")
        print(f"🔒 Patient Hash: {proof.get('patient_id_hash', '')[:16]}...")
        print(f"🏥 Provider Hash: {proof.get('provider_id_hash', '')[:16]}...")
        
        # Verify proof
        print("\n🔍 Verifying consent proof...")
        start_time = time.time()
        
        is_valid = zk_manager.verify_proof("consent_proof", proof)
        verification_time = time.time() - start_time
        
        if is_valid:
            print(f"✅ Consent proof verified in {verification_time:.2f} seconds")
            print("🎉 Valid consent proven without revealing consent details!")
            return True
        else:
            print("❌ Consent proof verification failed")
            return False
    else:
        print("❌ Consent proof generation failed")
        return False


def test_emergency_access():
    """Test emergency access validation with zk-SNARKs"""
    print("\n\n🚨 Testing Emergency Access with zk-SNARKs")
    print("=" * 60)
    
    zk_manager = ZKProofManager()
    
    if not zk_manager.is_circuit_setup("emergency_access"):
        print("❌ Emergency access circuit not set up")
        return False
    
    # Sample emergency data
    emergency_data = {
        "emergency_timestamp": int(datetime.utcnow().timestamp()),
        "emergency_type": 1,  # 1=cardiac, 2=trauma, 3=stroke, etc.
        "urgency_level": 5,  # 1-5, 5 being most urgent
        "location": "Emergency Room, City Hospital",
        "provider_credentials": "emergency_provider_license_hash",
        "max_access_duration": 3600,  # 1 hour
        "min_urgency_level": 3  # Level 3+ for access
    }
    
    patient_id = "patient_12345"
    provider_id = "emergency_provider_999"
    current_timestamp = int(datetime.utcnow().timestamp())
    
    print(f"🚨 Emergency Data: {emergency_data}")
    print(f"👤 Patient ID: {patient_id}")
    print(f"🏥 Emergency Provider: {provider_id}")
    print(f"⏰ Current Time: {current_timestamp}")
    
    # Generate proof
    print("\n🔐 Generating emergency access proof...")
    start_time = time.time()
    
    proof = zk_manager.generate_emergency_access_proof(
        emergency_data=emergency_data,
        patient_id=patient_id,
        provider_id=provider_id,
        current_timestamp=current_timestamp
    )
    
    generation_time = time.time() - start_time
    
    if proof:
        print(f"✅ Emergency access proof generated in {generation_time:.2f} seconds")
        print(f"🔑 Circuit Type: {proof.get('circuit_type')}")
        print(f"🚨 Emergency Type: {proof.get('emergency_type')}")
        print(f"⚡ Urgency Level: {proof.get('urgency_level')}")
        print(f"🔒 Patient Hash: {proof.get('patient_id_hash', '')[:16]}...")
        
        # Verify proof
        print("\n🔍 Verifying emergency access proof...")
        start_time = time.time()
        
        is_valid = zk_manager.verify_proof("emergency_access", proof)
        verification_time = time.time() - start_time
        
        if is_valid:
            print(f"✅ Emergency access proof verified in {verification_time:.2f} seconds")
            print("🎉 Legitimate emergency access proven without revealing patient details!")
            return True
        else:
            print("❌ Emergency access proof verification failed")
            return False
    else:
        print("❌ Emergency access proof generation failed")
        return False


def test_circuit_setup():
    """Test circuit setup status"""
    print("🔧 Testing Circuit Setup Status")
    print("=" * 60)
    
    zk_manager = ZKProofManager()
    
    circuits = zk_manager.list_circuits()
    print(f"📋 Available circuits: {len(circuits)}")
    
    for circuit_name in circuits:
        is_setup = zk_manager.is_circuit_setup(circuit_name)
        status = "✅ Ready" if is_setup else "❌ Not Setup"
        info = zk_manager.get_circuit_info(circuit_name)
        description = info.get('description', 'No description') if info else 'Unknown'
        
        print(f"\n🔧 {circuit_name}: {status}")
        print(f"   Description: {description}")
        if info:
            print(f"   Public Inputs: {info.get('public_inputs', 0)}")
            print(f"   Private Inputs: {info.get('private_inputs', 0)}")
    
    return True


def main():
    """Main test function"""
    print("🔐 MediLedger Nexus - zk-SNARK Testing Suite")
    print("=" * 80)
    print(f"⏰ Test started at: {datetime.utcnow().isoformat()}")
    
    # Test circuit setup
    test_circuit_setup()
    
    # Run tests
    tests = [
        ("Health Data Validation", test_health_data_validation),
        ("Consent Validation", test_consent_validation),
        ("Emergency Access", test_emergency_access)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*80}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 Test Results Summary")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All zk-SNARK tests passed!")
        print("🔐 Zero-knowledge proofs are working correctly")
        print("🛡️ Privacy-preserving validation is functional")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Please check the errors above and ensure circuits are properly set up")
    
    print(f"\n⏰ Test completed at: {datetime.utcnow().isoformat()}")


if __name__ == "__main__":
    main()
