#!/usr/bin/env python3
"""
MediLedger Nexus API Demo
Demonstrates the key features of the decentralized health data ecosystem
"""

import asyncio
import os
import httpx
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

class MediLedgerDemo:
    """Comprehensive demo client for MediLedger Nexus API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.user_data = {}
        self.demo_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    async def register_user(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Register a new user"""
        print(f"\n🔐 Registering user: {email}")
        
        user_data = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "hedera_account_id": "0.0.123456"  # Demo account
        }
        
        response = await self.client.post(
            "/api/v1/auth/register",
            json=user_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User registered successfully: {result['id']}")
            return result
        else:
            print(f"❌ Registration failed: {response.text}")
            return {}
    
    async def login(self, email: str, password: str) -> bool:
        """Login and get access token"""
        print(f"\n🔑 Logging in: {email}")
        
        login_data = {
            "username": email,
            "password": password
        }
        
        response = await self.client.post(
            "/api/v1/auth/token",
            data=login_data
        )
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result["access_token"]
            print(f"✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    async def create_health_vault(self, name: str, description: str) -> Dict[str, Any]:
        """Create a health vault"""
        print(f"\n🏥 Creating health vault: {name}")
        
        vault_data = {
            "name": name,
            "description": description,
            "encryption_enabled": True,
            "zk_proofs_enabled": True
        }
        
        response = await self.client.post(
            "/api/v1/vault/create",
            json=vault_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health vault created: {result['id']}")
            return result
        else:
            print(f"❌ Vault creation failed: {response.text}")
            return {}
    
    async def register_ai_agent(self, agent_name: str, agent_type: str) -> Dict[str, Any]:
        """Register an AI agent using HCS-10 standard"""
        print(f"\n🤖 Registering AI agent: {agent_name}")
        
        agent_data = {
            "name": agent_name,
            "agent_type": agent_type,
            "capabilities": ["diagnosis", "federated_learning", "research"],
            "hcs_topic_id": "0.0.789101",
            "profile_metadata": {
                "specialization": "cardiology",
                "model_version": "v1.0.0"
            }
        }
        
        response = await self.client.post(
            "/api/v1/ai/register-agent",
            json=agent_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI agent registered: {result['agent_id']}")
            return result
        else:
            print(f"❌ AI agent registration failed: {response.text}")
            return {}
    
    async def grant_consent(self, provider_account: str, record_types: list, duration_hours: int) -> Dict[str, Any]:
        """Grant consent for data access"""
        print(f"\n📋 Granting consent to provider: {provider_account}")
        
        consent_data = {
            "provider_account_id": provider_account,
            "record_types": record_types,
            "duration_hours": duration_hours,
            "compensation_rate": 5.0,  # $HEAL tokens per access
            "purpose": "Medical diagnosis and treatment"
        }
        
        response = await self.client.post(
            "/api/v1/consent/grant",
            json=consent_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Consent granted: {result['id']}")
            return result
        else:
            print(f"❌ Consent grant failed: {response.text}")
            return {}
    
    async def request_ai_diagnosis(self, symptoms: list, medical_history: dict) -> Dict[str, Any]:
        """Request AI diagnosis"""
        print(f"\n🔬 Requesting AI diagnosis for symptoms: {', '.join(symptoms)}")
        
        diagnosis_data = {
            "symptoms": symptoms,
            "medical_history": medical_history,
            "use_federated_learning": True,
            "privacy_level": "high"
        }
        
        response = await self.client.post(
            "/api/v1/ai/diagnose",
            json=diagnosis_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI diagnosis completed: {result['diagnosis_id']}")
            print(f"   Primary diagnosis: {result.get('primary_diagnosis', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 0)}%")
            return result
        else:
            print(f"❌ AI diagnosis failed: {response.text}")
            return {}
    
    async def join_federated_learning(self, study_type: str) -> Dict[str, Any]:
        """Join federated learning round"""
        print(f"\n🧠 Joining federated learning for: {study_type}")
        
        fl_data = {
            "study_type": study_type,
            "data_contribution": "anonymized_records",
            "min_participants": 3,
            "max_rounds": 10
        }
        
        response = await self.client.post(
            "/api/v1/ai/federated-learning/join",
            json=fl_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Joined federated learning round: {result['round_id']}")
            return result
        else:
            print(f"❌ Federated learning join failed: {response.text}")
            return {}
    
    async def emergency_access_demo(self, patient_identifier: str) -> Dict[str, Any]:
        """Demonstrate emergency access protocol"""
        print(f"\n🚨 Emergency access for patient: {patient_identifier}")
        
        emergency_data = {
            "patient_identifier": patient_identifier,
            "emergency_type": "cardiac_arrest",
            "requester_credentials": "EMT_LICENSE_12345",
            "location": "General Hospital ER",
            "urgency_level": "critical"
        }
        
        response = await self.client.post(
            "/api/v1/emergency/access",
            json=emergency_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Emergency access granted")
            print(f"   Blood type: {result.get('blood_type', 'N/A')}")
            print(f"   Allergies: {', '.join(result.get('allergies', []))}")
            print(f"   Emergency contact: {result.get('emergency_contact', 'N/A')}")
            return result
        else:
            print(f"❌ Emergency access failed: {response.text}")
            return {}
    
    async def research_participation_demo(self, study_name: str) -> Dict[str, Any]:
        """Demonstrate research participation"""
        print(f"\n🔬 Participating in research study: {study_name}")
        
        participation_data = {
            "study_name": study_name,
            "data_types": ["lab_results", "imaging", "genomics"],
            "anonymization_level": "full",
            "compensation_expected": True
        }
        
        response = await self.client.post(
            "/api/v1/research/participate",
            json=participation_data,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Research participation confirmed: {result['participation_id']}")
            return result
        else:
            print(f"❌ Research participation failed: {response.text}")
            return {}
    
    async def run_complete_demo(self):
        """Run complete MediLedger Nexus demo"""
        print("🌟 MediLedger Nexus API Demo Starting...")
        print("=" * 60)
        
        # Demo credentials must be supplied by the local development environment.
        email = os.getenv("DEMO_EMAIL", "demo@mediledgernexus.com")
        password = os.getenv("DEMO_PASSWORD")
        if not password:
            raise ValueError(
                "DEMO_PASSWORD is required to run the demo; set it only in a local environment"
            )
        full_name = "Demo Patient"
        
        try:
            # 1. Register user
            user = await self.register_user(email, password, full_name)
            if not user:
                return
            
            # 2. Login
            login_success = await self.login(email, password)
            if not login_success:
                return
            
            # 3. Create health vault
            vault = await self.create_health_vault(
                "Primary Health Vault",
                "Main vault for medical records and health data"
            )
            
            # 4. Register AI agent
            ai_agent = await self.register_ai_agent(
                "CardioAI Assistant",
                "diagnostic_agent"
            )
            
            # 5. Grant consent
            consent = await self.grant_consent(
                "0.0.654321",  # Provider account
                ["lab_results", "imaging", "prescriptions"],
                24  # 24 hours
            )
            
            # 6. Request AI diagnosis
            diagnosis = await self.request_ai_diagnosis(
                ["chest_pain", "shortness_of_breath", "fatigue"],
                {
                    "age": 45,
                    "gender": "male",
                    "previous_conditions": ["hypertension"],
                    "medications": ["lisinopril"]
                }
            )
            
            # 7. Join federated learning
            fl_round = await self.join_federated_learning("cardiovascular_disease")
            
            # 8. Emergency access demo
            emergency_access = await self.emergency_access_demo("patient_id_12345")
            
            # 9. Research participation
            research = await self.research_participation_demo("COVID-19 Long Term Effects Study")
            
            print("\n" + "=" * 60)
            print("🎉 MediLedger Nexus Demo Completed Successfully!")
            print("\nKey Features Demonstrated:")
            print("✅ User registration and authentication")
            print("✅ Health vault creation with encryption")
            print("✅ AI agent registration (HCS-10 standard)")
            print("✅ Tokenized consent management")
            print("✅ AI-powered diagnosis with federated learning")
            print("✅ Emergency response protocol")
            print("✅ Research data monetization")
            print("\n🔗 Blockchain Integration:")
            print("• Hedera Consensus Service (HCS) for data flow")
            print("• Hedera Token Service (HTS) for $HEAL tokens")
            print("• Smart contracts for consent management")
            print("• IPFS for decentralized storage")
            print("• zk-SNARKs for privacy-preserving proofs")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")


async def main():
    """Main demo function"""
    async with MediLedgerNexusDemo() as demo:
        await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())
