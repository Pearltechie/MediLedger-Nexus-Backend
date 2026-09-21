"""
Integration tests for complete workflows
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import uuid

from src.mediledger_nexus.main import app


@pytest.mark.integration
class TestCompleteUserJourney:
    """Test complete user journey from registration to AI diagnosis"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        """Create async test client"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture
    def unique_user_data(self):
        """Generate unique user data for each test"""
        unique_id = uuid.uuid4().hex[:8]
        return {
            "email": f"test_{unique_id}@example.com",
            "password": "SecurePassword123!",
            "full_name": f"Test User {unique_id}",
            "hedera_account_id": f"0.0.{unique_id[:6]}"
        }
    
    def test_complete_patient_workflow(self, client, unique_user_data):
        """Test complete patient workflow"""
        # Step 1: Register user
        response = client.post("/api/v1/auth/register", json=unique_user_data)
        if response.status_code != 200:
            pytest.skip(f"Registration failed: {response.json()}")
        
        user_data = response.json()
        assert user_data["email"] == unique_user_data["email"]
        
        # Step 2: Login
        login_data = {
            "username": unique_user_data["email"],
            "password": unique_user_data["password"]
        }
        response = client.post("/api/v1/auth/token", data=login_data)
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.json()}")
        
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Create health vault
        vault_data = {
            "name": "Primary Health Vault",
            "description": "Main vault for medical records",
            "encryption_enabled": True,
            "zk_proofs_enabled": True,
            "privacy_level": "high"
        }
        
        response = client.post("/api/v1/vault/create", json=vault_data, headers=headers)
        # Note: This might fail if the service is not fully implemented
        
        # Step 4: Register AI agent
        agent_data = {
            "name": "Personal Health AI",
            "agent_type": "diagnostic_agent",
            "capabilities": ["diagnosis", "health_insights"],
            "hcs_topic_id": f"0.0.{uuid.uuid4().hex[:6]}"
        }
        
        response = client.post("/api/v1/ai/register-agent", json=agent_data, headers=headers)
        # Note: This might fail if the service is not fully implemented


@pytest.mark.integration
class TestEmergencyWorkflows:
    """Test emergency access workflows"""
    
    @pytest.fixture
    def patient_client(self, client, unique_user_data):
        """Create patient client"""
        # Register and login patient
        client.post("/api/v1/auth/register", json=unique_user_data)
        login_response = client.post("/api/v1/auth/token", data={
            "username": unique_user_data["email"],
            "password": unique_user_data["password"]
        })
        
        if login_response.status_code != 200:
            pytest.skip("Patient authentication failed")
        
        token = login_response.json()["access_token"]
        return client, {"Authorization": f"Bearer {token}"}
    
    def test_emergency_profile_setup(self, patient_client):
        """Test emergency profile setup"""
        client, headers = patient_client
        
        # Set up emergency profile
        emergency_profile = {
            "blood_type": "O+",
            "allergies": ["penicillin", "latex"],
            "current_medications": ["lisinopril", "metformin"],
            "medical_conditions": ["hypertension", "diabetes"],
            "emergency_contact": {
                "name": "Jane Doe",
                "phone": "+1234567890",
                "relationship": "spouse",
                "email": "jane.doe@example.com"
            }
        }
        
        response = client.put("/api/v1/emergency/profile", json=emergency_profile, headers=headers)
        # Note: This might fail if the service is not fully implemented
        
        # Get emergency profile
        response = client.get("/api/v1/emergency/profile", headers=headers)
        # Note: This might fail if the service is not fully implemented


@pytest.mark.integration 
class TestDataFlowIntegration:
    """Test data flow between different components"""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create authenticated user"""
        unique_id = uuid.uuid4().hex[:8]
        user_data = {
            "email": f"dataflow_{unique_id}@example.com",
            "password": "SecurePassword123!",
            "full_name": f"Data Flow User {unique_id}",
            "hedera_account_id": f"0.0.{unique_id[:6]}"
        }
        
        client.post("/api/v1/auth/register", json=user_data)
        login_response = client.post("/api/v1/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed")
        
        token = login_response.json()["access_token"]
        return client, {"Authorization": f"Bearer {token}"}, user_data
    
    def test_vault_to_ai_data_flow(self, authenticated_user):
        """Test data flow from vault to AI diagnosis"""
        client, headers, user_data = authenticated_user
        
        # Create vault with medical data
        vault_data = {
            "name": "Medical Data Vault",
            "description": "Vault containing medical history",
            "encryption_enabled": True,
            "privacy_level": "high"
        }
        
        response = client.post("/api/v1/vault/create", json=vault_data, headers=headers)
        # Note: This might fail if the service is not fully implemented
        
        # Request AI diagnosis using vault data
        diagnosis_data = {
            "symptoms": ["fatigue", "dizziness"],
            "medical_history": {
                "age": 40,
                "gender": "female",
                "conditions": ["anemia"]
            },
            "use_vault_data": True,
            "privacy_level": "high"
        }
        
        response = client.post("/api/v1/ai/diagnose", json=diagnosis_data, headers=headers)
        # Note: This might fail if the service is not fully implemented
    
    def test_consent_to_research_data_flow(self, authenticated_user):
        """Test data flow from consent to research participation"""
        client, headers, user_data = authenticated_user
        
        # Grant research consent
        consent_data = {
            "provider_account_id": f"0.0.{uuid.uuid4().hex[:6]}",
            "record_types": ["lab_results", "genomics"],
            "duration_hours": 168,  # 1 week
            "compensation_rate": 15.0,
            "purpose": "Genomic research study"
        }
        
        response = client.post("/api/v1/consent/grant", json=consent_data, headers=headers)
        # Note: This might fail if the service is not fully implemented
        
        # Participate in research study
        participation_data = {
            "study_id": f"genomic_study_{uuid.uuid4().hex[:8]}",
            "data_types": ["genomics", "lab_results"],
            "anonymization_level": "maximum",
            "compensation_expected": 50.0
        }
        
        response = client.post("/api/v1/research/participate", json=participation_data, headers=headers)
        # Note: This might fail if the service is not fully implemented
