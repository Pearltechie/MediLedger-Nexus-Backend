"""
Research schemas for MediLedger Nexus
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ResearchStudyBase(BaseModel):
    """Base research study schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    study_type: str = Field(..., min_length=1, max_length=100)
    objectives: List[str] = Field(..., min_items=1)
    data_requirements: List[str] = Field(..., min_items=1)
    duration_months: int = Field(..., ge=1, le=60)
    max_participants: int = Field(..., ge=1, le=10000)


class ResearchStudyCreate(ResearchStudyBase):
    """Research study creation schema"""
    principal_investigator: str = Field(..., min_length=1, max_length=255)
    institution: str = Field(..., min_length=1, max_length=255)
    funding_source: Optional[str] = None
    ethical_approval: bool = False


class ResearchStudyUpdate(BaseModel):
    """Research study update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    objectives: Optional[List[str]] = None
    data_requirements: Optional[List[str]] = None
    duration_months: Optional[int] = Field(None, ge=1, le=60)
    max_participants: Optional[int] = Field(None, ge=1, le=10000)
    status: Optional[str] = None


class ResearchStudyResponse(ResearchStudyBase):
    """Research study response schema"""
    id: int
    principal_investigator: str
    institution: str
    funding_source: Optional[str] = None
    ethical_approval: bool = False
    status: str = "active"
    participant_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ResearchParticipationRequest(BaseModel):
    """Research participation request schema"""
    study_id: int
    patient_id: str = Field(..., min_length=1, max_length=255)
    consent_given: bool = False
    data_types: List[str] = Field(..., min_items=1)
    participation_duration: Optional[int] = Field(None, ge=1, le=60)


class ResearchParticipationResponse(BaseModel):
    """Research participation response schema"""
    participation_id: str
    study_id: int
    patient_id: str
    status: str
    data_contribution: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None


class ResearchDataRequest(BaseModel):
    """Research data request schema"""
    study_id: int
    data_types: List[str] = Field(..., min_items=1)
    purpose: str = Field(..., min_length=1)
    anonymization_level: str = Field(..., min_length=1, max_length=50)
    retention_period: int = Field(..., ge=1, le=120)


class ResearchDataResponse(BaseModel):
    """Research data response schema"""
    request_id: str
    study_id: int
    data_available: bool
    data_hash: Optional[str] = None
    access_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str


class ResearchDatasetRequest(BaseModel):
    """Research dataset request schema"""
    study_id: int
    dataset_name: str = Field(..., min_length=1, max_length=255)
    data_types: List[str] = Field(..., min_items=1)
    anonymization_level: str = Field(..., min_length=1, max_length=50)
    quality_requirements: Optional[Dict[str, Any]] = None


class ResearchDatasetResponse(BaseModel):
    """Research dataset response schema"""
    dataset_id: str
    study_id: int
    dataset_name: str
    data_types: List[str]
    anonymization_level: str
    quality_requirements: Optional[Dict[str, Any]] = None
    created_at: datetime
    status: str = "processing"
