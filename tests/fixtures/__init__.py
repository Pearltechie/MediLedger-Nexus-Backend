"""
Test fixtures for MediLedger Nexus backend tests
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
import uuid


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "password": "SecurePassword123!",
        "full_name": f"Test User {unique_id}",
        "hedera_account_id": f"0.0.{unique_id[:6]}",
        "user_type": "patient",
        "phone_number": "+1234567890"
    }


@pytest.fixture
def sample_provider_data():
    """Sample provider data for testing"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "email": f"provider_{unique_id}@hospital.com",
        "password": "SecurePassword123!",
        "full_name": f"Dr. Provider {unique_id}",
        "hedera_account_id": f"0.0.{unique_id[:6]}",
        "user_type": "provider",
        "license_number": f"MD{unique_id[:6]}",
        "specialization": "cardiology"
    }


@pytest.fixture
def sample_health_vault_data():
    """Sample health vault data for testing"""
    return {
        "name": "Test Health Vault",
        "description": "Test vault for medical records",
        "encryption_enabled": True,
        "zk_proofs_enabled": True,
        "privacy_level": "high",
        "data_types": ["lab_results", "imaging", "vital_signs"]
    }


@pytest.fixture
def sample_medical_record():
    """Sample medical record for testing"""
    return {
        "patient_id": "patient_123",
        "record_type": "lab_results",
        "diagnosis": "Hypertension",
        "medications": ["lisinopril", "hydrochlorothiazide"],
        "test_results": {
            "blood_pressure": "140/90",
            "heart_rate": 75,
            "cholesterol": 200
        },
        "notes": "Patient shows signs of improvement",
        "timestamp": datetime.utcnow().isoformat(),
        "provider_id": "provider_456"
    }


@pytest.fixture
def sample_ai_agent_data():
    """Sample AI agent data for testing"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "name": f"Test AI Agent {unique_id}",
        "agent_type": "diagnostic_agent",
        "capabilities": ["diagnosis", "health_insights", "emergency_response"],
        "hcs_topic_id": f"0.0.{unique_id[:6]}",
        "specialization": "general_medicine",
        "confidence_threshold": 0.8
    }


@pytest.fixture
def sample_consent_data():
    """Sample consent data for testing"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "provider_account_id": f"0.0.{unique_id[:6]}",
        "record_types": ["lab_results", "imaging", "vital_signs"],
        "duration_hours": 24,
        "compensation_rate": 5.0,
        "purpose": "Medical diagnosis and treatment",
        "privacy_level": "high",
        "auto_renewal": False
    }


@pytest.fixture
def sample_diagnosis_request():
    """Sample diagnosis request for testing"""
    return {
        "symptoms": ["chest_pain", "shortness_of_breath", "fatigue"],
        "medical_history": {
            "age": 45,
            "gender": "male",
            "conditions": ["hypertension", "diabetes"],
            "medications": ["lisinopril", "metformin"],
            "allergies": ["penicillin", "latex"]
        },
        "use_federated_learning": True,
        "privacy_level": "high",
        "urgency_level": "moderate"
    }


@pytest.fixture
def sample_emergency_profile():
    """Sample emergency profile for testing"""
    return {
        "blood_type": "O+",
        "allergies": ["penicillin", "latex", "shellfish"],
        "current_medications": ["lisinopril", "metformin", "aspirin"],
        "medical_conditions": ["hypertension", "diabetes", "asthma"],
        "emergency_contact": {
            "name": "Jane Doe",
            "phone": "+1234567890",
            "relationship": "spouse",
            "email": "jane.doe@example.com"
        },
        "insurance_info": {
            "provider": "Health Insurance Co",
            "policy_number": "HIC123456789",
            "group_number": "GRP001"
        }
    }


@pytest.fixture
def sample_federated_learning_config():
    """Sample federated learning configuration for testing"""
    return {
        "study_id": f"fl_study_{uuid.uuid4().hex[:8]}",
        "study_type": "cardiovascular_disease",
        "min_participants": 3,
        "max_rounds": 10,
        "privacy_budget": 1.0,
        "aggregation_method": "federated_averaging",
        "data_requirements": ["ecg_data", "vital_signs", "lab_results"],
        "convergence_threshold": 0.001
    }


@pytest.fixture
def sample_research_study():
    """Sample research study for testing"""
    return {
        "study_id": f"research_{uuid.uuid4().hex[:8]}",
        "title": "Cardiovascular Disease Risk Factors Study",
        "description": "Analyzing risk factors for cardiovascular disease",
        "principal_investigator": "Dr. Research Lead",
        "institution": "Medical Research Institute",
        "data_types": ["vital_signs", "lab_results", "lifestyle_data"],
        "compensation": 25.0,
        "duration_weeks": 12,
        "participant_criteria": {
            "age_range": [18, 65],
            "conditions": ["hypertension", "diabetes"],
            "exclusions": ["pregnancy", "cancer"]
        }
    }


@pytest.fixture
def mock_hedera_client():
    """Mock Hedera client for testing"""
    mock_client = Mock()
    mock_client.account_id = "0.0.123456"
    mock_client.private_key = None
    mock_client.network = "testnet"
    
    # Mock methods
    mock_client.create_topic.return_value = Mock(topic_id="0.0.789012")
    mock_client.submit_message.return_value = Mock(transaction_id="0.0.123456@1234567890.123456789")
    mock_client.get_topic_messages.return_value = []
    mock_client.create_token.return_value = Mock(token_id="0.0.345678")
    mock_client.transfer_tokens.return_value = Mock(success=True)
    
    return mock_client


@pytest.fixture
def mock_groq_client():
    """Mock Groq client for testing"""
    mock_client = Mock()
    
    # Mock response structure
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Mock AI response"
    mock_response.usage = Mock()
    mock_response.usage.total_tokens = 100
    mock_response.usage.prompt_tokens = 60
    mock_response.usage.completion_tokens = 40
    
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_database_session():
    """Mock database session for testing"""
    mock_session = Mock()
    
    # Mock common database operations
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.close.return_value = None
    mock_session.query.return_value = Mock()
    mock_session.execute.return_value = Mock()
    
    return mock_session


@pytest.fixture
def sample_jwt_token():
    """Sample JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjQwOTk1MjAwfQ.mock_signature"


@pytest.fixture
def sample_encryption_key():
    """Sample encryption key for testing"""
    return b"test_encryption_key_32_bytes_long"


@pytest.fixture
def sample_hcs_message():
    """Sample HCS message for testing"""
    return {
        "topic_id": "0.0.123456",
        "message": {
            "type": "agent_registration",
            "agent_id": "agent_123",
            "capabilities": ["diagnosis", "health_insights"],
            "timestamp": datetime.utcnow().isoformat()
        },
        "consensus_timestamp": "1640995200.123456789",
        "sequence_number": 1
    }


@pytest.fixture
def sample_zk_proof():
    """Sample zero-knowledge proof for testing"""
    return {
        "proof": "mock_zk_proof_data",
        "public_inputs": ["input1", "input2"],
        "verification_key": "mock_verification_key",
        "circuit_id": "medical_record_proof",
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture
def sample_heal_token_transaction():
    """Sample HEAL token transaction for testing"""
    return {
        "transaction_id": "0.0.123456@1234567890.123456789",
        "from_account": "0.0.123456",
        "to_account": "0.0.789012",
        "amount": 10.0,
        "token_id": "0.0.345678",
        "memo": "Consent compensation",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "success"
    }


@pytest.fixture
def sample_audit_log():
    """Sample audit log entry for testing"""
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "data_access",
        "user_id": "user_123",
        "resource_id": "vault_456",
        "action": "read",
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0 Test Browser",
        "success": True,
        "details": {
            "record_types": ["lab_results"],
            "privacy_level": "high"
        }
    }
