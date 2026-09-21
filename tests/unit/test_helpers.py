"""
Unit tests for health data helper utilities
"""

import pytest
from datetime import datetime, date
from unittest.mock import patch
import json

from src.mediledger_nexus.utils.helpers import HealthDataHelper


class TestHealthDataHelper:
    """Test HealthDataHelper class"""
    
    def test_generate_secure_id(self):
        """Test secure ID generation"""
        # Without prefix
        secure_id = HealthDataHelper.generate_secure_id()
        assert len(secure_id) == 32
        assert all(c in "0123456789abcdef" for c in secure_id)
        
        # With prefix
        secure_id = HealthDataHelper.generate_secure_id("TEST", 16)
        assert secure_id.startswith("TEST_")
        assert len(secure_id.split("_")[1]) == 16
        
        # Different lengths
        secure_id = HealthDataHelper.generate_secure_id(length=64)
        assert len(secure_id) == 64
    
    def test_generate_uuid(self):
        """Test UUID generation"""
        uuid1 = HealthDataHelper.generate_uuid()
        uuid2 = HealthDataHelper.generate_uuid()
        
        assert len(uuid1) == 36  # Standard UUID format
        assert "-" in uuid1
        assert uuid1 != uuid2  # Should be unique
    
    def test_calculate_age(self):
        """Test age calculation"""
        # Test with string date
        age = HealthDataHelper.calculate_age("1990-01-01")
        current_year = datetime.now().year
        expected_age = current_year - 1990
        assert age == expected_age or age == expected_age - 1  # Account for birthday
        
        # Test with datetime
        birth_date = datetime(1990, 1, 1)
        age = HealthDataHelper.calculate_age(birth_date)
        assert age >= 30  # Should be at least 30 in 2024+
    
    def test_calculate_bmi(self):
        """Test BMI calculation"""
        # Normal weight
        result = HealthDataHelper.calculate_bmi(70, 175)  # 70kg, 175cm
        assert 22 <= result["bmi"] <= 24
        assert result["category"] == "Normal weight"
        
        # Underweight
        result = HealthDataHelper.calculate_bmi(45, 175)
        assert result["category"] == "Underweight"
        
        # Overweight
        result = HealthDataHelper.calculate_bmi(85, 175)
        assert result["category"] == "Overweight"
        
        # Obese
        result = HealthDataHelper.calculate_bmi(100, 175)
        assert result["category"] == "Obese"
    
    def test_assess_vital_signs_risk(self):
        """Test vital signs risk assessment"""
        # Normal vital signs
        normal_vitals = {
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 70
        }
        result = HealthDataHelper.assess_vital_signs_risk(normal_vitals)
        assert result["risk_level"] == "Low"
        assert result["risk_score"] == 0
        assert len(result["risk_factors"]) == 0
        
        # High risk vital signs
        high_risk_vitals = {
            "blood_pressure_systolic": 200,  # High
            "heart_rate": 40  # Low
        }
        result = HealthDataHelper.assess_vital_signs_risk(high_risk_vitals)
        assert result["risk_level"] in ["High", "Critical"]
        assert result["risk_score"] > 0
        assert len(result["risk_factors"]) > 0
    
    def test_categorize_medications(self):
        """Test medication categorization"""
        medications = [
            "lisinopril",  # Cardiovascular
            "metformin",   # Diabetes
            "ibuprofen",   # Pain management
            "unknown_medication"  # Uncategorized
        ]
        
        result = HealthDataHelper.categorize_medications(medications)
        
        assert "cardiovascular" in result
        assert "lisinopril" in result["cardiovascular"]
        
        assert "diabetes" in result
        assert "metformin" in result["diabetes"]
        
        assert "pain_management" in result
        assert "ibuprofen" in result["pain_management"]
        
        assert "uncategorized" in result
        assert "unknown_medication" in result["uncategorized"]
    
    def test_calculate_consent_earnings(self):
        """Test consent earnings calculation"""
        # Basic calculation
        result = HealthDataHelper.calculate_consent_earnings(24, 5.0, ["vital_signs"])
        assert result["base_earnings"] == 120.0  # 24 * 5.0
        assert result["sensitivity_multiplier"] == 1.0
        assert result["final_earnings"] == 120.0
        assert result["currency"] == "HEAL"
        
        # With sensitive data
        result = HealthDataHelper.calculate_consent_earnings(24, 5.0, ["genomics"])
        assert result["sensitivity_multiplier"] == 2.0
        assert result["final_earnings"] == 240.0  # 120 * 2.0
        
        # Multiple data types
        result = HealthDataHelper.calculate_consent_earnings(24, 5.0, ["vital_signs", "genomics"])
        assert result["sensitivity_multiplier"] == 2.0  # Takes highest multiplier
    
    def test_generate_emergency_summary(self):
        """Test emergency summary generation"""
        patient_data = {
            "blood_type": "O+",
            "allergies": ["penicillin", "latex"],
            "medications": ["lisinopril", "metformin"],
            "conditions": ["hypertension", "diabetes"],
            "emergency_contact": {
                "name": "Jane Doe",
                "phone": "+1234567890",
                "relationship": "spouse"
            },
            "vital_signs": {
                "blood_pressure_systolic": 200  # High
            }
        }
        
        summary = HealthDataHelper.generate_emergency_summary(patient_data)
        
        assert summary["allergies"] == ["penicillin", "latex"]
        assert summary["current_medications"] == ["lisinopril", "metformin"]
        assert summary["medical_conditions"] == ["hypertension", "diabetes"]
        assert summary["emergency_contact"]["name"] == "Jane Doe"
        assert summary["critical_info"]["blood_type"] == "O+"
        assert summary["critical_info"]["vital_signs_risk"] in ["High", "Critical"]
        assert "penicillin" in summary["critical_info"]["critical_allergies"]
        assert "last_updated" in summary
    
    def test_calculate_privacy_score(self):
        """Test privacy score calculation"""
        # High privacy scenario
        result = HealthDataHelper.calculate_privacy_score(
            ["vital_signs"], "individual", "maximum"
        )
        assert result["privacy_score"] >= 80
        assert result["level"] == "High"
        
        # Low privacy scenario
        result = HealthDataHelper.calculate_privacy_score(
            ["genomics", "mental_health"], "public", "low"
        )
        assert result["privacy_score"] < 60
        assert result["level"] == "Low"
        assert len(result["recommendations"]) > 0
        
        # Medium privacy scenario
        result = HealthDataHelper.calculate_privacy_score(
            ["lab_results"], "research", "medium"
        )
        assert 60 <= result["privacy_score"] < 80 or result["privacy_score"] >= 80
    
    def test_generate_health_insights(self):
        """Test health insights generation"""
        medical_data = {
            "vital_signs_history": [
                {"blood_pressure_systolic": 120},
                {"blood_pressure_systolic": 130}
            ],
            "conditions": ["diabetes", "hypertension"],
            "medications": ["amoxicillin"],
            "allergies": ["penicillin"]
        }
        
        insights = HealthDataHelper.generate_health_insights(medical_data)
        
        assert "risk_factors" in insights
        assert "recommendations" in insights
        assert "trends" in insights
        assert "alerts" in insights
        
        # Should identify diabetes as risk factor
        assert any("diabetes" in rf.lower() or "cardiovascular" in rf.lower() 
                  for rf in insights["risk_factors"])
        
        # Should detect potential allergy interaction
        assert any("allergy" in alert.lower() for alert in insights["alerts"])
        
        # Should detect blood pressure trend
        if "blood_pressure" in insights["trends"]:
            assert insights["trends"]["blood_pressure"] in ["increasing", "decreasing", "stable"]
    
    def test_hash_medical_data(self):
        """Test medical data hashing"""
        data = {"patient_id": "123", "diagnosis": "hypertension"}
        
        # Generate hash
        hash_with_salt = HealthDataHelper.hash_medical_data(data)
        assert ":" in hash_with_salt
        assert len(hash_with_salt.split(":")) == 2
        
        salt, hash_value = hash_with_salt.split(":")
        assert len(salt) == 32  # 16 bytes hex = 32 chars
        assert len(hash_value) == 64  # SHA256 = 64 chars
        
        # Test with custom salt
        custom_salt = "custom_salt_123"
        hash_with_custom_salt = HealthDataHelper.hash_medical_data(data, custom_salt)
        assert hash_with_custom_salt.startswith(custom_salt + ":")
    
    def test_verify_medical_data_hash(self):
        """Test medical data hash verification"""
        data = {"patient_id": "123", "diagnosis": "hypertension"}
        
        # Generate hash and verify
        hash_with_salt = HealthDataHelper.hash_medical_data(data)
        assert HealthDataHelper.verify_medical_data_hash(data, hash_with_salt)
        
        # Verify with modified data (should fail)
        modified_data = {"patient_id": "456", "diagnosis": "hypertension"}
        assert not HealthDataHelper.verify_medical_data_hash(modified_data, hash_with_salt)
        
        # Verify with invalid hash format
        assert not HealthDataHelper.verify_medical_data_hash(data, "invalid_hash")
        assert not HealthDataHelper.verify_medical_data_hash(data, "no_colon_hash")
    
    def test_anonymize_patient_data(self):
        """Test patient data anonymization"""
        patient_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "age": 45,
            "gender": "male",
            "location": "New York, NY, USA",
            "conditions": ["hypertension"]
        }
        
        # High anonymization
        anonymized = HealthDataHelper.anonymize_patient_data(patient_data, "high")
        
        # Should remove direct identifiers
        assert "name" not in anonymized
        assert "email" not in anonymized
        assert "phone" not in anonymized
        
        # Should generalize age
        assert "age" not in anonymized
        assert "age_range" in anonymized
        assert anonymized["age_range"] == "30-49"
        
        # Should generalize location
        assert "location" not in anonymized
        if "region" in anonymized:
            assert "USA" in anonymized["region"]
        
        # Should preserve medical data
        assert anonymized["conditions"] == ["hypertension"]
        
        # Should add anonymization metadata
        assert "_anonymization" in anonymized
        assert anonymized["_anonymization"]["level"] == "high"
        assert anonymized["_anonymization"]["method"] == "k-anonymity"
    
    def test_anonymize_patient_data_age_ranges(self):
        """Test age range anonymization"""
        # Test different age ranges
        test_ages = [
            (15, "0-17"),
            (25, "18-29"),
            (35, "30-49"),
            (60, "50-69"),
            (75, "70+")
        ]
        
        for age, expected_range in test_ages:
            patient_data = {"age": age}
            anonymized = HealthDataHelper.anonymize_patient_data(patient_data, "high")
            assert anonymized["age_range"] == expected_range
    
    def test_private_methods(self):
        """Test private helper methods"""
        # Test _get_privacy_recommendations
        recommendations = HealthDataHelper._get_privacy_recommendations(50)
        assert len(recommendations) > 0
        assert any("encryption" in rec.lower() for rec in recommendations)
        
        recommendations = HealthDataHelper._get_privacy_recommendations(90)
        assert "well configured" in recommendations[0].lower()
        
        # Test _analyze_vital_trends
        vital_history = [
            {"blood_pressure_systolic": 120},
            {"blood_pressure_systolic": 130}
        ]
        trends = HealthDataHelper._analyze_vital_trends(vital_history)
        assert trends.get("blood_pressure") == "increasing"
        
        # Test _identify_risk_factors
        conditions = ["diabetes", "hypertension", "obesity"]
        risk_factors = HealthDataHelper._identify_risk_factors(conditions)
        assert len(risk_factors) >= 2  # Should identify multiple risk factors
        assert any("cardiovascular" in rf.lower() for rf in risk_factors)
        
        # Test _check_medication_interactions
        medications = ["amoxicillin", "aspirin"]
        allergies = ["penicillin", "aspirin"]
        alerts = HealthDataHelper._check_medication_interactions(medications, allergies)
        assert len(alerts) >= 1  # Should detect interactions
        assert any("amoxicillin" in alert and "penicillin" in alert for alert in alerts)
        assert any("aspirin" in alert for alert in alerts)
