#!/usr/bin/env python3
"""
MediLedger Nexus - zk-SNARK Setup and Management Script

This script sets up and manages zk-SNARK circuits for the MediLedger Nexus platform.
It handles circuit compilation, key generation, and proof verification.
"""

import os
import json
import subprocess
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ZKSNARKManager:
    """Manager for zk-SNARK circuits and proofs"""
    
    def __init__(self, circuits_dir: str = "circuits", zk_dir: str = "zk"):
        self.circuits_dir = Path(circuits_dir)
        self.zk_dir = Path(zk_dir)
        self.zk_dir.mkdir(exist_ok=True)
        
        # Circuit configurations
        self.circuits = {
            "health_data_validator": {
                "file": "health_data_validator.zok",
                "description": "Validates health data without revealing actual values",
                "public_inputs": 15,
                "private_inputs": 8
            },
            "consent_proof": {
                "file": "consent_proof.zok",
                "description": "Proves valid consent without revealing consent details",
                "public_inputs": 7,
                "private_inputs": 7
            },
            "emergency_access": {
                "file": "emergency_access.zok",
                "description": "Proves legitimate emergency access",
                "public_inputs": 7,
                "private_inputs": 7
            },
            "research_data_anonymizer": {
                "file": "research_data_anonymizer.zok",
                "description": "Proves data anonymization for research",
                "public_inputs": 7,
                "private_inputs": 8
            }
        }
    
    def check_zokrates_installation(self) -> bool:
        """Check if ZoKrates is properly installed"""
        try:
            result = subprocess.run(['zokrates', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ ZoKrates version: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ ZoKrates not found: {result.stderr}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ ZoKrates not installed or not in PATH")
            return False
    
    def compile_circuit(self, circuit_name: str) -> bool:
        """Compile a ZoKrates circuit"""
        if circuit_name not in self.circuits:
            print(f"❌ Unknown circuit: {circuit_name}")
            return False
        
        circuit_file = self.circuits_dir / self.circuits[circuit_name]["file"]
        if not circuit_file.exists():
            print(f"❌ Circuit file not found: {circuit_file}")
            return False
        
        try:
            print(f"🔨 Compiling circuit: {circuit_name}")
            
            # Compile the circuit
            cmd = ['zokrates', 'compile', '-i', str(circuit_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ Circuit compiled successfully: {circuit_name}")
                return True
            else:
                print(f"❌ Compilation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Compilation timeout for circuit: {circuit_name}")
            return False
        except Exception as e:
            print(f"❌ Error compiling circuit {circuit_name}: {e}")
            return False
    
    def setup_circuit(self, circuit_name: str) -> bool:
        """Setup a circuit (compile and generate keys)"""
        if circuit_name not in self.circuits:
            print(f"❌ Unknown circuit: {circuit_name}")
            return False
        
        try:
            print(f"🚀 Setting up circuit: {circuit_name}")
            
            # Compile circuit
            if not self.compile_circuit(circuit_name):
                return False
            
            # Setup (generate proving and verification keys)
            cmd = ['zokrates', 'setup']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ Circuit setup completed: {circuit_name}")
                
                # Move generated files to zk directory
                self._organize_generated_files(circuit_name)
                return True
            else:
                print(f"❌ Setup failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Setup timeout for circuit: {circuit_name}")
            return False
        except Exception as e:
            print(f"❌ Error setting up circuit {circuit_name}: {e}")
            return False
    
    def _organize_generated_files(self, circuit_name: str):
        """Organize generated zk-SNARK files"""
        circuit_zk_dir = self.zk_dir / circuit_name
        circuit_zk_dir.mkdir(exist_ok=True)
        
        # Files generated by ZoKrates
        generated_files = [
            "out",
            "proving.key",
            "verification.key",
            "abi.json"
        ]
        
        for file_name in generated_files:
            if os.path.exists(file_name):
                dest_path = circuit_zk_dir / file_name
                if os.path.isfile(file_name):
                    os.rename(file_name, dest_path)
                elif os.path.isdir(file_name):
                    if dest_path.exists():
                        import shutil
                        shutil.rmtree(dest_path)
                    os.rename(file_name, dest_path)
                print(f"📁 Moved {file_name} to {dest_path}")
    
    def generate_proof(self, circuit_name: str, inputs: List[str]) -> Optional[Dict[str, Any]]:
        """Generate a zk-SNARK proof"""
        if circuit_name not in self.circuits:
            print(f"❌ Unknown circuit: {circuit_name}")
            return None
        
        circuit_zk_dir = self.zk_dir / circuit_name
        if not circuit_zk_dir.exists():
            print(f"❌ Circuit not set up: {circuit_name}")
            return None
        
        try:
            print(f"🔐 Generating proof for circuit: {circuit_name}")
            
            # Change to circuit directory
            original_dir = os.getcwd()
            os.chdir(circuit_zk_dir)
            
            # Generate witness
            witness_cmd = ['zokrates', 'compute-witness', '-a'] + inputs
            witness_result = subprocess.run(witness_cmd, capture_output=True, text=True, timeout=60)
            
            if witness_result.returncode != 0:
                print(f"❌ Witness generation failed: {witness_result.stderr}")
                os.chdir(original_dir)
                return None
            
            # Generate proof
            proof_cmd = ['zokrates', 'generate-proof']
            proof_result = subprocess.run(proof_cmd, capture_output=True, text=True, timeout=120)
            
            os.chdir(original_dir)
            
            if proof_result.returncode == 0:
                print(f"✅ Proof generated successfully for: {circuit_name}")
                
                # Parse proof data
                proof_data = self._parse_proof_output(proof_result.stdout)
                return proof_data
            else:
                print(f"❌ Proof generation failed: {proof_result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"❌ Proof generation timeout for circuit: {circuit_name}")
            os.chdir(original_dir)
            return None
        except Exception as e:
            print(f"❌ Error generating proof for {circuit_name}: {e}")
            os.chdir(original_dir)
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
        if circuit_name not in self.circuits:
            print(f"❌ Unknown circuit: {circuit_name}")
            return False
        
        circuit_zk_dir = self.zk_dir / circuit_name
        if not circuit_zk_dir.exists():
            print(f"❌ Circuit not set up: {circuit_name}")
            return False
        
        try:
            print(f"🔍 Verifying proof for circuit: {circuit_name}")
            
            # Change to circuit directory
            original_dir = os.getcwd()
            os.chdir(circuit_zk_dir)
            
            # Verify proof
            verify_cmd = ['zokrates', 'verify']
            verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=60)
            
            os.chdir(original_dir)
            
            if verify_result.returncode == 0:
                print(f"✅ Proof verified successfully for: {circuit_name}")
                return True
            else:
                print(f"❌ Proof verification failed: {verify_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Verification timeout for circuit: {circuit_name}")
            os.chdir(original_dir)
            return False
        except Exception as e:
            print(f"❌ Error verifying proof for {circuit_name}: {e}")
            os.chdir(original_dir)
            return False
    
    def setup_all_circuits(self) -> Dict[str, bool]:
        """Setup all circuits"""
        results = {}
        
        print("🚀 Setting up all zk-SNARK circuits...")
        print("=" * 50)
        
        for circuit_name in self.circuits.keys():
            print(f"\n📋 Setting up: {circuit_name}")
            print(f"   Description: {self.circuits[circuit_name]['description']}")
            results[circuit_name] = self.setup_circuit(circuit_name)
        
        return results
    
    def create_test_data(self, circuit_name: str) -> Dict[str, Any]:
        """Create test data for a circuit"""
        if circuit_name not in self.circuits:
            return {}
        
        # Generate test data based on circuit type
        if circuit_name == "health_data_validator":
            return {
                "private_inputs": [
                    "1234567890", "1234567890", "1234567890", "1234567890",  # data_hash
                    "1234567890", "1234567890", "1234567890", "1234567890",  # patient_id_hash
                    "30",  # age
                    "120",  # systolic
                    "80",   # diastolic
                    "72",   # heart_rate
                    "365",  # temperature (36.5°C)
                    "1234567890", "1234567890", "1234567890", "1234567890"  # timestamp_hash
                ],
                "public_inputs": [
                    "18",   # min_age
                    "100",  # max_age
                    "180",  # max_systolic
                    "120",  # max_diastolic
                    "200",  # max_heart_rate
                    "400",  # max_temperature
                    "1234567890", "1234567890", "1234567890", "1234567890",  # expected_patient_hash
                    "1234567890", "1234567890", "1234567890", "1234567890"   # expected_timestamp_hash
                ]
            }
        
        # Add more test data for other circuits...
        return {}
    
    def generate_circuit_documentation(self) -> str:
        """Generate documentation for all circuits"""
        doc = "# MediLedger Nexus - zk-SNARK Circuits Documentation\n\n"
        doc += f"Generated on: {datetime.utcnow().isoformat()}\n\n"
        
        for circuit_name, config in self.circuits.items():
            doc += f"## {circuit_name}\n\n"
            doc += f"**Description:** {config['description']}\n\n"
            doc += f"**File:** `{config['file']}`\n\n"
            doc += f"**Public Inputs:** {config['public_inputs']}\n\n"
            doc += f"**Private Inputs:** {config['private_inputs']}\n\n"
            doc += "### Usage\n\n"
            doc += "```python\n"
            doc += f"# Setup circuit\n"
            doc += f"manager.setup_circuit('{circuit_name}')\n\n"
            doc += f"# Generate proof\n"
            doc += f"proof = manager.generate_proof('{circuit_name}', inputs)\n\n"
            doc += f"# Verify proof\n"
            doc += f"is_valid = manager.verify_proof('{circuit_name}', proof)\n"
            doc += "```\n\n"
        
        return doc


def main():
    """Main function"""
    print("🔐 MediLedger Nexus - zk-SNARK Setup")
    print("=" * 50)
    
    # Initialize manager
    manager = ZKSNARKManager()
    
    # Check ZoKrates installation
    if not manager.check_zokrates_installation():
        print("\n❌ Please install ZoKrates first:")
        print("   curl -LSfs https://raw.githubusercontent.com/Zokrates/zokrates/master/scripts/install.sh | sh")
        return
    
    # Setup all circuits
    results = manager.setup_all_circuits()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Setup Results")
    print("=" * 50)
    
    for circuit_name, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"{circuit_name}: {status}")
    
    successful = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 Overall: {successful}/{total} circuits set up successfully")
    
    if successful == total:
        print("\n🎉 All zk-SNARK circuits are ready!")
        print("\n📁 Generated files are in the 'zk/' directory")
        print("🔑 Proving and verification keys are ready for use")
        print("🔐 You can now generate and verify proofs")
    else:
        print(f"\n⚠️  {total - successful} circuit(s) failed setup")
        print("Please check the errors above and try again")
    
    # Generate documentation
    doc = manager.generate_circuit_documentation()
    with open("zk_circuits_documentation.md", "w") as f:
        f.write(doc)
    print(f"\n📚 Documentation saved to: zk_circuits_documentation.md")


if __name__ == "__main__":
    main()
