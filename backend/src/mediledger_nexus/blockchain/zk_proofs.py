"""
Zero-Knowledge Proof Integration for MediLedger Nexus

This module provides zk-SNARK proof generation and verification
for health data validation, consent management, and privacy-preserving operations.
"""

import os
import json
import hashlib
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ZKProofManager:
    """
    Manager for zk-SNARK proofs in MediLedger Nexus
    
    Handles proof generation, verification, and integration with smart contracts.
    """
    
    def __init__(self, zk_dir: str = "zk", circuits_dir: str = "circuits"):
        """Initialize ZK proof manager"""
        self.zk_dir = Path(zk_dir)
        self.circuits_dir = Path(circuits_dir)
        
        # Circuit configurations
        self.circuits = {
            "health_data_validator": {
                "description": "Validates health data without revealing actual values",
                "public_inputs": 15,
                "private_inputs": 8
            },
            "consent_proof": {
                "description": "Proves valid consent without revealing consent details",
                "public_inputs": 7,
                "private_inputs": 7
            },
            "emergency_access": {
                "description": "Proves legitimate emergency access",
                "public_inputs": 7,
                "private_inputs": 7
            },
            "research_data_anonymizer": {
                "description": "Proves data anonymization for research",
                "public_inputs": 7,
                "private_inputs": 8
            }
        }
    
    def hash_data(self, data: str) -> str:
        """Generate SHA-256 hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def hash_to_u32_array(self, hash_str: str) -> List[str]:
        """Convert hash string to array of u32 values for ZoKrates"""
        # Take first 32 characters (256 bits) and split into 8 u32 values
        hash_bytes = bytes.fromhex(hash_str[:64])  # 32 bytes = 256 bits
        u32_array = []
        
        for i in range(0, 32, 4):  # 8 iterations, 4 bytes each
            u32_value = int.from_bytes(hash_bytes[i:i+4], byteorder='big')
            u32_array.append(str(u32_value))
        
        return u32_array
    
    def generate_health_data_proof(self, 
                                 health_data: Dict[str, Any],
                                 patient_id: str,
                                 timestamp: str,
                                 constraints: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate zk-SNARK proof for health data validation
        
        Args:
            health_data: Dictionary containing health measurements
            patient_id: Patient identifier
            timestamp: Data timestamp
            constraints: Validation constraints
            
        Returns:
            Dictionary containing proof data or None if failed
        """
        try:
            # Prepare private inputs
            data_hash = self.hash_data(json.dumps(health_data, sort_keys=True))
            patient_hash = self.hash_data(patient_id)
            timestamp_hash = self.hash_data(timestamp)
            
            private_inputs = (
                self.hash_to_u32_array(data_hash) +
                self.hash_to_u32_array(patient_hash) +
                [str(health_data.get('age', 0))] +
                [str(health_data.get('blood_pressure_systolic', 0))] +
                [str(health_data.get('blood_pressure_diastolic', 0))] +
                [str(health_data.get('heart_rate', 0))] +
                [str(int(health_data.get('temperature', 0) * 10))] +  # Convert to tenths
                self.hash_to_u32_array(timestamp_hash)
            )
            
            # Prepare public inputs
            public_inputs = [
                str(constraints.get('min_age', 0)),
                str(constraints.get('max_age', 150)),
                str(constraints.get('max_systolic', 200)),
                str(constraints.get('max_diastolic', 120)),
                str(constraints.get('max_heart_rate', 200)),
                str(constraints.get('max_temperature', 400)),  # 40.0°C in tenths
            ] + self.hash_to_u32_array(patient_hash) + self.hash_to_u32_array(timestamp_hash)
            
            # Generate proof
            proof_data = self._generate_proof("health_data_validator", private_inputs, public_inputs)
            
            if proof_data:
                proof_data.update({
                    "circuit_type": "health_data_validator",
                    "patient_id_hash": patient_hash,
                    "data_hash": data_hash,
                    "timestamp_hash": timestamp_hash,
                    "constraints": constraints,
                    "generated_at": datetime.utcnow().isoformat()
                })
            
            return proof_data
            
        except Exception as e:
            logger.error(f"Error generating health data proof: {e}")
            return None
    
    def generate_consent_proof(self,
                             consent_data: Dict[str, Any],
                             patient_id: str,
                             provider_id: str,
                             current_timestamp: int) -> Optional[Dict[str, Any]]:
        """
        Generate zk-SNARK proof for consent validation
        
        Args:
            consent_data: Dictionary containing consent information
            patient_id: Patient identifier
            provider_id: Provider identifier
            current_timestamp: Current timestamp for validation
            
        Returns:
            Dictionary containing proof data or None if failed
        """
        try:
            # Prepare private inputs
            consent_hash = self.hash_data(json.dumps(consent_data, sort_keys=True))
            patient_hash = self.hash_data(patient_id)
            provider_hash = self.hash_data(provider_id)
            signature_hash = self.hash_data(consent_data.get('signature', ''))
            
            private_inputs = (
                self.hash_to_u32_array(consent_hash) +
                self.hash_to_u32_array(patient_hash) +
                self.hash_to_u32_array(provider_hash) +
                [str(consent_data.get('consent_timestamp', 0))] +
                [str(consent_data.get('expiration_timestamp', 0))] +
                [str(consent_data.get('data_types_consented', 0))] +
                self.hash_to_u32_array(signature_hash)
            )
            
            # Prepare public inputs
            public_inputs = [
                str(current_timestamp),
            ] + self.hash_to_u32_array(patient_hash) + self.hash_to_u32_array(provider_hash) + [
                str(consent_data.get('min_consent_duration', 3600)),  # 1 hour
                str(consent_data.get('max_consent_duration', 86400 * 365)),  # 1 year
                str(consent_data.get('required_data_types', 0)),
            ] + self.hash_to_u32_array(consent_hash)
            
            # Generate proof
            proof_data = self._generate_proof("consent_proof", private_inputs, public_inputs)
            
            if proof_data:
                proof_data.update({
                    "circuit_type": "consent_proof",
                    "patient_id_hash": patient_hash,
                    "provider_id_hash": provider_hash,
                    "consent_hash": consent_hash,
                    "generated_at": datetime.utcnow().isoformat()
                })
            
            return proof_data
            
        except Exception as e:
            logger.error(f"Error generating consent proof: {e}")
            return None
    
    def generate_emergency_access_proof(self,
                                      emergency_data: Dict[str, Any],
                                      patient_id: str,
                                      provider_id: str,
                                      current_timestamp: int) -> Optional[Dict[str, Any]]:
        """
        Generate zk-SNARK proof for emergency access validation
        
        Args:
            emergency_data: Dictionary containing emergency information
            patient_id: Patient identifier
            provider_id: Emergency provider identifier
            current_timestamp: Current timestamp for validation
            
        Returns:
            Dictionary containing proof data or None if failed
        """
        try:
            # Prepare private inputs
            patient_hash = self.hash_data(patient_id)
            provider_hash = self.hash_data(provider_id)
            location_hash = self.hash_data(emergency_data.get('location', ''))
            credentials_hash = self.hash_data(emergency_data.get('provider_credentials', ''))
            
            private_inputs = (
                self.hash_to_u32_array(patient_hash) +
                self.hash_to_u32_array(provider_hash) +
                [str(emergency_data.get('emergency_timestamp', 0))] +
                [str(emergency_data.get('emergency_type', 1))] +
                [str(emergency_data.get('urgency_level', 1))] +
                self.hash_to_u32_array(location_hash) +
                self.hash_to_u32_array(credentials_hash)
            )
            
            # Prepare public inputs
            public_inputs = [
                str(current_timestamp),
            ] + self.hash_to_u32_array(patient_hash) + self.hash_to_u32_array(provider_hash) + [
                str(emergency_data.get('max_access_duration', 3600)),  # 1 hour
                str(emergency_data.get('min_urgency_level', 3)),  # Level 3+ for access
            ] + self.hash_to_u32_array(location_hash) + self.hash_to_u32_array(credentials_hash)
            
            # Generate proof
            proof_data = self._generate_proof("emergency_access", private_inputs, public_inputs)
            
            if proof_data:
                proof_data.update({
                    "circuit_type": "emergency_access",
                    "patient_id_hash": patient_hash,
                    "provider_id_hash": provider_hash,
                    "emergency_type": emergency_data.get('emergency_type'),
                    "urgency_level": emergency_data.get('urgency_level'),
                    "generated_at": datetime.utcnow().isoformat()
                })
            
            return proof_data
            
        except Exception as e:
            logger.error(f"Error generating emergency access proof: {e}")
            return None
    
    def _generate_proof(self, 
                       circuit_name: str, 
                       private_inputs: List[str], 
                       public_inputs: List[str]) -> Optional[Dict[str, Any]]:
        """Generate zk-SNARK proof using ZoKrates"""
        try:
            circuit_zk_dir = self.zk_dir / circuit_name
            
            if not circuit_zk_dir.exists():
                logger.error(f"Circuit not set up: {circuit_name}")
                return None
            
            # Change to circuit directory
            original_dir = os.getcwd()
            os.chdir(circuit_zk_dir)
            
            try:
                # Generate witness
                witness_cmd = ['zokrates', 'compute-witness', '-a'] + private_inputs + public_inputs
                witness_result = subprocess.run(witness_cmd, capture_output=True, text=True, timeout=60)
                
                if witness_result.returncode != 0:
                    logger.error(f"Witness generation failed: {witness_result.stderr}")
                    return None
                
                # Generate proof
                proof_cmd = ['zokrates', 'generate-proof']
                proof_result = subprocess.run(proof_cmd, capture_output=True, text=True, timeout=120)
                
                if proof_result.returncode == 0:
                    # Parse proof data
                    proof_data = self._parse_proof_output(proof_result.stdout)
                    return proof_data
                else:
                    logger.error(f"Proof generation failed: {proof_result.stderr}")
                    return None
                    
            finally:
                os.chdir(original_dir)
                
        except subprocess.TimeoutExpired:
            logger.error(f"Proof generation timeout for circuit: {circuit_name}")
            return None
        except Exception as e:
            logger.error(f"Error generating proof for {circuit_name}: {e}")
            return None
    
    def _parse_proof_output(self, output: str) -> Dict[str, Any]:
        """Parse ZoKrates proof output"""
        # This is a simplified parser - in practice, you'd need more robust parsing
        proof_data = {
            "proof": {
                "a": ["0", "0"],
                "b": [["0", "0"], ["0", "0"]],
                "c": ["0", "0"]
            },
            "inputs": [],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Extract proof components from output
        lines = output.split('\n')
        for line in lines:
            if 'proof' in line.lower():
                # Parse proof data (simplified)
                pass
        
        return proof_data
    
    def verify_proof(self, circuit_name: str, proof_data: Dict[str, Any]) -> bool:
        """Verify a zk-SNARK proof"""
        try:
            circuit_zk_dir = self.zk_dir / circuit_name
            
            if not circuit_zk_dir.exists():
                logger.error(f"Circuit not set up: {circuit_name}")
                return False
            
            # Change to circuit directory
            original_dir = os.getcwd()
            os.chdir(circuit_zk_dir)
            
            try:
                # Verify proof
                verify_cmd = ['zokrates', 'verify']
                verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=60)
                
                if verify_result.returncode == 0:
                    logger.info(f"Proof verified successfully for circuit: {circuit_name}")
                    return True
                else:
                    logger.error(f"Proof verification failed: {verify_result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_dir)
                
        except subprocess.TimeoutExpired:
            logger.error(f"Verification timeout for circuit: {circuit_name}")
            return False
        except Exception as e:
            logger.error(f"Error verifying proof for {circuit_name}: {e}")
            return False
    
    def get_circuit_info(self, circuit_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a circuit"""
        if circuit_name in self.circuits:
            return self.circuits[circuit_name]
        return None
    
    def list_circuits(self) -> List[str]:
        """List available circuits"""
        return list(self.circuits.keys())
    
    def is_circuit_setup(self, circuit_name: str) -> bool:
        """Check if a circuit is properly set up"""
        if circuit_name not in self.circuits:
            return False
        
        circuit_zk_dir = self.zk_dir / circuit_name
        required_files = ["proving.key", "verification.key", "abi.json"]
        
        return all((circuit_zk_dir / file).exists() for file in required_files)


# Global instance
zk_proof_manager = ZKProofManager()