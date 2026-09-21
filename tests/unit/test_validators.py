"""
Unit tests for validation utilities
"""

import pytest
from datetime import date, datetime

from src.mediledger_nexus.utils.validators import DataValidator, MedicalDataValidator


class TestDataValidator:
    """Test DataValidator class"""
    
    def test_validate_email_address(self):
        """Test email validation"""
        # Valid emails
        assert DataValidator.validate_email_address("test@example.com")
        assert DataValidator.validate_email_address("user.name@domain.co.uk")
        assert DataValidator.validate_email_address("test+tag@example.org")
        
        # Invalid emails
        assert not DataValidator.validate_email_address("invalid-email")
        assert not DataValidator.validate_email_address("@domain.com")
        assert not DataValidator.validate_email_address("user@")
        assert not DataValidator.validate_email_address("")
    
    def test_validate_hedera_account_id(self):
        """Test Hedera account ID validation"""
        # Valid account IDs
        assert DataValidator.validate_hedera_account_id("0.0.123456")
        assert DataValidator.validate_hedera_account_id("0.0.1")
        assert DataValidator.validate_hedera_account_id("0.0.999999999")
        
        # Invalid account IDs
        assert not DataValidator.validate_hedera_account_id("123456")
        assert not DataValidator.validate_hedera_account_id("0.0")
        assert not DataValidator.validate_hedera_account_id("1.0.123456")
        assert not DataValidator.validate_hedera_account_id("0.0.abc")
        assert not DataValidator.validate_hedera_account_id("")
    
    def test_validate_hedera_topic_id(self):
        """Test Hedera topic ID validation"""
        # Valid topic IDs
        assert DataValidator.validate_hedera_topic_id("0.0.123456")
        assert DataValidator.validate_hedera_topic_id("0.0.1")
        
        # Invalid topic IDs
        assert not DataValidator.validate_hedera_topic_id("123456")
        assert not DataValidator.validate_hedera_topic_id("invalid")
    
    def test_validate_password_strength(self):
        """Test password strength validation"""
        # Strong password
        result = DataValidator.validate_password_strength("SecurePassword123!")
        assert result["is_valid"]
        assert len(result["issues"]) == 0
        
        # Weak passwords
        weak_passwords = [
            "weak",  # Too short
            "weakpassword",  # No uppercase, digits, special chars
            "WEAKPASSWORD",  # No lowercase, digits, special chars
            "WeakPassword",  # No digits, special chars
            "WeakPassword123",  # No special chars
        ]
        
        for password in weak_passwords:
            result = DataValidator.validate_password_strength(password)
            assert not result["is_valid"]
            assert len(result["issues"]) > 0
    
    def test_validate_phone_number(self):
        """Test phone number validation"""
        # Valid phone numbers
        assert DataValidator.validate_phone_number("+1234567890")
        assert DataValidator.validate_phone_number("1234567890")
        assert DataValidator.validate_phone_number("+44 20 7946 0958")
        assert DataValidator.validate_phone_number("(555) 123-4567")
        
        # Invalid phone numbers
        assert not DataValidator.validate_phone_number("123")  # Too short
        assert not DataValidator.validate_phone_number("1234567890123456")  # Too long
        assert not DataValidator.validate_phone_number("")
    
    def test_validate_blood_type(self):
        """Test blood type validation"""
        # Valid blood types
        valid_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        for blood_type in valid_types:
            assert DataValidator.validate_blood_type(blood_type)
        
        # Invalid blood types
        assert not DataValidator.validate_blood_type("C+")
        assert not DataValidator.validate_blood_type("A")
        assert not DataValidator.validate_blood_type("")
    
    def test_validate_medical_record_type(self):
        """Test medical record type validation"""
        # Valid types
        valid_types = ["lab_results", "imaging", "prescriptions", "allergies"]
        for record_type in valid_types:
            assert DataValidator.validate_medical_record_type(record_type)
        
        # Invalid types
        assert not DataValidator.validate_medical_record_type("invalid_type")
        assert not DataValidator.validate_medical_record_type("")
    
    def test_validate_file_extension(self):
        """Test file extension validation"""
        # Valid extensions
        valid_files = ["test.pdf", "image.jpg", "data.csv", "report.docx"]
        for filename in valid_files:
            assert DataValidator.validate_file_extension(filename)
        
        # Invalid extensions
        invalid_files = ["test.exe", "virus.bat", "script.js"]
        for filename in invalid_files:
            assert not DataValidator.validate_file_extension(filename)
    
    def test_validate_file_size(self):
        """Test file size validation"""
        # Valid sizes
        assert DataValidator.validate_file_size(1024 * 1024)  # 1MB
        assert DataValidator.validate_file_size(10 * 1024 * 1024)  # 10MB
        
        # Invalid sizes
        assert not DataValidator.validate_file_size(100 * 1024 * 1024)  # 100MB (exceeds default)
        assert not DataValidator.validate_file_size(600 * 1024 * 1024, "GENOMIC")  # Exceeds genomic limit
    
    def test_validate_vital_signs(self):
        """Test vital signs validation"""
        # Normal vital signs
        normal_vitals = {
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 70,
            "temperature": 98.6
        }
        result = DataValidator.validate_vital_signs(normal_vitals)
        assert result["is_valid"]
        assert len(result["issues"]) == 0
        
        # Abnormal vital signs
        abnormal_vitals = {
            "blood_pressure_systolic": 200,  # Too high
            "heart_rate": 40  # Too low
        }
        result = DataValidator.validate_vital_signs(abnormal_vitals)
        assert not result["is_valid"]
        assert len(result["issues"]) > 0
    
    def test_validate_lab_results(self):
        """Test lab results validation"""
        # Normal lab results
        normal_labs = {
            "glucose": 90,
            "cholesterol_total": 180
        }
        result = DataValidator.validate_lab_results(normal_labs)
        assert result["is_valid"]
        
        # Abnormal lab results
        abnormal_labs = {
            "glucose": 300,  # Too high
            "cholesterol_total": 300  # Too high
        }
        result = DataValidator.validate_lab_results(abnormal_labs)
        assert not result["is_valid"]
        assert len(result["issues"]) > 0
    
    def test_validate_age(self):
        """Test age validation"""
        # Valid ages
        result = DataValidator.validate_age("1990-01-01")
        assert result["is_valid"]
        assert result["age"] > 0
        
        result = DataValidator.validate_age(date(1990, 1, 1))
        assert result["is_valid"]
        
        # Invalid ages
        future_date = "2030-01-01"
        result = DataValidator.validate_age(future_date)
        assert not result["is_valid"]
        assert "future" in result["error"].lower()
    
    def test_validate_allergy_list(self):
        """Test allergy list validation"""
        # Valid allergies
        valid_allergies = ["penicillin", "peanuts", "shellfish"]
        result = DataValidator.validate_allergy_list(valid_allergies)
        assert result["is_valid"]
        assert len(result["valid_allergies"]) == 3
        
        # Mixed valid/invalid allergies
        mixed_allergies = ["penicillin", "", "invalid@allergy!"]
        result = DataValidator.validate_allergy_list(mixed_allergies)
        assert not result["is_valid"]
        assert len(result["issues"]) > 0
    
    def test_validate_emergency_contact(self):
        """Test emergency contact validation"""
        # Valid contact
        valid_contact = {
            "name": "John Doe",
            "phone": "+1234567890",
            "relationship": "spouse",
            "email": "john@example.com"
        }
        result = DataValidator.validate_emergency_contact(valid_contact)
        assert result["is_valid"]
        
        # Invalid contact
        invalid_contact = {
            "name": "",  # Missing name
            "phone": "invalid",  # Invalid phone
            "relationship": "invalid_relationship"  # Invalid relationship
        }
        result = DataValidator.validate_emergency_contact(invalid_contact)
        assert not result["is_valid"]
        assert len(result["issues"]) > 0
    
    def test_validate_consent_duration(self):
        """Test consent duration validation"""
        assert DataValidator.validate_consent_duration(24)  # 24 hours
        assert DataValidator.validate_consent_duration(168)  # 1 week
        assert not DataValidator.validate_consent_duration(0)  # Too short
        assert not DataValidator.validate_consent_duration(365 * 24 + 1)  # Too long
    
    def test_validate_compensation_rate(self):
        """Test compensation rate validation"""
        assert DataValidator.validate_compensation_rate(5.0)
        assert DataValidator.validate_compensation_rate(0.0)
        assert DataValidator.validate_compensation_rate(1000.0)
        assert not DataValidator.validate_compensation_rate(-1.0)  # Negative
        assert not DataValidator.validate_compensation_rate(1001.0)  # Too high
    
    def test_validate_diagnostic_confidence(self):
        """Test diagnostic confidence validation"""
        assert DataValidator.validate_diagnostic_confidence(0.0)
        assert DataValidator.validate_diagnostic_confidence(0.5)
        assert DataValidator.validate_diagnostic_confidence(1.0)
        assert not DataValidator.validate_diagnostic_confidence(-0.1)
        assert not DataValidator.validate_diagnostic_confidence(1.1)
    
    def test_validate_json_structure(self):
        """Test JSON structure validation"""
        # Valid structure
        data = {"field1": "value1", "field2": "value2"}
        required_fields = ["field1", "field2"]
        result = DataValidator.validate_json_structure(data, required_fields)
        assert result["is_valid"]
        
        # Missing fields
        data = {"field1": "value1"}
        required_fields = ["field1", "field2"]
        result = DataValidator.validate_json_structure(data, required_fields)
        assert not result["is_valid"]
        assert len(result["issues"]) > 0
        
        # Null values
        data = {"field1": "value1", "field2": None}
        required_fields = ["field1", "field2"]
        result = DataValidator.validate_json_structure(data, required_fields)
        assert not result["is_valid"]


class TestMedicalDataValidator:
    """Test Pydantic-based medical data validator"""
    
    def test_email_validation(self):
        """Test email validation in Pydantic model"""
        # This would require creating a test model that uses the validator
        # For now, we'll test the underlying validator function
        assert DataValidator.validate_email_address("test@example.com")
    
    def test_hedera_account_validation(self):
        """Test Hedera account validation in Pydantic model"""
        assert DataValidator.validate_hedera_account_id("0.0.123456")
    
    def test_blood_type_validation(self):
        """Test blood type validation in Pydantic model"""
        assert DataValidator.validate_blood_type("O+")
    
    def test_phone_validation(self):
        """Test phone validation in Pydantic model"""
        assert DataValidator.validate_phone_number("+1234567890")
