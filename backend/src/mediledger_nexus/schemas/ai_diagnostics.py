"""
AI Diagnostics schemas for MediLedger Nexus
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class DiagnosticRequest(BaseModel):
    """Request for AI diagnosis"""
    symptoms: List[str] = Field(..., description="List of symptoms")
    medical_history: Dict[str, Any] = Field(default_factory=dict, description="Patient medical history")
    use_federated_learning: bool = Field(default=True, description="Use federated learning insights")
    privacy_level: str = Field(default="high", description="Privacy level for analysis")


class DiagnosticResponse(BaseModel):
    """Response from AI diagnosis"""
    diagnosis_id: str = Field(..., description="Unique diagnosis ID")
    user_id: UUID = Field(..., description="User ID")
    primary_diagnosis: str = Field(..., description="Primary diagnosis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    recommendations: List[str] = Field(default_factory=list, description="Treatment recommendations")
    urgency_level: str = Field(..., description="Urgency level")
    analysis_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed analysis")
    timestamp: datetime = Field(..., description="Diagnosis timestamp")
    federated_learning_used: bool = Field(..., description="Whether federated learning was used")
    privacy_level: str = Field(..., description="Privacy level used")


class FederatedLearningRequest(BaseModel):
    """Request to join federated learning"""
    study_type: str = Field(..., description="Type of study")
    data_contribution: str = Field(..., description="Type of data to contribute")
    min_participants: int = Field(default=3, description="Minimum participants required")
    max_rounds: int = Field(default=10, description="Maximum learning rounds")


class FederatedLearningResponse(BaseModel):
    """Response from federated learning join"""
    round_id: str = Field(..., description="Learning round ID")
    participant_id: str = Field(..., description="Participant ID")
    status: str = Field(..., description="Participation status")
    expected_rounds: int = Field(..., description="Expected number of rounds")
    current_participants: int = Field(..., description="Current number of participants")


class AIAgentRegistration(BaseModel):
    """AI Agent registration data"""
    name: str = Field(..., description="Agent name")
    agent_type: str = Field(..., description="Type of AI agent")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    hcs_topic_id: str = Field(..., description="HCS topic ID for communication")
    profile_metadata: Dict[str, Any] = Field(default_factory=dict, description="Agent profile metadata")


class AIAgentResponse(BaseModel):
    """AI Agent response"""
    agent_id: str = Field(..., description="Unique agent ID")
    name: str = Field(..., description="Agent name")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Agent status")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    hcs_topic_id: str = Field(..., description="HCS topic ID")
    inbound_topic_id: Optional[str] = Field(None, description="Inbound communication topic")
    outbound_topic_id: Optional[str] = Field(None, description="Outbound communication topic")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
