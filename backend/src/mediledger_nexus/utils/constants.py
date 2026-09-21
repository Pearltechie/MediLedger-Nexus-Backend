"""
Medical and system constants for MediLedger Nexus
"""

from typing import Dict, List, Set

# Medical Record Types
MEDICAL_RECORD_TYPES = {
    "LAB_RESULTS": "lab_results",
    "IMAGING": "imaging", 
    "PRESCRIPTIONS": "prescriptions",
    "ALLERGIES": "allergies",
    "IMMUNIZATIONS": "immunizations",
    "VITAL_SIGNS": "vital_signs",
    "PROCEDURES": "procedures",
    "DIAGNOSES": "diagnoses",
    "GENOMICS": "genomics",
    "PATHOLOGY": "pathology"
}

# Blood Types
BLOOD_TYPES = {
    "A_POSITIVE": "A+",
    "A_NEGATIVE": "A-",
    "B_POSITIVE": "B+", 
    "B_NEGATIVE": "B-",
    "AB_POSITIVE": "AB+",
    "AB_NEGATIVE": "AB-",
    "O_POSITIVE": "O+",
    "O_NEGATIVE": "O-"
}

# Common Allergies
COMMON_ALLERGIES = {
    "penicillin", "aspirin", "ibuprofen", "codeine", "morphine",
    "latex", "peanuts", "shellfish", "eggs", "milk", "soy",
    "wheat", "tree_nuts", "fish", "sesame", "sulfa_drugs",
    "contrast_dye", "anesthesia", "bee_stings", "pollen"
}

# Emergency Contact Types
EMERGENCY_CONTACT_TYPES = {
    "SPOUSE": "spouse",
    "PARENT": "parent",
    "CHILD": "child",
    "SIBLING": "sibling",
    "FRIEND": "friend",
    "GUARDIAN": "guardian",
    "OTHER": "other"
}

# User Types
USER_TYPES = {
    "PATIENT": "patient",
    "PROVIDER": "provider", 
    "RESEARCHER": "researcher",
    "ADMIN": "admin",
    "AI_AGENT": "ai_agent"
}

# Consent Status
CONSENT_STATUS = {
    "PENDING": "pending",
    "ACTIVE": "active",
    "EXPIRED": "expired",
    "REVOKED": "revoked",
    "SUSPENDED": "suspended"
}

# AI Agent Types
AI_AGENT_TYPES = {
    "DIAGNOSTIC": "diagnostic_agent",
    "RESEARCH": "research_agent",
    "EMERGENCY": "emergency_agent",
    "FEDERATED_LEARNING": "federated_learning_agent",
    "CONSENT_MANAGER": "consent_manager_agent"
}

# Federated Learning Study Types
FL_STUDY_TYPES = {
    "CARDIOVASCULAR": "cardiovascular_disease",
    "DIABETES": "diabetes_management",
    "CANCER": "cancer_research",
    "MENTAL_HEALTH": "mental_health",
    "INFECTIOUS_DISEASE": "infectious_disease",
    "RARE_DISEASE": "rare_disease",
    "DRUG_DISCOVERY": "drug_discovery",
    "GENOMICS": "genomics_research"
}

# Privacy Levels
PRIVACY_LEVELS = {
    "LOW": "low",
    "MEDIUM": "medium", 
    "HIGH": "high",
    "MAXIMUM": "maximum"
}

# Urgency Levels
URGENCY_LEVELS = {
    "LOW": "low",
    "MODERATE": "moderate",
    "HIGH": "high", 
    "CRITICAL": "critical",
    "EMERGENCY": "emergency"
}

# File Extensions
ALLOWED_MEDICAL_FILE_EXTENSIONS = {
    ".pdf", ".dcm", ".fastq", ".json", ".xml", ".hl7",
    ".jpg", ".jpeg", ".png", ".tiff", ".bmp",
    ".txt", ".csv", ".xlsx", ".doc", ".docx"
}

# Maximum File Sizes (in bytes)
MAX_FILE_SIZES = {
    "DOCUMENT": 50 * 1024 * 1024,  # 50MB
    "IMAGE": 100 * 1024 * 1024,    # 100MB
    "GENOMIC": 500 * 1024 * 1024,  # 500MB
    "DEFAULT": 50 * 1024 * 1024    # 50MB
}

# Encryption Constants
ENCRYPTION_CONSTANTS = {
    "AES_KEY_SIZE": 256,
    "RSA_KEY_SIZE": 2048,
    "PBKDF2_ITERATIONS": 100000,
    "SALT_SIZE": 32,
    "IV_SIZE": 16
}

# Hedera Network Constants
HEDERA_CONSTANTS = {
    "TESTNET": {
        "NETWORK": "testnet",
        "MIRROR_NODE": "https://testnet.mirrornode.hedera.com",
        "CONSENSUS_NODES": ["0.testnet.hedera.com:50211"]
    },
    "MAINNET": {
        "NETWORK": "mainnet", 
        "MIRROR_NODE": "https://mainnet-public.mirrornode.hedera.com",
        "CONSENSUS_NODES": ["0.mainnet.hedera.com:50211"]
    }
}

# HCS-10 OpenConvAI Constants
HCS10_CONSTANTS = {
    "PROTOCOL_VERSION": "1.0",
    "MESSAGE_TYPES": {
        "REGISTER": "register",
        "DELETE": "delete", 
        "CONNECTION_REQUEST": "connection_request",
        "CONNECTION_CREATED": "connection_created",
        "MESSAGE": "message",
        "TRANSACTION": "transaction"
    },
    "TOPIC_TYPES": {
        "REGISTRY": 3,
        "INBOUND": 0,
        "OUTBOUND": 1,
        "CONNECTION": 2
    }
}

# API Rate Limits
RATE_LIMITS = {
    "DEFAULT": 100,  # requests per minute
    "AUTH": 10,      # login attempts per minute
    "UPLOAD": 20,    # file uploads per minute
    "AI_DIAGNOSIS": 5,  # AI requests per minute
    "EMERGENCY": 1000   # emergency requests per minute
}

# Cache TTL (Time To Live) in seconds
CACHE_TTL = {
    "USER_SESSION": 3600,      # 1 hour
    "HEALTH_INSIGHTS": 7200,   # 2 hours
    "CONSENT_STATUS": 300,     # 5 minutes
    "AI_DIAGNOSIS": 86400,     # 24 hours
    "EMERGENCY_PROFILE": 60    # 1 minute
}

# Medical Specialties
MEDICAL_SPECIALTIES = {
    "CARDIOLOGY": "cardiology",
    "NEUROLOGY": "neurology",
    "ONCOLOGY": "oncology",
    "ENDOCRINOLOGY": "endocrinology",
    "INFECTIOUS_DISEASE": "infectious_disease",
    "PSYCHIATRY": "psychiatry",
    "RADIOLOGY": "radiology",
    "PATHOLOGY": "pathology",
    "EMERGENCY_MEDICINE": "emergency_medicine",
    "FAMILY_MEDICINE": "family_medicine",
    "INTERNAL_MEDICINE": "internal_medicine",
    "PEDIATRICS": "pediatrics",
    "OBSTETRICS_GYNECOLOGY": "obstetrics_gynecology",
    "SURGERY": "surgery",
    "ANESTHESIOLOGY": "anesthesiology"
}

# Vital Signs Normal Ranges
VITAL_SIGNS_RANGES = {
    "BLOOD_PRESSURE_SYSTOLIC": {"min": 90, "max": 140, "unit": "mmHg"},
    "BLOOD_PRESSURE_DIASTOLIC": {"min": 60, "max": 90, "unit": "mmHg"},
    "HEART_RATE": {"min": 60, "max": 100, "unit": "bpm"},
    "TEMPERATURE": {"min": 97.0, "max": 99.5, "unit": "°F"},
    "RESPIRATORY_RATE": {"min": 12, "max": 20, "unit": "breaths/min"},
    "OXYGEN_SATURATION": {"min": 95, "max": 100, "unit": "%"}
}

# Lab Test Reference Ranges
LAB_REFERENCE_RANGES = {
    "GLUCOSE": {"min": 70, "max": 100, "unit": "mg/dL", "fasting": True},
    "HBA1C": {"min": 4.0, "max": 5.6, "unit": "%"},
    "CHOLESTEROL_TOTAL": {"min": 0, "max": 200, "unit": "mg/dL"},
    "HDL_CHOLESTEROL": {"min": 40, "max": 999, "unit": "mg/dL"},
    "LDL_CHOLESTEROL": {"min": 0, "max": 100, "unit": "mg/dL"},
    "TRIGLYCERIDES": {"min": 0, "max": 150, "unit": "mg/dL"},
    "CREATININE": {"min": 0.6, "max": 1.3, "unit": "mg/dL"},
    "BUN": {"min": 7, "max": 20, "unit": "mg/dL"}
}

# Medication Categories
MEDICATION_CATEGORIES = {
    "CARDIOVASCULAR": "cardiovascular",
    "DIABETES": "diabetes",
    "PAIN_MANAGEMENT": "pain_management",
    "ANTIBIOTICS": "antibiotics",
    "MENTAL_HEALTH": "mental_health",
    "RESPIRATORY": "respiratory",
    "GASTROINTESTINAL": "gastrointestinal",
    "HORMONAL": "hormonal",
    "IMMUNOSUPPRESSIVE": "immunosuppressive",
    "ONCOLOGY": "oncology"
}

# Diagnostic Confidence Levels
DIAGNOSTIC_CONFIDENCE = {
    "VERY_LOW": 0.0,
    "LOW": 0.25,
    "MODERATE": 0.5,
    "HIGH": 0.75,
    "VERY_HIGH": 0.9,
    "CERTAIN": 1.0
}

class MEDICAL_CONSTANTS:
    """Container for all medical constants"""
    
    RECORD_TYPES = MEDICAL_RECORD_TYPES
    BLOOD_TYPES = BLOOD_TYPES
    ALLERGIES = COMMON_ALLERGIES
    EMERGENCY_CONTACTS = EMERGENCY_CONTACT_TYPES
    USER_TYPES = USER_TYPES
    CONSENT_STATUS = CONSENT_STATUS
    AI_AGENTS = AI_AGENT_TYPES
    FL_STUDIES = FL_STUDY_TYPES
    PRIVACY = PRIVACY_LEVELS
    URGENCY = URGENCY_LEVELS
    FILE_EXTENSIONS = ALLOWED_MEDICAL_FILE_EXTENSIONS
    FILE_SIZES = MAX_FILE_SIZES
    ENCRYPTION = ENCRYPTION_CONSTANTS
    HEDERA = HEDERA_CONSTANTS
    HCS10 = HCS10_CONSTANTS
    RATES = RATE_LIMITS
    CACHE = CACHE_TTL
    SPECIALTIES = MEDICAL_SPECIALTIES
    VITALS = VITAL_SIGNS_RANGES
    LAB_RANGES = LAB_REFERENCE_RANGES
    MEDICATIONS = MEDICATION_CATEGORIES
    CONFIDENCE = DIAGNOSTIC_CONFIDENCE
