"""
Emergency schemas for MediLedger Nexus
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EmergencyContactBase(BaseModel):
    """Base emergency contact schema"""
    name: str = Field(..., min_length=1, max_length=255)
    relationship: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = None


class EmergencyContactCreate(EmergencyContactBase):
    """Emergency contact creation schema"""
    patient_id: str = Field(..., min_length=1, max_length=255)


class EmergencyContactUpdate(BaseModel):
    """Emergency contact update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    relationship: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = None


class EmergencyContactResponse(EmergencyContactBase):
    """Emergency contact response schema"""
    id: int
    patient_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EmergencyAccessRequest(BaseModel):
    """Emergency access request schema"""
    patient_id: str = Field(..., min_length=1, max_length=255)
    emergency_type: str = Field(..., min_length=1, max_length=100)
    requester_id: str = Field(..., min_length=1, max_length=255)
    requester_role: str = Field(..., min_length=1, max_length=100)
    justification: str = Field(..., min_length=1)
    urgency_level: int = Field(..., ge=1, le=5)


class EmergencyAccessResponse(BaseModel):
    """Emergency access response schema"""
    access_granted: bool
    access_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str
    emergency_contacts: Optional[List[EmergencyContactResponse]] = None


class EmergencyAlert(BaseModel):
    """Emergency alert schema"""
    patient_id: str = Field(..., min_length=1, max_length=255)
    alert_type: str = Field(..., min_length=1, max_length=100)
    severity: int = Field(..., ge=1, le=5)
    message: str = Field(..., min_length=1)
    location: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EmergencyAlertResponse(BaseModel):
    """Emergency alert response schema"""
    alert_id: str
    status: str
    message: str
    timestamp: datetime


class EmergencyProfileUpdate(BaseModel):
    """Emergency profile update schema"""
    emergency_contacts: Optional[List[EmergencyContactCreate]] = None
    medical_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    blood_type: Optional[str] = None
    insurance_info: Optional[Dict[str, Any]] = None
