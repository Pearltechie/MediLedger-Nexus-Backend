"""
Unit tests for data formatting utilities
"""

import pytest
from datetime import datetime, date, timezone
from decimal import Decimal

from src.mediledger_nexus.utils.formatters import DataFormatter


class TestDataFormatter:
    """Test DataFormatter class"""
    
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        # Test with specific datetime
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        formatted = DataFormatter.format_timestamp(dt)
        assert "2024-01-01T12:00:00" in formatted
        assert "+00:00" in formatted
        
        # Test with None (current time)
        formatted = DataFormatter.format_timestamp()
        assert "T" in formatted  # ISO format
        
        # Test without timezone
        formatted = DataFormatter.format_timestamp(dt, include_timezone=False)
        assert "+00:00" not in formatted or "Z" not in formatted
    
    def test_format_date(self):
        """Test date formatting"""
        # Test with specific date
        d = date(2024, 1, 1)
        formatted = DataFormatter.format_date(d)
        assert formatted == "2024-01-01"
        
        # Test with None (current date)
        formatted = DataFormatter.format_date()
        assert len(formatted) == 10  # YYYY-MM-DD format
    
    def test_format_hedera_account_id(self):
        """Test Hedera account ID formatting"""
        # Already formatted
        assert DataFormatter.format_hedera_account_id("0.0.123456") == "0.0.123456"
        
        # Just account number
        assert DataFormatter.format_hedera_account_id("123456") == "0.0.123456"
        
        # With whitespace
        assert DataFormatter.format_hedera_account_id(" 0.0.123456 ") == "0.0.123456"
    
    def test_format_phone_number(self):
        """Test phone number formatting"""
        # US number without country code
        assert DataFormatter.format_phone_number("1234567890").startswith("+1")
        
        # Already formatted
        formatted = DataFormatter.format_phone_number("+1234567890")
        assert formatted.startswith("+")
        
        # With formatting characters
        formatted = DataFormatter.format_phone_number("(555) 123-4567")
        assert "(" not in formatted and ")" not in formatted and "-" not in formatted
    
    def test_format_medical_record_id(self):
        """Test medical record ID generation"""
        user_id = "user123456789"
        record_type = "lab_results"
        
        record_id = DataFormatter.format_medical_record_id(user_id, record_type)
        
        assert record_id.startswith("MR_")
        assert "user1234" in record_id  # First 8 chars of user_id
        assert "LAB" in record_id  # First 3 chars of record_type
        assert len(record_id.split("_")) == 4  # MR_userid_type_timestamp
    
    def test_format_consent_id(self):
        """Test consent ID generation"""
        user_id = "user123456789"
        provider_id = "provider123456789"
        
        consent_id = DataFormatter.format_consent_id(user_id, provider_id)
        
        assert consent_id.startswith("CNS_")
        assert "user1234" in consent_id
        assert "provider" in consent_id
    
    def test_format_ai_agent_id(self):
        """Test AI agent ID generation"""
        agent_name = "Diagnostic Agent"
        agent_type = "diagnostic_agent"
        user_id = "user123456789"
        
        agent_id = DataFormatter.format_ai_agent_id(agent_name, agent_type, user_id)
        
        assert agent_id.startswith("AI_")
        assert "DIA" in agent_id  # First 3 chars of agent_type
        assert "user1234" in agent_id
    
    def test_format_vault_id(self):
        """Test vault ID generation"""
        user_id = "user123456789"
        vault_name = "Primary Health Vault"
        
        vault_id = DataFormatter.format_vault_id(user_id, vault_name)
        
        assert vault_id.startswith("VLT_")
        assert "user1234" in vault_id
        assert "PRIMARY" in vault_id or "HEALTH" in vault_id
    
    def test_format_file_size(self):
        """Test file size formatting"""
        assert DataFormatter.format_file_size(0) == "0 B"
        assert DataFormatter.format_file_size(1024) == "1.0 KB"
        assert DataFormatter.format_file_size(1024 * 1024) == "1.0 MB"
        assert DataFormatter.format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert DataFormatter.format_file_size(1536) == "1.5 KB"  # 1.5 KB
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert DataFormatter.format_currency(5.0) == "5.00 HEAL"
        assert DataFormatter.format_currency(5.123) == "5.12 HEAL"
        assert DataFormatter.format_currency(Decimal("5.50")) == "5.50 HEAL"
        assert DataFormatter.format_currency(5.0, "USD") == "5.00 USD"
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        assert DataFormatter.format_percentage(0.5) == "50.0%"
        assert DataFormatter.format_percentage(0.123) == "12.3%"
        assert DataFormatter.format_percentage(0.123, 2) == "12.30%"
        assert DataFormatter.format_percentage(1.0) == "100.0%"
    
    def test_format_vital_signs(self):
        """Test vital signs formatting"""
        vital_signs = {
            "blood_pressure_systolic": 120,
            "heart_rate": 70,
            "temperature": 98.6
        }
        
        formatted = DataFormatter.format_vital_signs(vital_signs)
        
        assert "blood_pressure_systolic" in formatted
        assert "120 mmHg" in formatted["blood_pressure_systolic"]["value"]
        assert formatted["blood_pressure_systolic"]["status"] == "Normal"
        
        assert "heart_rate" in formatted
        assert "70 bpm" in formatted["heart_rate"]["value"]
        
        # Test abnormal values
        abnormal_vitals = {"blood_pressure_systolic": 200}
        formatted = DataFormatter.format_vital_signs(abnormal_vitals)
        assert formatted["blood_pressure_systolic"]["status"] == "High"
    
    def test_format_lab_results(self):
        """Test lab results formatting"""
        lab_results = {
            "glucose": 90,
            "cholesterol_total": 180
        }
        
        formatted = DataFormatter.format_lab_results(lab_results)
        
        assert "glucose" in formatted
        assert "90 mg/dL" in formatted["glucose"]["value"]
        assert formatted["glucose"]["status"] == "Normal"
        
        # Test abnormal values
        abnormal_labs = {"glucose": 300}
        formatted = DataFormatter.format_lab_results(abnormal_labs)
        assert formatted["glucose"]["status"] == "High"
    
    def test_format_medical_history(self):
        """Test medical history formatting"""
        history = {
            "age": 45,
            "gender": "male",
            "conditions": ["hypertension", "diabetes"],
            "medications": ["lisinopril", "metformin"],
            "allergies": ["penicillin"]
        }
        
        formatted = DataFormatter.format_medical_history(history)
        
        assert formatted["age"] == "45 years old"
        assert formatted["gender"] == "Male"
        assert "hypertension" in formatted["conditions"]
        assert "lisinopril" in formatted["medications"]
        assert "penicillin" in formatted["allergies"]
    
    def test_format_diagnosis_result(self):
        """Test diagnosis result formatting"""
        diagnosis = {
            "diagnosis_id": "diag_123",
            "timestamp": datetime.now(),
            "primary_diagnosis": "Hypertension",
            "confidence": 0.85,
            "severity": "moderate",
            "urgency": "low",
            "differential_diagnoses": [
                {"condition": "Anxiety", "confidence": 0.3}
            ],
            "recommendations": ["Monitor blood pressure", "Lifestyle changes"]
        }
        
        formatted = DataFormatter.format_diagnosis_result(diagnosis)
        
        assert formatted["diagnosis_id"] == "diag_123"
        assert formatted["primary_diagnosis"] == "Hypertension"
        assert "85.0%" in formatted["confidence"]
        assert formatted["severity"] == "Moderate"
        assert len(formatted["differential_diagnoses"]) == 1
        assert "30.0%" in formatted["differential_diagnoses"][0]["confidence"]
    
    def test_format_consent_summary(self):
        """Test consent summary formatting"""
        consent = {
            "id": "consent_123",
            "provider_account_id": "0.0.654321",
            "status": "active",
            "granted_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24),
            "compensation_rate": 5.0,
            "purpose": "Medical diagnosis",
            "record_types": ["lab_results", "imaging"]
        }
        
        formatted = DataFormatter.format_consent_summary(consent)
        
        assert formatted["consent_id"] == "consent_123"
        assert formatted["status"] == "Active"
        assert "5.00 HEAL" in formatted["compensation_rate"]
        assert "lab_results, imaging" in formatted["record_types"]
    
    def test_format_emergency_profile(self):
        """Test emergency profile formatting"""
        profile = {
            "blood_type": "O+",
            "allergies": ["penicillin", "latex"],
            "current_medications": ["lisinopril"],
            "medical_conditions": ["hypertension"],
            "emergency_contact": {
                "name": "Jane Doe",
                "relationship": "spouse",
                "phone": "+1234567890"
            }
        }
        
        formatted = DataFormatter.format_emergency_profile(profile)
        
        assert formatted["blood_type"] == "O+"
        assert "penicillin, latex" in formatted["allergies"]
        assert "lisinopril" in formatted["medications"]
        assert "Jane Doe (spouse) - +1234567890" in formatted["emergency_contact_formatted"]
    
    def test_format_hcs10_message(self):
        """Test HCS-10 message formatting"""
        payload = {"test": "data"}
        sender_id = "0.0.123456"
        recipient_id = "0.0.654321"
        
        formatted = DataFormatter.format_hcs10_message("register", payload, sender_id, recipient_id)
        
        assert formatted["protocol_version"] == "1.0"
        assert formatted["message_type"] == "register"
        assert formatted["sender_id"] == sender_id
        assert formatted["recipient_id"] == recipient_id
        assert formatted["payload"] == payload
        assert "message_hash" in formatted
        assert len(formatted["message_hash"]) == 64  # SHA256 hash
    
    def test_format_federated_learning_round(self):
        """Test federated learning round formatting"""
        round_info = {
            "round_id": "round_123",
            "study_type": "cardiovascular_disease",
            "participant_count": 5,
            "status": "active",
            "started_at": datetime.now(),
            "model_accuracy": 0.85,
            "privacy_budget": 1.0
        }
        
        formatted = DataFormatter.format_federated_learning_round(round_info)
        
        assert formatted["round_id"] == "round_123"
        assert formatted["study_type"] == "Cardiovascular Disease"
        assert formatted["participants"] == 5
        assert formatted["status"] == "Active"
        assert "85.0%" in formatted["model_accuracy"]
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Normal filename
        assert DataFormatter.sanitize_filename("test.pdf") == "test.pdf"
        
        # Filename with unsafe characters
        unsafe = "test<>:\"/\\|?*.pdf"
        sanitized = DataFormatter.sanitize_filename(unsafe)
        assert "<" not in sanitized
        assert ">" not in sanitized
        assert ":" not in sanitized
        
        # Filename starting with dot
        assert DataFormatter.sanitize_filename(".hidden") == "file.hidden"
        
        # Very long filename
        long_name = "a" * 150 + ".pdf"
        sanitized = DataFormatter.sanitize_filename(long_name)
        assert len(sanitized) <= 100
        assert sanitized.endswith(".pdf")
    
    def test_mask_sensitive_data(self):
        """Test sensitive data masking"""
        # Normal masking
        assert DataFormatter.mask_sensitive_data("1234567890") == "1234******"
        assert DataFormatter.mask_sensitive_data("secret", visible_chars=2) == "se****"
        
        # Short data
        assert DataFormatter.mask_sensitive_data("abc") == "***"
        
        # Custom mask character
        assert DataFormatter.mask_sensitive_data("1234567890", mask_char="X") == "1234XXXXXX"
    
    def test_format_json_response(self):
        """Test JSON response formatting"""
        data = {"test": "value"}
        
        response = DataFormatter.format_json_response(data)
        
        assert response["status"] == "success"
        assert response["data"] == data
        assert "timestamp" in response
        
        # With message
        response = DataFormatter.format_json_response(data, message="Test message")
        assert response["message"] == "Test message"
    
    def test_format_error_response(self):
        """Test error response formatting"""
        error = "Test error"
        
        response = DataFormatter.format_error_response(error)
        
        assert response["status"] == "error"
        assert response["error"] == error
        assert "timestamp" in response
        
        # With error code and details
        response = DataFormatter.format_error_response(
            error, 
            error_code="TEST_ERROR",
            details={"field": "value"}
        )
        assert response["error_code"] == "TEST_ERROR"
        assert response["details"]["field"] == "value"
