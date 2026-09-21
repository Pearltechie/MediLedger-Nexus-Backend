"""
Data formatting utilities for MediLedger Nexus
"""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date, timezone
from decimal import Decimal
import hashlib
import base64

from .constants import MEDICAL_CONSTANTS


class DataFormatter:
    """Comprehensive data formatting utilities"""
    
    @staticmethod
    def format_timestamp(dt: Optional[datetime] = None, include_timezone: bool = True) -> str:
        """Format datetime to ISO string"""
        if dt is None:
            dt = datetime.now(timezone.utc)
        
        if include_timezone and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt.isoformat()
    
    @staticmethod
    def format_date(d: Optional[date] = None) -> str:
        """Format date to ISO string"""
        if d is None:
            d = date.today()
        return d.isoformat()
    
    @staticmethod
    def format_hedera_account_id(account_id: str) -> str:
        """Ensure Hedera account ID is properly formatted"""
        # Remove any whitespace and ensure proper format
        account_id = account_id.strip()
        if not account_id.startswith('0.0.'):
            # Assume it's just the account number
            account_id = f"0.0.{account_id}"
        return account_id
    
    @staticmethod
    def format_phone_number(phone: str, country_code: str = "+1") -> str:
        """Format phone number to international format"""
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present
        if not phone.startswith('+'):
            if len(digits) == 10:  # US number without country code
                digits = f"1{digits}"
            phone = f"+{digits}"
        
        return phone
    
    @staticmethod
    def format_medical_record_id(user_id: str, record_type: str, timestamp: Optional[datetime] = None) -> str:
        """Generate formatted medical record ID"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
        record_type_short = record_type.upper()[:3]
        
        return f"MR_{user_id[:8]}_{record_type_short}_{timestamp_str}"
    
    @staticmethod
    def format_consent_id(user_id: str, provider_id: str, timestamp: Optional[datetime] = None) -> str:
        """Generate formatted consent ID"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
        
        return f"CNS_{user_id[:8]}_{provider_id[:8]}_{timestamp_str}"
    
    @staticmethod
    def format_ai_agent_id(agent_name: str, agent_type: str, user_id: str) -> str:
        """Generate formatted AI agent ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        agent_type_short = agent_type.upper()[:3]
        
        return f"AI_{agent_type_short}_{user_id[:8]}_{timestamp}"
    
    @staticmethod
    def format_vault_id(user_id: str, vault_name: str, timestamp: Optional[datetime] = None) -> str:
        """Generate formatted health vault ID"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
        vault_name_short = ''.join(filter(str.isalnum, vault_name))[:8].upper()
        
        return f"VLT_{user_id[:8]}_{vault_name_short}_{timestamp_str}"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def format_currency(amount: Union[float, Decimal], currency: str = "HEAL") -> str:
        """Format currency amount"""
        if isinstance(amount, Decimal):
            amount = float(amount)
        
        return f"{amount:.2f} {currency}"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 1) -> str:
        """Format percentage value"""
        return f"{value * 100:.{decimal_places}f}%"
    
    @staticmethod
    def format_vital_signs(vital_signs: Dict[str, float]) -> Dict[str, str]:
        """Format vital signs with units and status"""
        formatted = {}
        
        for vital_name, value in vital_signs.items():
            if vital_name.upper() in MEDICAL_CONSTANTS.VITALS:
                range_info = MEDICAL_CONSTANTS.VITALS[vital_name.upper()]
                unit = range_info["unit"]
                
                # Determine status
                if range_info["min"] <= value <= range_info["max"]:
                    status = "Normal"
                elif value < range_info["min"]:
                    status = "Low"
                else:
                    status = "High"
                
                formatted[vital_name] = {
                    "value": f"{value} {unit}",
                    "status": status,
                    "normal_range": f"{range_info['min']}-{range_info['max']} {unit}"
                }
            else:
                formatted[vital_name] = {"value": str(value), "status": "Unknown"}
        
        return formatted
    
    @staticmethod
    def format_lab_results(lab_results: Dict[str, float]) -> Dict[str, str]:
        """Format lab results with units and reference ranges"""
        formatted = {}
        
        for test_name, value in lab_results.items():
            if test_name.upper() in MEDICAL_CONSTANTS.LAB_RANGES:
                range_info = MEDICAL_CONSTANTS.LAB_RANGES[test_name.upper()]
                unit = range_info["unit"]
                
                # Determine status
                if range_info["min"] <= value <= range_info["max"]:
                    status = "Normal"
                elif value < range_info["min"]:
                    status = "Low"
                else:
                    status = "High"
                
                formatted[test_name] = {
                    "value": f"{value} {unit}",
                    "status": status,
                    "reference_range": f"{range_info['min']}-{range_info['max']} {unit}"
                }
            else:
                formatted[test_name] = {"value": str(value), "status": "Unknown"}
        
        return formatted
    
    @staticmethod
    def format_medical_history(history: Dict[str, Any]) -> Dict[str, Any]:
        """Format medical history for display"""
        formatted = {}
        
        # Format age
        if "age" in history:
            formatted["age"] = f"{history['age']} years old"
        
        # Format gender
        if "gender" in history:
            formatted["gender"] = history["gender"].title()
        
        # Format conditions
        if "conditions" in history and isinstance(history["conditions"], list):
            formatted["conditions"] = ", ".join(history["conditions"])
        
        # Format medications
        if "medications" in history and isinstance(history["medications"], list):
            formatted["medications"] = ", ".join(history["medications"])
        
        # Format allergies
        if "allergies" in history and isinstance(history["allergies"], list):
            formatted["allergies"] = ", ".join(history["allergies"])
        
        return formatted
    
    @staticmethod
    def format_diagnosis_result(diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Format AI diagnosis result for display"""
        formatted = {
            "diagnosis_id": diagnosis.get("diagnosis_id", ""),
            "timestamp": DataFormatter.format_timestamp(diagnosis.get("timestamp")),
            "primary_diagnosis": diagnosis.get("primary_diagnosis", ""),
            "confidence": DataFormatter.format_percentage(diagnosis.get("confidence", 0.0)),
            "severity": diagnosis.get("severity", "").title(),
            "urgency": diagnosis.get("urgency", "").title()
        }
        
        # Format differential diagnoses
        if "differential_diagnoses" in diagnosis:
            formatted["differential_diagnoses"] = [
                {
                    "condition": dd.get("condition", ""),
                    "confidence": DataFormatter.format_percentage(dd.get("confidence", 0.0))
                }
                for dd in diagnosis["differential_diagnoses"]
            ]
        
        # Format recommendations
        if "recommendations" in diagnosis:
            formatted["recommendations"] = diagnosis["recommendations"]
        
        return formatted
    
    @staticmethod
    def format_consent_summary(consent: Dict[str, Any]) -> Dict[str, Any]:
        """Format consent information for display"""
        formatted = {
            "consent_id": consent.get("id", ""),
            "provider": consent.get("provider_account_id", ""),
            "status": consent.get("status", "").title(),
            "granted_at": DataFormatter.format_timestamp(consent.get("granted_at")),
            "expires_at": DataFormatter.format_timestamp(consent.get("expires_at")),
            "compensation_rate": DataFormatter.format_currency(consent.get("compensation_rate", 0.0)),
            "purpose": consent.get("purpose", "")
        }
        
        # Format record types
        if "record_types" in consent and isinstance(consent["record_types"], list):
            formatted["record_types"] = ", ".join(consent["record_types"])
        
        return formatted
    
    @staticmethod
    def format_emergency_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
        """Format emergency profile for display"""
        formatted = {
            "blood_type": profile.get("blood_type", "Unknown"),
            "allergies": ", ".join(profile.get("allergies", [])),
            "medications": ", ".join(profile.get("current_medications", [])),
            "conditions": ", ".join(profile.get("medical_conditions", [])),
            "emergency_contact": profile.get("emergency_contact", {})
        }
        
        # Format emergency contact
        if formatted["emergency_contact"]:
            contact = formatted["emergency_contact"]
            formatted["emergency_contact_formatted"] = (
                f"{contact.get('name', 'Unknown')} "
                f"({contact.get('relationship', 'Unknown')}) - "
                f"{contact.get('phone', 'No phone')}"
            )
        
        return formatted
    
    @staticmethod
    def format_hcs10_message(message_type: str, payload: Dict[str, Any], 
                           sender_id: str, recipient_id: Optional[str] = None) -> Dict[str, Any]:
        """Format HCS-10 OpenConvAI message"""
        formatted = {
            "protocol_version": MEDICAL_CONSTANTS.HCS10["PROTOCOL_VERSION"],
            "message_type": message_type,
            "timestamp": DataFormatter.format_timestamp(),
            "sender_id": sender_id,
            "payload": payload
        }
        
        if recipient_id:
            formatted["recipient_id"] = recipient_id
        
        # Add message hash for integrity
        message_str = json.dumps(formatted, sort_keys=True)
        formatted["message_hash"] = hashlib.sha256(message_str.encode()).hexdigest()
        
        return formatted
    
    @staticmethod
    def format_federated_learning_round(round_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format federated learning round information"""
        formatted = {
            "round_id": round_info.get("round_id", ""),
            "study_type": round_info.get("study_type", "").replace("_", " ").title(),
            "participants": round_info.get("participant_count", 0),
            "status": round_info.get("status", "").title(),
            "started_at": DataFormatter.format_timestamp(round_info.get("started_at")),
            "model_accuracy": DataFormatter.format_percentage(round_info.get("model_accuracy", 0.0)),
            "privacy_budget": round_info.get("privacy_budget", 0.0)
        }
        
        return formatted
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove or replace unsafe characters
        import re
        
        # Keep only alphanumeric, dots, hyphens, and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
        
        # Ensure it doesn't start with a dot
        if sanitized.startswith('.'):
            sanitized = 'file' + sanitized
        
        # Limit length
        if len(sanitized) > 100:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:95] + ('.' + ext if ext else '')
        
        return sanitized
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """Mask sensitive data for logging/display"""
        if len(data) <= visible_chars:
            return mask_char * len(data)
        
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)
    
    @staticmethod
    def format_json_response(data: Any, status: str = "success", message: str = "") -> Dict[str, Any]:
        """Format standardized JSON API response"""
        response = {
            "status": status,
            "timestamp": DataFormatter.format_timestamp(),
            "data": data
        }
        
        if message:
            response["message"] = message
        
        return response
    
    @staticmethod
    def format_error_response(error: str, error_code: Optional[str] = None, 
                            details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format standardized error response"""
        response = {
            "status": "error",
            "timestamp": DataFormatter.format_timestamp(),
            "error": error
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        return response
