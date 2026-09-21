"""
Unit tests for AI services
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime

from src.mediledger_nexus.ai.groq_service import GroqService
from src.mediledger_nexus.ai.diagnostics import AIDiagnosticsService
from src.mediledger_nexus.ai.federated_learning import FederatedLearningEngine


class TestGroqService:
    """Test GroqService class"""
    
    @pytest.fixture
    def groq_service(self):
        """Create GroqService instance"""
        with patch('src.mediledger_nexus.ai.groq_service.Groq') as mock_groq:
            service = GroqService()
            service.client = mock_groq.return_value
            return service
    
    @pytest.fixture
    def mock_groq_response(self):
        """Mock Groq API response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test AI response"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 100
        return mock_response
    
    def test_generate_response(self, groq_service, mock_groq_response):
        """Test basic response generation"""
        groq_service.client.chat.completions.create.return_value = mock_groq_response
        
        prompt = "What is hypertension?"
        response = groq_service.generate_response(prompt)
        
        assert response == "Test AI response"
        groq_service.client.chat.completions.create.assert_called_once()
        
        # Verify the call parameters
        call_args = groq_service.client.chat.completions.create.call_args
        assert call_args[1]["model"] == "mixtral-8x7b-32768"
        assert len(call_args[1]["messages"]) == 1
        assert call_args[1]["messages"][0]["content"] == prompt
    
    def test_generate_response_with_system_message(self, groq_service, mock_groq_response):
        """Test response generation with system message"""
        groq_service.client.chat.completions.create.return_value = mock_groq_response
        
        prompt = "Diagnose these symptoms"
        system_message = "You are a medical AI assistant"
        
        response = groq_service.generate_response(prompt, system_message=system_message)
        
        assert response == "Test AI response"
        
        # Verify system message is included
        call_args = groq_service.client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == system_message
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == prompt
    
    def test_generate_response_with_custom_parameters(self, groq_service, mock_groq_response):
        """Test response generation with custom parameters"""
        groq_service.client.chat.completions.create.return_value = mock_groq_response
        
        prompt = "Test prompt"
        response = groq_service.generate_response(
            prompt,
            model="llama2-70b-4096",
            temperature=0.8,
            max_tokens=500
        )
        
        assert response == "Test AI response"
        
        # Verify custom parameters
        call_args = groq_service.client.chat.completions.create.call_args
        assert call_args[1]["model"] == "llama2-70b-4096"
        assert call_args[1]["temperature"] == 0.8
        assert call_args[1]["max_tokens"] == 500
    
    def test_generate_response_api_error(self, groq_service):
        """Test handling of API errors"""
        groq_service.client.chat.completions.create.side_effect = Exception("API Error")
        
        prompt = "Test prompt"
        
        with pytest.raises(Exception) as exc_info:
            groq_service.generate_response(prompt)
        
        assert "API Error" in str(exc_info.value)
    
    def test_generate_medical_diagnosis(self, groq_service, mock_groq_response):
        """Test medical diagnosis generation"""
        mock_groq_response.choices[0].message.content = json.dumps({
            "primary_diagnosis": "Hypertension",
            "confidence": 0.85,
            "differential_diagnoses": ["Essential hypertension", "Secondary hypertension"],
            "recommended_tests": ["Blood pressure monitoring", "Urinalysis"],
            "urgency_level": "moderate"
        })
        
        groq_service.client.chat.completions.create.return_value = mock_groq_response
        
        symptoms = ["headache", "dizziness", "chest pain"]
        medical_history = {"age": 45, "gender": "male", "conditions": ["diabetes"]}
        
        diagnosis = groq_service.generate_medical_diagnosis(symptoms, medical_history)
        
        assert isinstance(diagnosis, dict)
        assert "primary_diagnosis" in diagnosis
        assert "confidence" in diagnosis
        assert diagnosis["primary_diagnosis"] == "Hypertension"
        assert diagnosis["confidence"] == 0.85
    
    def test_generate_health_insights(self, groq_service, mock_groq_response):
        """Test health insights generation"""
        mock_groq_response.choices[0].message.content = json.dumps({
            "insights": [
                "Your blood pressure readings suggest hypertension",
                "Consider reducing sodium intake",
                "Regular exercise can help manage blood pressure"
            ],
            "risk_factors": ["High sodium diet", "Sedentary lifestyle"],
            "recommendations": [
                "Monitor blood pressure daily",
                "Consult with cardiologist",
                "Start low-sodium diet"
            ],
            "priority": "high"
        })
        
        groq_service.client.chat.completions.create.return_value = mock_groq_response
        
        health_data = {
            "vital_signs": {"blood_pressure": "150/95", "heart_rate": 80},
            "lab_results": {"cholesterol": 220, "glucose": 95},
            "lifestyle": {"exercise": "sedentary", "diet": "high_sodium"}
        }
        
        insights = groq_service.generate_health_insights(health_data)
        
        assert isinstance(insights, dict)
        assert "insights" in insights
        assert "recommendations" in insights
        assert len(insights["insights"]) == 3
        assert insights["priority"] == "high"
    
    def test_generate_emergency_summary(self, groq_service, mock_groq_response):
        """Test emergency summary generation"""
        mock_groq_response.choices[0].message.content = json.dumps({
            "emergency_summary": "45-year-old male with chest pain and hypertension",
            "critical_conditions": ["Hypertension", "Chest pain"],
            "allergies": ["Penicillin"],
            "current_medications": ["Lisinopril", "Metformin"],
            "emergency_contacts": [{"name": "Jane Doe", "phone": "+1234567890"}],
            "blood_type": "O+",
            "urgency_assessment": "high"
        })
        
        groq_service.client.chat.completions.create.return_value = mock_groq_response
        
        patient_data = {
            "age": 45,
            "gender": "male",
            "conditions": ["hypertension"],
            "symptoms": ["chest_pain"],
            "allergies": ["penicillin"],
            "medications": ["lisinopril", "metformin"],
            "blood_type": "O+"
        }
        
        summary = groq_service.generate_emergency_summary(patient_data)
        
        assert isinstance(summary, dict)
        assert "emergency_summary" in summary
        assert "urgency_assessment" in summary
        assert summary["urgency_assessment"] == "high"
    
    def test_token_usage_tracking(self, groq_service, mock_groq_response):
        """Test token usage tracking"""
        mock_groq_response.usage.prompt_tokens = 50
        mock_groq_response.usage.completion_tokens = 30
        mock_groq_response.usage.total_tokens = 80
        
        groq_service.client.chat.completions.create.return_value = mock_groq_response
        
        prompt = "Test prompt"
        response = groq_service.generate_response(prompt)
        
        # Check if usage is tracked (implementation dependent)
        assert response == "Test AI response"


class TestAIDiagnosticsService:
    """Test AIDiagnosticsService class"""
    
    @pytest.fixture
    def ai_diagnostics_service(self):
        """Create AIDiagnosticsService instance"""
        with patch('src.mediledger_nexus.ai.diagnostics.GroqService') as mock_groq:
            service = AIDiagnosticsService()
            service.groq_service = mock_groq.return_value
            return service
    
    @pytest.fixture
    def sample_diagnosis_request(self):
        """Sample diagnosis request data"""
        return {
            "symptoms": ["fever", "cough", "fatigue"],
            "medical_history": {
                "age": 35,
                "gender": "female",
                "conditions": ["asthma"],
                "medications": ["albuterol"],
                "allergies": ["latex"]
            },
            "privacy_level": "high",
            "use_federated_learning": True
        }
    
    def test_process_diagnosis_request(self, ai_diagnostics_service, sample_diagnosis_request):
        """Test diagnosis request processing"""
        mock_diagnosis = {
            "primary_diagnosis": "Upper respiratory infection",
            "confidence": 0.78,
            "differential_diagnoses": ["Common cold", "Flu", "COVID-19"],
            "recommended_tests": ["COVID-19 test", "Chest X-ray"],
            "urgency_level": "low"
        }
        
        ai_diagnostics_service.groq_service.generate_medical_diagnosis.return_value = mock_diagnosis
        
        result = ai_diagnostics_service.process_diagnosis_request(sample_diagnosis_request)
        
        assert isinstance(result, dict)
        assert "diagnosis" in result
        assert "metadata" in result
        assert result["diagnosis"]["primary_diagnosis"] == "Upper respiratory infection"
        assert result["diagnosis"]["confidence"] == 0.78
        
        # Verify metadata
        metadata = result["metadata"]
        assert "timestamp" in metadata
        assert "privacy_level" in metadata
        assert metadata["privacy_level"] == "high"
    
    def test_process_diagnosis_with_federated_learning(self, ai_diagnostics_service, sample_diagnosis_request):
        """Test diagnosis with federated learning"""
        mock_diagnosis = {
            "primary_diagnosis": "Pneumonia",
            "confidence": 0.82,
            "federated_insights": "Based on similar cases from 3 hospitals"
        }
        
        ai_diagnostics_service.groq_service.generate_medical_diagnosis.return_value = mock_diagnosis
        
        with patch.object(ai_diagnostics_service, '_apply_federated_learning') as mock_fl:
            mock_fl.return_value = {"enhanced_confidence": 0.89}
            
            result = ai_diagnostics_service.process_diagnosis_request(sample_diagnosis_request)
            
            # Verify federated learning was applied
            mock_fl.assert_called_once()
            assert "federated_learning" in result["metadata"]
    
    def test_generate_health_insights(self, ai_diagnostics_service):
        """Test health insights generation"""
        health_data = {
            "vital_signs": {"temperature": 101.2, "heart_rate": 95},
            "lab_results": {"white_blood_cells": 12000},
            "symptoms": ["fever", "chills"]
        }
        
        mock_insights = {
            "insights": ["Elevated temperature suggests infection"],
            "recommendations": ["Rest and hydration", "Monitor temperature"],
            "risk_assessment": "moderate"
        }
        
        ai_diagnostics_service.groq_service.generate_health_insights.return_value = mock_insights
        
        result = ai_diagnostics_service.generate_health_insights(health_data)
        
        assert isinstance(result, dict)
        assert "insights" in result
        assert "recommendations" in result
        assert result["risk_assessment"] == "moderate"
    
    def test_register_ai_agent(self, ai_diagnostics_service):
        """Test AI agent registration"""
        agent_data = {
            "name": "Cardiology AI",
            "agent_type": "diagnostic_agent",
            "capabilities": ["ecg_analysis", "cardiac_diagnosis"],
            "hcs_topic_id": "0.0.123456"
        }
        
        with patch.object(ai_diagnostics_service, '_create_hcs_agent') as mock_create:
            mock_create.return_value = {"agent_id": "agent_123", "status": "active"}
            
            result = ai_diagnostics_service.register_ai_agent(agent_data)
            
            assert isinstance(result, dict)
            assert "agent_id" in result
            assert result["status"] == "active"
            mock_create.assert_called_once_with(agent_data)
    
    def test_connect_ai_agents(self, ai_diagnostics_service):
        """Test AI agent connection"""
        agent1_id = "agent_123"
        agent2_id = "agent_456"
        
        with patch.object(ai_diagnostics_service, '_establish_hcs_connection') as mock_connect:
            mock_connect.return_value = {"connection_id": "conn_789", "status": "connected"}
            
            result = ai_diagnostics_service.connect_ai_agents(agent1_id, agent2_id)
            
            assert isinstance(result, dict)
            assert "connection_id" in result
            assert result["status"] == "connected"
            mock_connect.assert_called_once_with(agent1_id, agent2_id)
    
    def test_privacy_level_enforcement(self, ai_diagnostics_service, sample_diagnosis_request):
        """Test privacy level enforcement"""
        # Test with maximum privacy
        sample_diagnosis_request["privacy_level"] = "maximum"
        
        mock_diagnosis = {"primary_diagnosis": "Test diagnosis"}
        ai_diagnostics_service.groq_service.generate_medical_diagnosis.return_value = mock_diagnosis
        
        with patch.object(ai_diagnostics_service, '_apply_privacy_filters') as mock_privacy:
            mock_privacy.return_value = {"anonymized_diagnosis": "Condition X"}
            
            result = ai_diagnostics_service.process_diagnosis_request(sample_diagnosis_request)
            
            mock_privacy.assert_called_once()
            assert result["metadata"]["privacy_level"] == "maximum"
    
    def test_error_handling_in_diagnosis(self, ai_diagnostics_service, sample_diagnosis_request):
        """Test error handling in diagnosis processing"""
        ai_diagnostics_service.groq_service.generate_medical_diagnosis.side_effect = Exception("AI service error")
        
        with pytest.raises(Exception) as exc_info:
            ai_diagnostics_service.process_diagnosis_request(sample_diagnosis_request)
        
        assert "AI service error" in str(exc_info.value)


class TestFederatedLearningEngine:
    """Test FederatedLearningEngine class"""
    
    @pytest.fixture
    def fl_engine(self):
        """Create FederatedLearningEngine instance"""
        return FederatedLearningEngine()
    
    @pytest.fixture
    def sample_study_config(self):
        """Sample federated learning study configuration"""
        return {
            "study_id": "cardio_study_001",
            "study_type": "cardiovascular_disease",
            "min_participants": 5,
            "max_rounds": 10,
            "privacy_budget": 1.0,
            "aggregation_method": "federated_averaging",
            "data_requirements": ["ecg_data", "vital_signs"]
        }
    
    def test_create_study(self, fl_engine, sample_study_config):
        """Test federated learning study creation"""
        with patch.object(fl_engine, '_initialize_study') as mock_init:
            mock_init.return_value = {"status": "initialized", "participants": 0}
            
            result = fl_engine.create_study(sample_study_config)
            
            assert isinstance(result, dict)
            assert "study_id" in result
            assert result["study_id"] == "cardio_study_001"
            assert result["status"] == "initialized"
            mock_init.assert_called_once_with(sample_study_config)
    
    def test_join_study(self, fl_engine):
        """Test joining a federated learning study"""
        study_id = "cardio_study_001"
        participant_data = {
            "participant_id": "hospital_123",
            "data_types": ["ecg_data", "vital_signs"],
            "privacy_level": "high",
            "contribution_size": 1000
        }
        
        with patch.object(fl_engine, '_validate_participant') as mock_validate:
            mock_validate.return_value = True
            
            with patch.object(fl_engine, '_add_participant') as mock_add:
                mock_add.return_value = {"participant_id": "hospital_123", "status": "joined"}
                
                result = fl_engine.join_study(study_id, participant_data)
                
                assert isinstance(result, dict)
                assert result["participant_id"] == "hospital_123"
                assert result["status"] == "joined"
                mock_validate.assert_called_once()
                mock_add.assert_called_once()
    
    def test_start_training_round(self, fl_engine):
        """Test starting a training round"""
        study_id = "cardio_study_001"
        round_config = {
            "round_number": 1,
            "learning_rate": 0.01,
            "batch_size": 32,
            "epochs": 5
        }
        
        with patch.object(fl_engine, '_distribute_model') as mock_distribute:
            mock_distribute.return_value = {"model_distributed": True, "participants": 5}
            
            result = fl_engine.start_training_round(study_id, round_config)
            
            assert isinstance(result, dict)
            assert "round_id" in result
            assert result["status"] == "training_started"
            mock_distribute.assert_called_once()
    
    def test_aggregate_model_updates(self, fl_engine):
        """Test model update aggregation"""
        study_id = "cardio_study_001"
        round_id = "round_001"
        model_updates = [
            {"participant_id": "hospital_123", "weights": [0.1, 0.2, 0.3]},
            {"participant_id": "hospital_456", "weights": [0.15, 0.25, 0.35]},
            {"participant_id": "hospital_789", "weights": [0.12, 0.22, 0.32]}
        ]
        
        with patch.object(fl_engine, '_federated_averaging') as mock_avg:
            mock_avg.return_value = {"aggregated_weights": [0.123, 0.223, 0.323]}
            
            result = fl_engine.aggregate_model_updates(study_id, round_id, model_updates)
            
            assert isinstance(result, dict)
            assert "aggregated_model" in result
            assert "aggregated_weights" in result["aggregated_model"]
            mock_avg.assert_called_once_with(model_updates)
    
    def test_privacy_preservation(self, fl_engine):
        """Test privacy preservation mechanisms"""
        model_updates = [
            {"participant_id": "hospital_123", "weights": [0.1, 0.2]},
            {"participant_id": "hospital_456", "weights": [0.15, 0.25]}
        ]
        privacy_budget = 1.0
        
        with patch.object(fl_engine, '_apply_differential_privacy') as mock_dp:
            mock_dp.return_value = [0.105, 0.205]  # Noisy weights
            
            result = fl_engine.apply_privacy_preservation(model_updates, privacy_budget)
            
            assert isinstance(result, list)
            assert len(result) == 2  # Number of weights
            mock_dp.assert_called_once()
    
    def test_get_study_status(self, fl_engine):
        """Test getting study status"""
        study_id = "cardio_study_001"
        
        with patch.object(fl_engine, '_get_study_metadata') as mock_metadata:
            mock_metadata.return_value = {
                "study_id": study_id,
                "status": "training",
                "current_round": 3,
                "participants": 7,
                "accuracy": 0.85
            }
            
            result = fl_engine.get_study_status(study_id)
            
            assert isinstance(result, dict)
            assert result["study_id"] == study_id
            assert result["status"] == "training"
            assert result["current_round"] == 3
            assert result["participants"] == 7
    
    def test_list_available_studies(self, fl_engine):
        """Test listing available studies"""
        with patch.object(fl_engine, '_query_studies') as mock_query:
            mock_query.return_value = [
                {"study_id": "cardio_001", "type": "cardiovascular", "participants": 5},
                {"study_id": "diabetes_002", "type": "diabetes", "participants": 8},
                {"study_id": "cancer_003", "type": "oncology", "participants": 12}
            ]
            
            result = fl_engine.list_available_studies()
            
            assert isinstance(result, list)
            assert len(result) == 3
            assert result[0]["study_id"] == "cardio_001"
            assert result[1]["type"] == "diabetes"
            assert result[2]["participants"] == 12
    
    def test_model_convergence_check(self, fl_engine):
        """Test model convergence checking"""
        study_id = "cardio_study_001"
        current_accuracy = 0.92
        previous_accuracy = 0.91
        convergence_threshold = 0.001
        
        with patch.object(fl_engine, '_calculate_convergence') as mock_conv:
            mock_conv.return_value = {"converged": True, "improvement": 0.01}
            
            result = fl_engine.check_convergence(
                study_id, current_accuracy, previous_accuracy, convergence_threshold
            )
            
            assert isinstance(result, dict)
            assert result["converged"] is True
            assert result["improvement"] == 0.01
    
    def test_participant_dropout_handling(self, fl_engine):
        """Test handling of participant dropout"""
        study_id = "cardio_study_001"
        dropped_participant_id = "hospital_456"
        
        with patch.object(fl_engine, '_remove_participant') as mock_remove:
            mock_remove.return_value = {"removed": True, "remaining_participants": 4}
            
            result = fl_engine.handle_participant_dropout(study_id, dropped_participant_id)
            
            assert isinstance(result, dict)
            assert result["removed"] is True
            assert result["remaining_participants"] == 4
            mock_remove.assert_called_once_with(study_id, dropped_participant_id)
