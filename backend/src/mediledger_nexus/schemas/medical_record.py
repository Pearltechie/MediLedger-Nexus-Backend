"""
Medical Record schemas for MediLedger Nexus
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
