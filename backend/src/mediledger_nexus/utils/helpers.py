"""
Health data helper utilities for MediLedger Nexus
"""

import json
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import uuid

from .constants import MEDICAL_CONSTANTS
from .validators import DataValidator
from .formatters import DataFormatter


class HealthDataHelper:
    """Helper utilities for health data processing"""
    
    @staticmethod
    def generate_secure_id(prefix: str = "", length: int = 32) -> str:
        """Generate cryptographically secure ID"""
        secure_random = secrets.token_hex(length // 2)
        if prefix:
            return f"{prefix}_{secure_random}"
        return secure_random
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID4"""
        return str(uuid.uuid4())
    
    @staticmethod
    def calculate_age(birth_date: Union[str, datetime]) -> int:
        """Calculate age from birth date"""
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        
        today = datetime.now()
        age = today.year - birth_date.year
        
        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age
    
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Union[float, str]]:
        """Calculate BMI and category"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        # Determine BMI category
        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 25:
            category = "Normal weight"
        elif 25 <= bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        
        return {
            "bmi": round(bmi, 1),
            "category": category
        }
    
    @staticmethod
    def assess_vital_signs_risk(vital_signs: Dict[str, float]) -> Dict[str, Any]:
        """Assess risk level based on vital signs"""
        risk_factors = []
        risk_score = 0
        
        for vital_name, value in vital_signs.items():
            if vital_name.upper() in MEDICAL_CONSTANTS.VITALS:
                range_info = MEDICAL_CONSTANTS.VITALS[vital_name.upper()]
                
                if value < range_info["min"]:
                    risk_factors.append(f"Low {vital_name}")
                    risk_score += 1
                elif value > range_info["max"]:
                    risk_factors.append(f"High {vital_name}")
                    risk_score += 2  # High values often more concerning
        
        # Determine overall risk level
        if risk_score == 0:
            risk_level = "Low"
        elif risk_score <= 2:
            risk_level = "Moderate"
        elif risk_score <= 4:
            risk_level = "High"
        else:
            risk_level = "Critical"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors
        }
    
    @staticmethod
    def categorize_medications(medications: List[str]) -> Dict[str, List[str]]:
        """Categorize medications by type"""
        categories = {category: [] for category in MEDICAL_CONSTANTS.MEDICATIONS.values()}
        uncategorized = []
        
        # Simple keyword-based categorization
        medication_keywords = {
            "cardiovascular": ["lisinopril", "metoprolol", "amlodipine", "atorvastatin", "warfarin"],
            "diabetes": ["metformin", "insulin", "glipizide", "januvia", "lantus"],
            "pain_management": ["ibuprofen", "acetaminophen", "tramadol", "morphine", "oxycodone"],
            "antibiotics": ["amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline"],
            "mental_health": ["sertraline", "fluoxetine", "lorazepam", "risperidone"],
            "respiratory": ["albuterol", "prednisone", "montelukast", "fluticasone"],
        }
        
        for medication in medications:
            medication_lower = medication.lower()
            categorized = False
            
            for category, keywords in medication_keywords.items():
                if any(keyword in medication_lower for keyword in keywords):
                    categories[category].append(medication)
                    categorized = True
                    break
            
            if not categorized:
                uncategorized.append(medication)
        
        # Remove empty categories
        categories = {k: v for k, v in categories.items() if v}
        
        if uncategorized:
            categories["uncategorized"] = uncategorized
        
        return categories
    
    @staticmethod
    def calculate_consent_earnings(duration_hours: int, rate_per_hour: float, 
                                 data_types: List[str]) -> Dict[str, Any]:
        """Calculate earnings from data consent"""
        base_earnings = duration_hours * rate_per_hour
        
        # Apply multipliers based on data sensitivity
        sensitivity_multipliers = {
            "genomics": 2.0,
            "mental_health": 1.8,
            "reproductive_health": 1.6,
            "imaging": 1.4,
            "lab_results": 1.2,
            "vital_signs": 1.0
        }
        
        total_multiplier = 1.0
        for data_type in data_types:
            multiplier = sensitivity_multipliers.get(data_type, 1.0)
            total_multiplier = max(total_multiplier, multiplier)
        
        final_earnings = base_earnings * total_multiplier
        
        return {
            "base_earnings": round(base_earnings, 2),
            "sensitivity_multiplier": total_multiplier,
            "final_earnings": round(final_earnings, 2),
            "currency": "HEAL"
        }
    
    @staticmethod
    def generate_emergency_summary(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate emergency medical summary"""
        summary = {
            "critical_info": {},
            "allergies": patient_data.get("allergies", []),
            "current_medications": patient_data.get("medications", []),
            "medical_conditions": patient_data.get("conditions", []),
            "emergency_contact": patient_data.get("emergency_contact", {}),
            "last_updated": DataFormatter.format_timestamp()
        }
        
        # Extract critical information
        if "blood_type" in patient_data:
            summary["critical_info"]["blood_type"] = patient_data["blood_type"]
        
        if "vital_signs" in patient_data:
            risk_assessment = HealthDataHelper.assess_vital_signs_risk(patient_data["vital_signs"])
            summary["critical_info"]["vital_signs_risk"] = risk_assessment["risk_level"]
        
        # Identify high-priority allergies
        critical_allergies = []
        for allergy in summary["allergies"]:
            if any(critical in allergy.lower() for critical in ["penicillin", "latex", "anesthesia"]):
                critical_allergies.append(allergy)
        
        if critical_allergies:
            summary["critical_info"]["critical_allergies"] = critical_allergies
        
        return summary
    
    @staticmethod
    def calculate_privacy_score(data_types: List[str], sharing_scope: str, 
                              encryption_level: str) -> Dict[str, Any]:
        """Calculate privacy score for data sharing"""
        base_score = 100
        
        # Deduct points based on data sensitivity
        sensitivity_penalties = {
            "genomics": 30,
            "mental_health": 25,
            "reproductive_health": 20,
            "financial": 20,
            "imaging": 15,
            "lab_results": 10,
            "vital_signs": 5,
            "demographics": 5
        }
        
        for data_type in data_types:
            penalty = sensitivity_penalties.get(data_type, 0)
            base_score -= penalty
        
        # Adjust based on sharing scope
        scope_multipliers = {
            "individual": 1.0,
            "institution": 0.9,
            "research": 0.8,
            "public": 0.6
        }
        
        scope_multiplier = scope_multipliers.get(sharing_scope, 0.8)
        base_score *= scope_multiplier
        
        # Adjust based on encryption level
        encryption_bonuses = {
            "maximum": 1.1,
            "high": 1.05,
            "medium": 1.0,
            "low": 0.9
        }
        
        encryption_bonus = encryption_bonuses.get(encryption_level, 1.0)
        final_score = base_score * encryption_bonus
        
        # Ensure score is between 0 and 100
        final_score = max(0, min(100, final_score))
        
        return {
            "privacy_score": round(final_score, 1),
            "level": "High" if final_score >= 80 else "Medium" if final_score >= 60 else "Low",
            "recommendations": HealthDataHelper._get_privacy_recommendations(final_score)
        }
    
    @staticmethod
    def _get_privacy_recommendations(score: float) -> List[str]:
        """Get privacy improvement recommendations"""
        recommendations = []
        
        if score < 60:
            recommendations.extend([
                "Consider reducing the scope of data sharing",
                "Enable maximum encryption level",
                "Limit sharing of sensitive data types"
            ])
        elif score < 80:
            recommendations.extend([
                "Consider upgrading encryption level",
                "Review data types being shared"
            ])
        else:
            recommendations.append("Privacy settings are well configured")
        
        return recommendations
    
    @staticmethod
    def generate_health_insights(medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate health insights from medical data"""
        insights = {
            "risk_factors": [],
            "recommendations": [],
            "trends": {},
            "alerts": []
        }
        
        # Analyze vital signs trends
        if "vital_signs_history" in medical_data:
            trends = HealthDataHelper._analyze_vital_trends(medical_data["vital_signs_history"])
            insights["trends"].update(trends)
        
        # Identify risk factors
        if "conditions" in medical_data:
            risk_factors = HealthDataHelper._identify_risk_factors(medical_data["conditions"])
            insights["risk_factors"].extend(risk_factors)
        
        # Generate recommendations
        if "medications" in medical_data and "allergies" in medical_data:
            med_alerts = HealthDataHelper._check_medication_interactions(
                medical_data["medications"], medical_data["allergies"]
            )
            insights["alerts"].extend(med_alerts)
        
        return insights
    
    @staticmethod
    def _analyze_vital_trends(vital_history: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze trends in vital signs"""
        trends = {}
        
        if len(vital_history) < 2:
            return trends
        
        # Simple trend analysis for blood pressure
        bp_systolic_values = [v.get("blood_pressure_systolic") for v in vital_history if v.get("blood_pressure_systolic")]
        
        if len(bp_systolic_values) >= 2:
            if bp_systolic_values[-1] > bp_systolic_values[-2]:
                trends["blood_pressure"] = "increasing"
            elif bp_systolic_values[-1] < bp_systolic_values[-2]:
                trends["blood_pressure"] = "decreasing"
            else:
                trends["blood_pressure"] = "stable"
        
        return trends
    
    @staticmethod
    def _identify_risk_factors(conditions: List[str]) -> List[str]:
        """Identify cardiovascular and other risk factors"""
        risk_factors = []
        
        high_risk_conditions = {
            "diabetes": "Increased cardiovascular risk",
            "hypertension": "High blood pressure increases heart disease risk",
            "obesity": "Weight management recommended",
            "smoking": "Smoking cessation strongly recommended"
        }
        
        for condition in conditions:
            condition_lower = condition.lower()
            for risk_condition, description in high_risk_conditions.items():
                if risk_condition in condition_lower:
                    risk_factors.append(description)
        
        return risk_factors
    
    @staticmethod
    def _check_medication_interactions(medications: List[str], allergies: List[str]) -> List[str]:
        """Check for potential medication-allergy interactions"""
        alerts = []
        
        allergy_medications = {
            "penicillin": ["amoxicillin", "ampicillin", "penicillin"],
            "sulfa": ["sulfamethoxazole", "trimethoprim"],
            "aspirin": ["aspirin", "salicylate"]
        }
        
        for allergy in allergies:
            allergy_lower = allergy.lower()
            for allergy_type, contraindicated_meds in allergy_medications.items():
                if allergy_type in allergy_lower:
                    for medication in medications:
                        medication_lower = medication.lower()
                        for contraindicated in contraindicated_meds:
                            if contraindicated in medication_lower:
                                alerts.append(f"Potential allergy interaction: {medication} with {allergy} allergy")
        
        return alerts
    
    @staticmethod
    def hash_medical_data(data: Dict[str, Any], salt: Optional[str] = None) -> str:
        """Create hash of medical data for integrity verification"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Convert data to canonical JSON string
        data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # Create hash with salt
        hash_input = f"{salt}{data_str}".encode('utf-8')
        data_hash = hashlib.sha256(hash_input).hexdigest()
        
        return f"{salt}:{data_hash}"
    
    @staticmethod
    def verify_medical_data_hash(data: Dict[str, Any], hash_with_salt: str) -> bool:
        """Verify medical data integrity using hash"""
        try:
            salt, expected_hash = hash_with_salt.split(':', 1)
            calculated_hash = HealthDataHelper.hash_medical_data(data, salt)
            return calculated_hash == hash_with_salt
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def anonymize_patient_data(patient_data: Dict[str, Any], 
                             anonymization_level: str = "high") -> Dict[str, Any]:
        """Anonymize patient data for research purposes"""
        anonymized = patient_data.copy()
        
        # Remove direct identifiers
        identifiers_to_remove = [
            "name", "full_name", "email", "phone", "address", 
            "ssn", "patient_id", "account_id"
        ]
        
        for identifier in identifiers_to_remove:
            anonymized.pop(identifier, None)
        
        # Generalize quasi-identifiers based on anonymization level
        if anonymization_level in ["high", "maximum"]:
            # Generalize age to age ranges
            if "age" in anonymized:
                age = anonymized["age"]
                if age < 18:
                    anonymized["age_range"] = "0-17"
                elif age < 30:
                    anonymized["age_range"] = "18-29"
                elif age < 50:
                    anonymized["age_range"] = "30-49"
                elif age < 70:
                    anonymized["age_range"] = "50-69"
                else:
                    anonymized["age_range"] = "70+"
                del anonymized["age"]
            
            # Generalize location to region/state only
            if "location" in anonymized:
                # Keep only state/region level information
                location_parts = anonymized["location"].split(",")
                if len(location_parts) > 1:
                    anonymized["region"] = location_parts[-1].strip()
                del anonymized["location"]
        
        # Add anonymization metadata
        anonymized["_anonymization"] = {
            "level": anonymization_level,
            "timestamp": DataFormatter.format_timestamp(),
            "method": "k-anonymity"
        }
        
        return anonymized
