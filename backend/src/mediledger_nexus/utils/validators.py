"""
Data validation utilities for MediLedger Nexus
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, field_validator

from .constants import MEDICAL_CONSTANTS


class DataValidator:
    """Comprehensive data validation utilities"""
    
    @staticmethod
    def validate_email_address(email: str) -> bool:
        """Validate email address format"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod
    def validate_hedera_account_id(account_id: str) -> bool:
        """Validate Hedera account ID format (0.0.123456)"""
        pattern = r'^0\.0\.\d+$'
        return bool(re.match(pattern, account_id))
    
    @staticmethod
    def validate_hedera_topic_id(topic_id: str) -> bool:
        """Validate Hedera topic ID format"""
        pattern = r'^0\.0\.\d+$'
        return bool(re.match(pattern, topic_id))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Union[bool, List[str]]]:
        """Validate password strength and return detailed feedback"""
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            issues.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format (international format)"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it's a valid international format (7-15 digits)
        return 7 <= len(digits_only) <= 15
    
    @staticmethod
    def validate_blood_type(blood_type: str) -> bool:
        """Validate blood type"""
        return blood_type in MEDICAL_CONSTANTS.BLOOD_TYPES.values()
    
    @staticmethod
    def validate_medical_record_type(record_type: str) -> bool:
        """Validate medical record type"""
        return record_type in MEDICAL_CONSTANTS.RECORD_TYPES.values()
    
    @staticmethod
    def validate_user_type(user_type: str) -> bool:
        """Validate user type"""
        return user_type in MEDICAL_CONSTANTS.USER_TYPES.values()
    
    @staticmethod
    def validate_consent_status(status: str) -> bool:
        """Validate consent status"""
        return status in MEDICAL_CONSTANTS.CONSENT_STATUS.values()
    
    @staticmethod
    def validate_ai_agent_type(agent_type: str) -> bool:
        """Validate AI agent type"""
        return agent_type in MEDICAL_CONSTANTS.AI_AGENTS.values()
    
    @staticmethod
    def validate_privacy_level(privacy_level: str) -> bool:
        """Validate privacy level"""
        return privacy_level in MEDICAL_CONSTANTS.PRIVACY.values()
    
    @staticmethod
    def validate_urgency_level(urgency_level: str) -> bool:
        """Validate urgency level"""
        return urgency_level in MEDICAL_CONSTANTS.URGENCY.values()
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file extension for medical files"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return f".{extension}" in MEDICAL_CONSTANTS.FILE_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file_size: int, file_type: str = "DEFAULT") -> bool:
        """Validate file size against limits"""
        max_size = MEDICAL_CONSTANTS.FILE_SIZES.get(file_type.upper(), 
                                                   MEDICAL_CONSTANTS.FILE_SIZES["DEFAULT"])
        return file_size <= max_size
    
    @staticmethod
    def validate_vital_signs(vital_signs: Dict[str, float]) -> Dict[str, Union[bool, List[str]]]:
        """Validate vital signs against normal ranges"""
        issues = []
        
        for vital_name, value in vital_signs.items():
            if vital_name.upper() in MEDICAL_CONSTANTS.VITALS:
                range_info = MEDICAL_CONSTANTS.VITALS[vital_name.upper()]
                if not (range_info["min"] <= value <= range_info["max"]):
                    issues.append(
                        f"{vital_name} ({value} {range_info['unit']}) is outside "
                        f"normal range ({range_info['min']}-{range_info['max']} {range_info['unit']})"
                    )
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }
    
    @staticmethod
    def validate_lab_results(lab_results: Dict[str, float]) -> Dict[str, Union[bool, List[str]]]:
        """Validate lab results against reference ranges"""
        issues = []
        
        for test_name, value in lab_results.items():
            if test_name.upper() in MEDICAL_CONSTANTS.LAB_RANGES:
                range_info = MEDICAL_CONSTANTS.LAB_RANGES[test_name.upper()]
                if not (range_info["min"] <= value <= range_info["max"]):
                    issues.append(
                        f"{test_name} ({value} {range_info['unit']}) is outside "
                        f"reference range ({range_info['min']}-{range_info['max']} {range_info['unit']})"
                    )
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }
    
    @staticmethod
    def validate_age(birth_date: Union[str, date, datetime]) -> Dict[str, Union[bool, int, str]]:
        """Validate and calculate age from birth date"""
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            elif isinstance(birth_date, datetime):
                birth_date = birth_date.date()
            
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 0:
                return {"is_valid": False, "error": "Birth date cannot be in the future"}
            
            if age > 150:
                return {"is_valid": False, "error": "Age cannot exceed 150 years"}
            
            return {"is_valid": True, "age": age}
            
        except ValueError as e:
            return {"is_valid": False, "error": f"Invalid date format: {str(e)}"}
    
    @staticmethod
    def validate_medication_name(medication: str) -> bool:
        """Basic validation for medication names"""
        # Check if medication name contains only valid characters
        pattern = r'^[a-zA-Z0-9\s\-\.]+$'
        return bool(re.match(pattern, medication)) and len(medication.strip()) > 0
    
    @staticmethod
    def validate_allergy_list(allergies: List[str]) -> Dict[str, Union[bool, List[str]]]:
        """Validate list of allergies"""
        issues = []
        valid_allergies = []
        
        for allergy in allergies:
            allergy = allergy.strip().lower()
            if not allergy:
                issues.append("Empty allergy entry found")
                continue
            
            # Check if it's a common known allergy
            if allergy in MEDICAL_CONSTANTS.ALLERGIES:
                valid_allergies.append(allergy)
            else:
                # Allow custom allergies but validate format
                if re.match(r'^[a-zA-Z0-9\s\-\.]+$', allergy):
                    valid_allergies.append(allergy)
                else:
                    issues.append(f"Invalid allergy format: {allergy}")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "valid_allergies": valid_allergies
        }
    
    @staticmethod
    def validate_emergency_contact(contact_info: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
        """Validate emergency contact information"""
        issues = []
        required_fields = ["name", "phone", "relationship"]
        
        for field in required_fields:
            if field not in contact_info or not contact_info[field]:
                issues.append(f"Missing required field: {field}")
        
        if "phone" in contact_info and contact_info["phone"]:
            if not DataValidator.validate_phone_number(contact_info["phone"]):
                issues.append("Invalid phone number format")
        
        if "relationship" in contact_info and contact_info["relationship"]:
            if contact_info["relationship"] not in MEDICAL_CONSTANTS.EMERGENCY_CONTACTS.values():
                issues.append("Invalid emergency contact relationship")
        
        if "email" in contact_info and contact_info["email"]:
            if not DataValidator.validate_email_address(contact_info["email"]):
                issues.append("Invalid email address format")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }
    
    @staticmethod
    def validate_consent_duration(duration_hours: int) -> bool:
        """Validate consent duration"""
        # Consent duration should be between 1 hour and 1 year
        return 1 <= duration_hours <= (365 * 24)
    
    @staticmethod
    def validate_compensation_rate(rate: float) -> bool:
        """Validate compensation rate for data sharing"""
        # Rate should be between 0 and 1000 HEAL tokens per hour
        return 0.0 <= rate <= 1000.0
    
    @staticmethod
    def validate_diagnostic_confidence(confidence: float) -> bool:
        """Validate diagnostic confidence score"""
        return 0.0 <= confidence <= 1.0
    
    @staticmethod
    def validate_hcs10_message_type(message_type: str) -> bool:
        """Validate HCS-10 message type"""
        return message_type in MEDICAL_CONSTANTS.HCS10["MESSAGE_TYPES"].values()
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Union[bool, List[str]]]:
        """Validate JSON structure has required fields"""
        issues = []
        
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
            elif data[field] is None:
                issues.append(f"Field '{field}' cannot be null")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }


class MedicalDataValidator(BaseModel):
    """Pydantic-based medical data validator"""
    
    email: Optional[str] = None
    hedera_account_id: Optional[str] = None
    blood_type: Optional[str] = None
    phone: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and not DataValidator.validate_email_address(v):
            raise ValueError('Invalid email address')
        return v
    
    @field_validator('hedera_account_id')
    @classmethod
    def validate_hedera_account(cls, v):
        if v and not DataValidator.validate_hedera_account_id(v):
            raise ValueError('Invalid Hedera account ID format')
        return v
    
    @field_validator('blood_type')
    @classmethod
    def validate_blood_type(cls, v):
        if v and not DataValidator.validate_blood_type(v):
            raise ValueError('Invalid blood type')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not DataValidator.validate_phone_number(v):
            raise ValueError('Invalid phone number format')
        return v
