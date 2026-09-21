"""
Unit tests for service modules
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from src.mediledger_nexus.services.groq_ai import GroqAIService
from src.mediledger_nexus.services.ai_diagnostics import AIDiagnosticsService
from src.mediledger_nexus.ai.federated_learning import FederatedLearningEngine
from src.mediledger_nexus.security.encryption import EncryptionService


class TestGroqAIService:
    """Test GroqAI service"""
    
    @pytest.fixture
    def groq_service(self):
        """Create GroqAI service instance"""
        return GroqAIService()
    
    @patch('src.mediledger_nexus.services.groq_ai.Groq')
    def test_analyze_symptoms(self, mock_groq, groq_service):
        """Test symptom analysis"""
        # Mock Groq client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"primary_diagnosis": "Hypertension", "confidence": 0.85}'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_client
        
        symptoms = ["chest_pain", "shortness_of_breath"]
        medical_history = {"age": 45, "gender": "male"}
        
        result = groq_service.analyze_symptoms(symptoms, medical_history)
        
        assert "primary_diagnosis" in result
        assert "confidence" in result
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('src.mediledger_nexus.services.groq_ai.Groq')
    def test_generate_health_insights(self, mock_groq, groq_service):
        """Test health insights generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"insights": ["Monitor blood pressure"]}'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_client
        
        medical_data = {"conditions": ["hypertension"]}
        
        result = groq_service.generate_health_insights(medical_data)
        
        assert "insights" in result
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('src.mediledger_nexus.services.groq_ai.Groq')
    def test_analyze_research_data(self, mock_groq, groq_service):
        """Test research data analysis"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"patterns": ["Correlation found"]}'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_client
        
        research_data = {"study_type": "cardiovascular", "participants": 100}
        
        result = groq_service.analyze_research_data(research_data)
        
        assert "patterns" in result
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('src.mediledger_nexus.services.groq_ai.Groq')
    def test_generate_emergency_summary(self, mock_groq, groq_service):
        """Test emergency summary generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"summary": "Critical patient", "priority": "high"}'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_client
        
        patient_data = {"blood_type": "O+", "allergies": ["penicillin"]}
        
        result = groq_service.generate_emergency_summary(patient_data)
        
        assert "summary" in result
        assert "priority" in result
        mock_client.chat.completions.create.assert_called_once()
    
    def test_error_handling(self, groq_service):
        """Test error handling in GroqAI service"""
        with patch('src.mediledger_nexus.services.groq_ai.Groq') as mock_groq:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_groq.return_value = mock_client
            
            result = groq_service.analyze_symptoms(["headache"], {})
            
            assert "error" in result
            assert "API Error" in result["error"]


class TestAIDiagnosticsService:
    """Test AI Diagnostics service"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI diagnostics service instance"""
        return AIDiagnosticsService()
    
    @patch('src.mediledger_nexus.services.ai_diagnostics.GroqAIService')
    def test_analyze_symptoms(self, mock_groq_service, ai_service):
        """Test symptom analysis"""
        mock_groq_instance = Mock()
        mock_groq_instance.analyze_symptoms.return_value = {
            "primary_diagnosis": "Hypertension",
            "confidence": 0.85
        }
        mock_groq_service.return_value = mock_groq_instance
        
        symptoms = ["chest_pain"]
        medical_history = {"age": 45}
        
        result = ai_service.analyze_symptoms(symptoms, medical_history)
        
        assert result["primary_diagnosis"] == "Hypertension"
        assert result["confidence"] == 0.85
        mock_groq_instance.analyze_symptoms.assert_called_once_with(symptoms, medical_history)
    
    @patch('src.mediledger_nexus.services.ai_diagnostics.GroqAIService')
    def test_generate_health_insights(self, mock_groq_service, ai_service):
        """Test health insights generation"""
        mock_groq_instance = Mock()
        mock_groq_instance.generate_health_insights.return_value = {
            "insights": ["Monitor blood pressure regularly"]
        }
        mock_groq_service.return_value = mock_groq_instance
        
        medical_data = {"conditions": ["hypertension"]}
        
        result = ai_service.generate_health_insights(medical_data)
        
        assert "insights" in result
        mock_groq_instance.generate_health_insights.assert_called_once_with(medical_data)
    
    def test_process_federated_learning_data(self, ai_service):
        """Test federated learning data processing"""
        fl_data = {
            "model_updates": [{"layer1": [0.1, 0.2]}, {"layer1": [0.15, 0.25]}],
            "participant_count": 2
        }
        
        result = ai_service.process_federated_learning_data(fl_data)
        
        assert "aggregated_model" in result
        assert "insights" in result
        assert result["participant_count"] == 2
    
    def test_generate_emergency_summary(self, ai_service):
        """Test emergency summary generation"""
        patient_data = {
            "blood_type": "O+",
            "allergies": ["penicillin"],
            "conditions": ["diabetes"]
        }
        
        with patch('src.mediledger_nexus.services.ai_diagnostics.GroqAIService') as mock_groq_service:
            mock_groq_instance = Mock()
            mock_groq_instance.generate_emergency_summary.return_value = {
                "summary": "Diabetic patient with penicillin allergy",
                "priority": "medium"
            }
            mock_groq_service.return_value = mock_groq_instance
            
            result = ai_service.generate_emergency_summary(patient_data)
            
            assert "summary" in result
            assert "priority" in result


class TestFederatedLearningEngine:
    """Test Federated Learning Engine"""
    
    @pytest.fixture
    def fl_engine(self):
        """Create federated learning engine instance"""
        return FederatedLearningEngine()
    
    def test_create_round(self, fl_engine):
        """Test creating a federated learning round"""
        study_config = {
            "study_type": "cardiovascular_disease",
            "min_participants": 3,
            "max_rounds": 10
        }
        
        round_id = fl_engine.create_round(study_config)
        
        assert round_id is not None
        assert round_id in fl_engine.active_rounds
        assert fl_engine.active_rounds[round_id]["study_type"] == "cardiovascular_disease"
        assert fl_engine.active_rounds[round_id]["status"] == "waiting_for_participants"
    
    def test_join_round(self, fl_engine):
        """Test joining a federated learning round"""
        # Create a round first
        study_config = {"study_type": "diabetes", "min_participants": 2}
        round_id = fl_engine.create_round(study_config)
        
        participant_id = "participant_123"
        participant_data = {"data_size": 1000}
        
        result = fl_engine.join_round(round_id, participant_id, participant_data)
        
        assert result["success"]
        assert participant_id in fl_engine.active_rounds[round_id]["participants"]
    
    def test_submit_model_update(self, fl_engine):
        """Test submitting model updates"""
        # Setup round with participants
        study_config = {"study_type": "diabetes", "min_participants": 1}
        round_id = fl_engine.create_round(study_config)
        participant_id = "participant_123"
        fl_engine.join_round(round_id, participant_id, {"data_size": 1000})
        
        model_update = {"layer1": [0.1, 0.2, 0.3]}
        
        result = fl_engine.submit_model_update(round_id, participant_id, model_update)
        
        assert result["success"]
        assert round_id in fl_engine.model_updates
        assert participant_id in fl_engine.model_updates[round_id]
    
    def test_aggregate_models(self, fl_engine):
        """Test model aggregation"""
        # Setup round with multiple participants
        study_config = {"study_type": "diabetes", "min_participants": 2}
        round_id = fl_engine.create_round(study_config)
        
        # Add participants and model updates
        participants = ["p1", "p2"]
        for i, p_id in enumerate(participants):
            fl_engine.join_round(round_id, p_id, {"data_size": 1000})
            model_update = {"layer1": [0.1 + i*0.1, 0.2 + i*0.1]}
            fl_engine.submit_model_update(round_id, p_id, model_update)
        
        aggregated_model = fl_engine.aggregate_models(round_id)
        
        assert aggregated_model is not None
        assert "layer1" in aggregated_model
        # Check if aggregation (averaging) worked
        assert aggregated_model["layer1"][0] == 0.15  # (0.1 + 0.2) / 2
    
    @patch('src.mediledger_nexus.ai.federated_learning.GroqAIService')
    def test_generate_insights(self, mock_groq_service, fl_engine):
        """Test generating federated learning insights"""
        mock_groq_instance = Mock()
        mock_groq_instance.generate_federated_learning_insights.return_value = {
            "model_performance": "Good convergence",
            "recommendations": ["Increase learning rate"]
        }
        mock_groq_service.return_value = mock_groq_instance
        
        fl_data = {
            "round_id": "round_123",
            "participant_count": 5,
            "model_accuracy": 0.85
        }
        
        insights = fl_engine.generate_insights(fl_data)
        
        assert "model_performance" in insights
        assert "recommendations" in insights
        mock_groq_instance.generate_federated_learning_insights.assert_called_once()
    
    def test_get_round_status(self, fl_engine):
        """Test getting round status"""
        study_config = {"study_type": "diabetes", "min_participants": 2}
        round_id = fl_engine.create_round(study_config)
        
        status = fl_engine.get_round_status(round_id)
        
        assert status["round_id"] == round_id
        assert status["status"] == "waiting_for_participants"
        assert status["participant_count"] == 0
        
        # Add participant and check status change
        fl_engine.join_round(round_id, "participant_1", {"data_size": 1000})
        status = fl_engine.get_round_status(round_id)
        assert status["participant_count"] == 1


class TestEncryptionService:
    """Test Encryption Service"""
    
    @pytest.fixture
    def encryption_service(self):
        """Create encryption service instance"""
        return EncryptionService()
    
    def test_generate_key(self, encryption_service):
        """Test key generation"""
        key = encryption_service.generate_key()
        assert key is not None
        assert len(key) > 0
    
    def test_encrypt_decrypt_data(self, encryption_service):
        """Test data encryption and decryption"""
        data = "Sensitive medical data"
        key = encryption_service.generate_key()
        
        # Encrypt
        encrypted_data = encryption_service.encrypt_data(data, key)
        assert encrypted_data != data
        assert len(encrypted_data) > len(data)
        
        # Decrypt
        decrypted_data = encryption_service.decrypt_data(encrypted_data, key)
        assert decrypted_data == data
    
    def test_generate_rsa_key_pair(self, encryption_service):
        """Test RSA key pair generation"""
        private_key, public_key = encryption_service.generate_rsa_key_pair()
        
        assert private_key is not None
        assert public_key is not None
        assert private_key != public_key
    
    def test_rsa_encrypt_decrypt(self, encryption_service):
        """Test RSA encryption and decryption"""
        data = "Small sensitive data"
        private_key, public_key = encryption_service.generate_rsa_key_pair()
        
        # Encrypt with public key
        encrypted_data = encryption_service.rsa_encrypt(data, public_key)
        assert encrypted_data != data
        
        # Decrypt with private key
        decrypted_data = encryption_service.rsa_decrypt(encrypted_data, private_key)
        assert decrypted_data == data
    
    def test_hash_data(self, encryption_service):
        """Test data hashing"""
        data = "Data to hash"
        
        hash1 = encryption_service.hash_data(data)
        hash2 = encryption_service.hash_data(data)
        
        assert hash1 == hash2  # Same data should produce same hash
        assert len(hash1) == 64  # SHA256 produces 64 character hex string
        
        # Different data should produce different hash
        hash3 = encryption_service.hash_data("Different data")
        assert hash1 != hash3
    
    def test_create_access_key(self, encryption_service):
        """Test access key creation"""
        user_id = "user_123"
        resource_id = "resource_456"
        permissions = ["read", "write"]
        
        access_key = encryption_service.create_access_key(user_id, resource_id, permissions)
        
        assert access_key is not None
        assert len(access_key) > 0
    
    def test_validate_access_key(self, encryption_service):
        """Test access key validation"""
        user_id = "user_123"
        resource_id = "resource_456"
        permissions = ["read", "write"]
        
        # Create and validate access key
        access_key = encryption_service.create_access_key(user_id, resource_id, permissions)
        is_valid = encryption_service.validate_access_key(access_key, user_id, resource_id)
        
        assert is_valid
        
        # Test with wrong user_id
        is_valid = encryption_service.validate_access_key(access_key, "wrong_user", resource_id)
        assert not is_valid
        
        # Test with wrong resource_id
        is_valid = encryption_service.validate_access_key(access_key, user_id, "wrong_resource")
        assert not is_valid
    
    def test_encrypt_medical_record(self, encryption_service):
        """Test medical record encryption"""
        medical_record = {
            "patient_id": "patient_123",
            "diagnosis": "Hypertension",
            "medications": ["lisinopril"],
            "test_results": {"blood_pressure": "140/90"}
        }
        
        encrypted_record = encryption_service.encrypt_medical_record(medical_record)
        
        assert "encrypted_data" in encrypted_record
        assert "encryption_key" in encrypted_record
        assert "metadata" in encrypted_record
        assert encrypted_record["encrypted_data"] != str(medical_record)
    
    def test_decrypt_medical_record(self, encryption_service):
        """Test medical record decryption"""
        medical_record = {
            "patient_id": "patient_123",
            "diagnosis": "Hypertension"
        }
        
        # Encrypt first
        encrypted_record = encryption_service.encrypt_medical_record(medical_record)
        
        # Decrypt
        decrypted_record = encryption_service.decrypt_medical_record(
            encrypted_record["encrypted_data"],
            encrypted_record["encryption_key"]
        )
        
        assert decrypted_record == medical_record
    
    def test_encryption_error_handling(self, encryption_service):
        """Test encryption error handling"""
        # Test decryption with wrong key
        data = "test data"
        key1 = encryption_service.generate_key()
        key2 = encryption_service.generate_key()
        
        encrypted_data = encryption_service.encrypt_data(data, key1)
        
        # Should raise exception or return error when using wrong key
        try:
            decrypted_data = encryption_service.decrypt_data(encrypted_data, key2)
            # If no exception, check if it returns original data (it shouldn't)
            assert decrypted_data != data
        except Exception:
            # Exception is expected for wrong key
            pass
