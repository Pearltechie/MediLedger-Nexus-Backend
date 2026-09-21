"""
AI Diagnostics endpoints for MediLedger Nexus with HCS-10 agent communication
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mediledger_nexus.core.database import get_async_session
from mediledger_nexus.core.logging import get_logger
from ...models import User
from mediledger_nexus.schemas.ai_diagnostics import (
    DiagnosticRequest,
    DiagnosticResponse,
    FederatedLearningRequest,
    FederatedLearningResponse,
    AIAgentRegistration,
    AIAgentResponse
)
from mediledger_nexus.services.auth import AuthService
from mediledger_nexus.services.ai_diagnostics import AIDiagnosticsService
from mediledger_nexus.services.federated_learning import FederatedLearningService
from mediledger_nexus.services.hcs_agent import HCSAgentService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register-agent", response_model=AIAgentResponse)
async def register_ai_agent(
    agent_data: AIAgentRegistration,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Register an AI agent using HCS-10 OpenConvAI standard"""
    try:
        hcs_agent_service = HCSAgentService(db)
        
        # Register agent in HCS-10 registry
        agent = await hcs_agent_service.register_agent(
            user_id=current_user.id,
            agent_data=agent_data
        )
        
        logger.info(f"AI agent registered: {agent.agent_id} for user {current_user.id}")
        return AIAgentResponse.from_orm(agent)
    
    except Exception as e:
        logger.error(f"AI agent registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register AI agent"
        )


@router.get("/agents", response_model=List[AIAgentResponse])
async def get_user_agents(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get all AI agents for the current user"""
    try:
        hcs_agent_service = HCSAgentService(db)
        agents = await hcs_agent_service.get_user_agents(current_user.id)
        
        return [AIAgentResponse.from_orm(agent) for agent in agents]
    
    except Exception as e:
        logger.error(f"Get agents error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI agents"
        )


@router.post("/diagnose", response_model=DiagnosticResponse)
async def request_ai_diagnosis(
    diagnostic_request: DiagnosticRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Request AI diagnosis using federated learning insights"""
    try:
        ai_service = AIDiagnosticsService(db)
        
        # Perform AI diagnosis with privacy-preserving techniques
        diagnosis = await ai_service.perform_diagnosis(
            user_id=current_user.id,
            diagnostic_request=diagnostic_request
        )
        
        logger.info(f"AI diagnosis completed for user {current_user.id}")
        return diagnosis
    
    except Exception as e:
        logger.error(f"AI diagnosis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform AI diagnosis"
        )


@router.post("/federated-learning/join", response_model=FederatedLearningResponse)
async def join_federated_learning(
    fl_request: FederatedLearningRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Join a federated learning round using HCS-10 agent coordination"""
    try:
        fl_service = FederatedLearningService(db)
        hcs_agent_service = HCSAgentService(db)
        
        # Coordinate with other AI agents via HCS-10
        response = await fl_service.join_learning_round(
            user_id=current_user.id,
            fl_request=fl_request
        )
        
        # Notify other agents via HCS topics
        await hcs_agent_service.broadcast_learning_participation(
            user_id=current_user.id,
            round_id=response.round_id
        )
        
        logger.info(f"User {current_user.id} joined federated learning round {response.round_id}")
        return response
    
    except Exception as e:
        logger.error(f"Federated learning join error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join federated learning"
        )


@router.get("/federated-learning/rounds", response_model=List[FederatedLearningResponse])
async def get_learning_rounds(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get available federated learning rounds"""
    try:
        fl_service = FederatedLearningService(db)
        rounds = await fl_service.get_available_rounds()
        
        return rounds
    
    except Exception as e:
        logger.error(f"Get learning rounds error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve learning rounds"
        )


@router.post("/agents/{agent_id}/connect")
async def connect_to_agent(
    agent_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Connect to another AI agent using HCS-10 connection protocol"""
    try:
        hcs_agent_service = HCSAgentService(db)
        
        # Initiate HCS-10 connection request
        connection = await hcs_agent_service.request_agent_connection(
            requester_user_id=current_user.id,
            target_agent_id=agent_id
        )
        
        logger.info(f"Connection requested to agent {agent_id} by user {current_user.id}")
        return {
            "connection_id": connection.connection_id,
            "connection_topic_id": connection.connection_topic_id,
            "status": "connection_requested"
        }
    
    except Exception as e:
        logger.error(f"Agent connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to AI agent"
        )


@router.post("/agents/{agent_id}/message")
async def send_agent_message(
    agent_id: str,
    message: dict,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Send a message to an AI agent via HCS-10 connection topic"""
    try:
        hcs_agent_service = HCSAgentService(db)
        
        # Send message via HCS-10 connection topic
        message_id = await hcs_agent_service.send_agent_message(
            sender_user_id=current_user.id,
            target_agent_id=agent_id,
            message=message
        )
        
        logger.info(f"Message sent to agent {agent_id} by user {current_user.id}")
        return {
            "message_id": message_id,
            "status": "message_sent"
        }
    
    except Exception as e:
        logger.error(f"Agent message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message to AI agent"
        )


@router.get("/insights", response_model=List[dict])
async def get_ai_insights(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get AI-generated health insights from federated learning"""
    try:
        ai_service = AIDiagnosticsService(db)
        
        # Get personalized insights from federated learning models
        insights = await ai_service.get_health_insights(current_user.id)
        
        return insights
    
    except Exception as e:
        logger.error(f"Get insights error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI insights"
        )
