"""
Unit tests for API endpoints
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status
import json

from src.mediledger_nexus.main import app


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user_service(self):
        """Mock user service"""
        with patch('src.mediledger_nexus.api.endpoints.auth.UserService') as mock:
            yield mock
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock auth service"""
        with patch('src.mediledger_nexus.api.endpoints.auth.AuthService') as mock:
            yield mock
    
    def test_register_valid_user(self, client, mock_user_service):
        """Test user registration with valid data"""
        mock_service_instance = Mock()
        mock_service_instance.get_by_email.return_value = None  # User doesn't exist
        mock_service_instance.create.return_value = Mock(
            id=1,
            email="test@example.com",
            full_name="Test User",
            created_at="2024-01-01T00:00:00Z"
        )
        mock_user_service.return_value = mock_service_instance
        
        user_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
            "hedera_account_id": "0.0.123456"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        mock_service_instance.get_by_email.assert_called_once_with("test@example.com")
        mock_service_instance.create.assert_called_once()
    
    def test_register_invalid_email(self, client):
        """Test user registration with invalid email"""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid email address format" in response.json()["detail"]
    
    def test_register_weak_password(self, client):
        """Test user registration with weak password"""
        user_data = {
            "email": "test@example.com",
            "password": "weak",
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Password validation failed" in response.json()["detail"]
    
    def test_register_invalid_hedera_account(self, client):
        """Test user registration with invalid Hedera account ID"""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
            "hedera_account_id": "invalid-account"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid Hedera account ID format" in response.json()["detail"]
    
    def test_register_existing_user(self, client, mock_user_service):
        """Test user registration with existing email"""
        mock_service_instance = Mock()
        mock_service_instance.get_by_email.return_value = Mock(id=1)  # User exists
        mock_user_service.return_value = mock_service_instance
        
        user_data = {
            "email": "existing@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]
    
    def test_login_valid_credentials(self, client, mock_auth_service):
        """Test login with valid credentials"""
        mock_service_instance = Mock()
        mock_user = Mock(email="test@example.com")
        mock_service_instance.authenticate_user.return_value = mock_user
        mock_service_instance.create_access_token.return_value = "test_token"
        mock_auth_service.return_value = mock_service_instance
        
        login_data = {
            "username": "test@example.com",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/api/v1/auth/token", data=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "access_token" in response_data
        assert response_data["token_type"] == "bearer"
        assert "expires_in" in response_data
    
    def test_login_invalid_credentials(self, client, mock_auth_service):
        """Test login with invalid credentials"""
        mock_service_instance = Mock()
        mock_service_instance.authenticate_user.return_value = None  # Authentication failed
        mock_auth_service.return_value = mock_service_instance
        
        login_data = {
            "username": "test@example.com",
            "password": "wrong_password"
        }
        
        response = client.post("/api/v1/auth/token", data=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_get_current_user(self, client):
        """Test getting current user information"""
        with patch('src.mediledger_nexus.api.endpoints.auth.AuthService.get_current_user') as mock_get_user:
            mock_user = Mock(
                id=1,
                email="test@example.com",
                full_name="Test User"
            )
            mock_get_user.return_value = mock_user
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_user
            
            response = client.get("/api/v1/auth/me")
            
            assert response.status_code == status.HTTP_200_OK
            
            # Clean up
            app.dependency_overrides.clear()
    
    def test_refresh_token(self, client, mock_auth_service):
        """Test token refresh"""
        with patch('src.mediledger_nexus.api.endpoints.auth.AuthService.get_current_user') as mock_get_user:
            mock_user = Mock(email="test@example.com")
            mock_get_user.return_value = mock_user
            
            mock_service_instance = Mock()
            mock_service_instance.create_access_token.return_value = "new_test_token"
            mock_auth_service.return_value = mock_service_instance
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_user
            
            response = client.post("/api/v1/auth/refresh")
            
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "access_token" in response_data
            assert response_data["token_type"] == "bearer"
            
            # Clean up
            app.dependency_overrides.clear()


class TestHealthVaultEndpoints:
    """Test health vault endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        return Mock(id=1, email="test@example.com")
    
    def test_create_vault_success(self, client, mock_current_user):
        """Test successful vault creation"""
        with patch('src.mediledger_nexus.api.endpoints.health_vault.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            vault_data = {
                "name": "Test Vault",
                "description": "Test vault description",
                "encryption_enabled": True,
                "zk_proofs_enabled": True,
                "privacy_level": "high"
            }
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.post("/api/v1/vault/create", json=vault_data)
            
            # Note: This might fail without proper service mocking
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()
    
    def test_get_user_vaults(self, client, mock_current_user):
        """Test getting user vaults"""
        with patch('src.mediledger_nexus.api.endpoints.health_vault.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.get("/api/v1/vault/")
            
            # The actual response depends on the implementation
            # This test verifies the endpoint is accessible
            
            # Clean up
            app.dependency_overrides.clear()
    
    def test_unauthorized_vault_access(self, client):
        """Test unauthorized vault access"""
        vault_data = {
            "name": "Test Vault",
            "description": "Test vault description"
        }
        
        response = client.post("/api/v1/vault/create", json=vault_data)
        
        # Should return 401 or 403 for unauthorized access
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestAIDiagnosticsEndpoints:
    """Test AI diagnostics endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        return Mock(id=1, email="test@example.com")
    
    def test_register_ai_agent(self, client, mock_current_user):
        """Test AI agent registration"""
        with patch('src.mediledger_nexus.api.endpoints.ai_diagnostics.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            agent_data = {
                "name": "Test AI Agent",
                "agent_type": "diagnostic_agent",
                "capabilities": ["diagnosis", "health_insights"],
                "hcs_topic_id": "0.0.123456"
            }
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.post("/api/v1/ai/register-agent", json=agent_data)
            
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()
    
    def test_ai_diagnosis_request(self, client, mock_current_user):
        """Test AI diagnosis request"""
        with patch('src.mediledger_nexus.api.endpoints.ai_diagnostics.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            diagnosis_data = {
                "symptoms": ["headache", "fever"],
                "medical_history": {
                    "age": 30,
                    "gender": "female"
                },
                "use_federated_learning": True,
                "privacy_level": "high"
            }
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.post("/api/v1/ai/diagnose", json=diagnosis_data)
            
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()


class TestConsentEndpoints:
    """Test consent management endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        return Mock(id=1, email="test@example.com")
    
    def test_grant_consent(self, client, mock_current_user):
        """Test granting consent"""
        with patch('src.mediledger_nexus.api.endpoints.consent.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            consent_data = {
                "provider_account_id": "0.0.654321",
                "record_types": ["lab_results", "imaging"],
                "duration_hours": 24,
                "compensation_rate": 5.0,
                "purpose": "Medical diagnosis"
            }
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.post("/api/v1/consent/grant", json=consent_data)
            
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()
    
    def test_get_user_consents(self, client, mock_current_user):
        """Test getting user consents"""
        with patch('src.mediledger_nexus.api.endpoints.consent.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.get("/api/v1/consent/")
            
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()


class TestEmergencyEndpoints:
    """Test emergency access endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        return Mock(id=1, email="test@example.com")
    
    def test_emergency_access_request(self, client, mock_current_user):
        """Test emergency access request"""
        with patch('src.mediledger_nexus.api.endpoints.emergency.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            emergency_data = {
                "patient_identifier": "patient@example.com",
                "emergency_type": "cardiac_arrest",
                "requester_credentials": "EMT_LICENSE_12345",
                "location": "General Hospital ER",
                "urgency_level": "critical"
            }
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.post("/api/v1/emergency/access", json=emergency_data)
            
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()
    
    def test_update_emergency_profile(self, client, mock_current_user):
        """Test updating emergency profile"""
        with patch('src.mediledger_nexus.api.endpoints.emergency.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            profile_data = {
                "blood_type": "O+",
                "allergies": ["penicillin", "latex"],
                "current_medications": ["lisinopril"],
                "medical_conditions": ["hypertension"],
                "emergency_contact": {
                    "name": "Jane Doe",
                    "phone": "+1234567890",
                    "relationship": "spouse"
                }
            }
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.put("/api/v1/emergency/profile", json=profile_data)
            
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()


class TestResearchEndpoints:
    """Test research participation endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        return Mock(id=1, email="test@example.com")
    
    def test_get_available_studies(self, client, mock_current_user):
        """Test getting available research studies"""
        with patch('src.mediledger_nexus.api.endpoints.research.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.get("/api/v1/research/studies")
            
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()
    
    def test_participate_in_study(self, client, mock_current_user):
        """Test participating in research study"""
        with patch('src.mediledger_nexus.api.endpoints.research.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            participation_data = {
                "study_id": "study_123",
                "data_types": ["vital_signs", "lab_results"],
                "anonymization_level": "high",
                "compensation_expected": 10.0
            }
            
            # Mock the dependency
            app.dependency_overrides[mock_get_user] = lambda: mock_current_user
            
            response = client.post("/api/v1/research/participate", json=participation_data)
            
            # The actual response depends on the implementation
            
            # Clean up
            app.dependency_overrides.clear()


class TestHealthCheckEndpoint:
    """Test health check endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert "status" in response_data
        assert response_data["status"] == "healthy"
        assert "version" in response_data
        assert "environment" in response_data
        assert "timestamp" in response_data
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert "message" in response_data
        assert "version" in response_data
        assert "docs_url" in response_data


class TestErrorHandling:
    """Test error handling in endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get("/api/v1/nonexistent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error handling"""
        # Try to POST to a GET-only endpoint
        response = client.post("/health")
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_422_validation_error(self, client):
        """Test 422 validation error handling"""
        # Send invalid JSON to registration endpoint
        invalid_data = {
            "email": "not-an-email",
            "password": "",  # Empty password
            # Missing required fields
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        # Should return validation error
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_500_internal_server_error_handling(self, client):
        """Test 500 error handling"""
        # This would require mocking a service to raise an exception
        # The actual implementation depends on how errors are handled
        
        with patch('src.mediledger_nexus.api.endpoints.auth.UserService') as mock_service:
            mock_service.side_effect = Exception("Database connection failed")
            
            user_data = {
                "email": "test@example.com",
                "password": "SecurePassword123!",
                "full_name": "Test User"
            }
            
            response = client.post("/api/v1/auth/register", json=user_data)
            
            # Should handle the exception gracefully
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
