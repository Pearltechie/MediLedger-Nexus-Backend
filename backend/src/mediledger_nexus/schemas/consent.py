"""
Consent schemas for MediLedger Nexus
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ConsentBase(BaseModel):
    """Base consent schema"""
    patient_id: str = Field(..., min_length=1, max_length=255)
    consent_type: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=1)
    data_types: Optional[List[str]] = None
    recipients: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class ConsentCreate(ConsentBase):
    """Consent creation schema"""
    granted: bool = False
    zk_proof: Optional[str] = None
    consent_metadata: Optional[Dict[str, Any]] = None


class ConsentUpdate(BaseModel):
    """Consent update schema"""
    granted: Optional[bool] = None
    purpose: Optional[str] = Field(None, min_length=1)
    data_types: Optional[List[str]] = None
    recipients: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    zk_proof: Optional[str] = None
    consent_metadata: Optional[Dict[str, Any]] = None


class ConsentResponse(ConsentBase):
    """Consent response schema"""
    id: int
    granted: bool
    zk_proof: Optional[str] = None
    consent_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    health_vault_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class ConsentList(BaseModel):
    """Consent list response schema"""
    consents: List[ConsentResponse]
    total: int
    page: int
    size: int


class ConsentRevoke(BaseModel):
    """Consent revocation schema"""
    consent_id: int
    reason: str = Field(..., min_length=1)
    revoked_by: str = Field(..., min_length=1)
