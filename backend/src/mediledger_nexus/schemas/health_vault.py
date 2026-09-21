"""
Health Vault schemas for MediLedger Nexus
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class HealthVaultBase(BaseModel):
    """Base health vault schema"""
    patient_id: str = Field(..., min_length=1, max_length=255)
    vault_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True


class HealthVaultCreate(HealthVaultBase):
    """Health vault creation schema"""
    pass


class HealthVaultUpdate(BaseModel):
    """Health vault update schema"""
    vault_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class HealthVaultResponse(HealthVaultBase):
    """Health vault response schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class HealthVaultList(BaseModel):
    """Health vault list response schema"""
    vaults: List[HealthVaultResponse]
    total: int
    page: int
    size: int


class VaultAccessRequest(BaseModel):
    """Vault access request schema"""
    vault_id: int
    access_type: str = Field(..., min_length=1, max_length=50)
    purpose: str = Field(..., min_length=1)
    duration_hours: Optional[int] = Field(None, ge=1, le=24)


class VaultAccessResponse(BaseModel):
    """Vault access response schema"""
    access_granted: bool
    access_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str
