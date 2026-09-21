"""
Integration tests for MediLedger Nexus API
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_user_registration_flow(self, client: TestClient, test_user_data):
        """Test complete user registration flow"""
        # Register user
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == test_user_data["email"]
        
        # Login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        
        # Get current user
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        current_user = response.json()
        assert current_user["email"] == test_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_health_vault_workflow(self, async_client: AsyncClient, test_user_data, test_health_vault_data):
        """Test health vault creation workflow"""
        # Register and login user
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await async_client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create health vault
        response = await async_client.post(
            "/api/v1/vault/create",
            json=test_health_vault_data,
            headers=headers
        )
        
        assert response.status_code == 200
        vault_data = response.json()
        assert vault_data["name"] == test_health_vault_data["name"]
        
        # Get user vaults
        response = await async_client.get("/api/v1/vault/", headers=headers)
        assert response.status_code == 200
        
        vaults = response.json()
        assert len(vaults) == 1
        assert vaults[0]["name"] == test_health_vault_data["name"]
    
    @pytest.mark.asyncio
    async def test_ai_agent_registration(self, async_client: AsyncClient, test_user_data, test_ai_agent_data):
        """Test AI agent registration workflow"""
        # Register and login user
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await async_client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Register AI agent
        response = await async_client.post(
            "/api/v1/ai/register-agent",
            json=test_ai_agent_data,
            headers=headers
        )
        
        assert response.status_code == 200
        agent_data = response.json()
        assert agent_data["name"] == test_ai_agent_data["name"]
        assert "agent_id" in agent_data
        
        # Get user agents
        response = await async_client.get("/api/v1/ai/agents", headers=headers)
        assert response.status_code == 200
        
        agents = response.json()
        assert len(agents) == 1
        assert agents[0]["name"] == test_ai_agent_data["name"]
    
    @pytest.mark.asyncio
    async def test_consent_management(self, async_client: AsyncClient, test_user_data, test_consent_data):
        """Test consent management workflow"""
        # Register and login user
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await async_client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Grant consent
        response = await async_client.post(
            "/api/v1/consent/grant",
            json=test_consent_data,
            headers=headers
        )
        
        assert response.status_code == 200
        consent_data = response.json()
        assert "id" in consent_data
        
        # Get user consents
        response = await async_client.get("/api/v1/consent/", headers=headers)
        assert response.status_code == 200
        
        consents = response.json()
        assert len(consents) == 1
        assert consents[0]["provider_account_id"] == test_consent_data["provider_account_id"]
    
    @pytest.mark.asyncio
    async def test_ai_diagnosis_request(self, async_client: AsyncClient, test_user_data):
        """Test AI diagnosis request"""
        # Register and login user
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await async_client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Request AI diagnosis
        diagnosis_data = {
            "symptoms": ["headache", "fever", "fatigue"],
            "medical_history": {
                "age": 30,
                "gender": "female",
                "conditions": ["hypertension"]
            },
            "use_federated_learning": True,
            "privacy_level": "high"
        }
        
        response = await async_client.post(
            "/api/v1/ai/diagnose",
            json=diagnosis_data,
            headers=headers
        )
        
        assert response.status_code == 200
        diagnosis_result = response.json()
        assert "diagnosis_id" in diagnosis_result
        assert "primary_diagnosis" in diagnosis_result
        assert "confidence" in diagnosis_result
    
    @pytest.mark.asyncio
    async def test_federated_learning_join(self, async_client: AsyncClient, test_user_data):
        """Test joining federated learning"""
        # Register and login user
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await async_client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Join federated learning
        fl_data = {
            "study_type": "cardiovascular_disease",
            "data_contribution": "anonymized_records",
            "min_participants": 3,
            "max_rounds": 10
        }
        
        response = await async_client.post(
            "/api/v1/ai/federated-learning/join",
            json=fl_data,
            headers=headers
        )
        
        assert response.status_code == 200
        fl_result = response.json()
        assert "round_id" in fl_result
        assert "participant_id" in fl_result
    
    @pytest.mark.asyncio
    async def test_emergency_access(self, async_client: AsyncClient, test_user_data):
        """Test emergency access protocol"""
        # Register and login user (as healthcare provider)
        provider_data = test_user_data.copy()
        provider_data["email"] = "provider@hospital.com"
        provider_data["user_type"] = "provider"
        
        await async_client.post("/api/v1/auth/register", json=provider_data)
        
        login_data = {
            "username": provider_data["email"],
            "password": provider_data["password"]
        }
        login_response = await async_client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Request emergency access
        emergency_data = {
            "patient_identifier": "patient_id_12345",
            "emergency_type": "cardiac_arrest",
            "requester_credentials": "EMT_LICENSE_12345",
            "location": "General Hospital ER",
            "urgency_level": "critical"
        }
        
        response = await async_client.post(
            "/api/v1/emergency/access",
            json=emergency_data,
            headers=headers
        )
        
        assert response.status_code == 200
        emergency_result = response.json()
        assert "blood_type" in emergency_result or "error" in emergency_result


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndWorkflows:
    """End-to-end workflow tests"""
    
    @pytest.mark.asyncio
    async def test_complete_patient_journey(self, async_client: AsyncClient):
        """Test complete patient journey from registration to AI diagnosis"""
        # Patient registration
        patient_data = {
            "email": "patient@example.com",
            "password": "securepassword123",
            "full_name": "John Patient",
            "hedera_account_id": "0.0.123456"
        }
        
        await async_client.post("/api/v1/auth/register", json=patient_data)
        
        # Patient login
        login_response = await async_client.post(
            "/api/v1/auth/token",
            data={"username": patient_data["email"], "password": patient_data["password"]}
        )
        patient_token = login_response.json()["access_token"]
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        
        # Create health vault
        vault_data = {
            "name": "Primary Health Vault",
            "description": "Main vault for medical records",
            "encryption_enabled": True,
            "zk_proofs_enabled": True
        }
        
        vault_response = await async_client.post(
            "/api/v1/vault/create",
            json=vault_data,
            headers=patient_headers
        )
        vault_id = vault_response.json()["id"]
        
        # Grant consent to provider
        consent_data = {
            "provider_account_id": "0.0.654321",
            "record_types": ["lab_results", "imaging"],
            "duration_hours": 24,
            "compensation_rate": 5.0,
            "purpose": "Medical diagnosis"
        }
        
        await async_client.post(
            "/api/v1/consent/grant",
            json=consent_data,
            headers=patient_headers
        )
        
        # Register AI agent
        agent_data = {
            "name": "Personal Health AI",
            "agent_type": "diagnostic_agent",
            "capabilities": ["diagnosis", "health_insights"],
            "hcs_topic_id": "0.0.789101",
            "profile_metadata": {"specialization": "general_medicine"}
        }
        
        await async_client.post(
            "/api/v1/ai/register-agent",
            json=agent_data,
            headers=patient_headers
        )
        
        # Request AI diagnosis
        diagnosis_data = {
            "symptoms": ["chest_pain", "shortness_of_breath"],
            "medical_history": {
                "age": 45,
                "gender": "male",
                "conditions": ["hypertension"],
                "medications": ["lisinopril"]
            },
            "use_federated_learning": True,
            "privacy_level": "high"
        }
        
        diagnosis_response = await async_client.post(
            "/api/v1/ai/diagnose",
            json=diagnosis_data,
            headers=patient_headers
        )
        
        assert diagnosis_response.status_code == 200
        diagnosis_result = diagnosis_response.json()
        assert "diagnosis_id" in diagnosis_result
        assert "primary_diagnosis" in diagnosis_result
        
        # Get health insights
        insights_response = await async_client.get(
            "/api/v1/ai/insights",
            headers=patient_headers
        )
        
        assert insights_response.status_code == 200
        insights = insights_response.json()
        assert isinstance(insights, list)
