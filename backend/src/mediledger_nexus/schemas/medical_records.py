"""
Medical Records schemas for MediLedger Nexus
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class MedicalRecordBase(BaseModel):
    """Base medical record schema"""
    patient_id: str = Field(..., min_length=1, max_length=255)
    record_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    record_metadata: Optional[Dict[str, Any]] = None


class MedicalRecordCreate(MedicalRecordBase):
    """Medical record creation schema"""
    encrypted_data: str = Field(..., min_length=1)
    data_hash: str = Field(..., min_length=64, max_length=64)


class MedicalRecordUpdate(BaseModel):
    """Medical record update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    record_metadata: Optional[Dict[str, Any]] = None


class MedicalRecordResponse(MedicalRecordBase):
    """Medical record response schema"""
    id: int
    encrypted_data: str
    data_hash: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    health_vault_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class MedicalRecordList(BaseModel):
    """Medical record list response schema"""
    records: List[MedicalRecordResponse]
    total: int
    page: int
    size: int


class MedicalRecordSearch(BaseModel):
    """Medical record search schema"""
    patient_id: Optional[str] = None
    record_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    keywords: Optional[List[str]] = None


class RecordAccessRequest(BaseModel):
    """Record access request schema"""
    record_id: int
    access_type: str = Field(..., min_length=1, max_length=50)
    purpose: str = Field(..., min_length=1)
    duration_hours: Optional[int] = Field(None, ge=1, le=24)


class RecordAccessResponse(BaseModel):
    """Record access response schema"""
    access_granted: bool
    access_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str


class RecordShareRequest(BaseModel):
    """Record sharing request schema"""
    record_id: int
    recipient_id: str = Field(..., min_length=1)
    share_type: str = Field(..., min_length=1, max_length=50)
    purpose: str = Field(..., min_length=1)
    expires_at: Optional[datetime] = None


class RecordShareResponse(BaseModel):
    """Record sharing response schema"""
    share_granted: bool
    share_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str
