"""
Research endpoints for MediLedger Nexus
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mediledger_nexus.core.database import get_async_session
from mediledger_nexus.core.logging import get_logger
from ...models import User
from mediledger_nexus.schemas.research import (
    ResearchDatasetRequest,
    ResearchDatasetResponse,
    ResearchParticipationRequest
)
from mediledger_nexus.services.auth import AuthService
from mediledger_nexus.services.research import ResearchService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/datasets/request", response_model=ResearchDatasetResponse)
async def request_research_dataset(
    dataset_request: ResearchDatasetRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Request access to anonymized research dataset"""
    try:
        research_service = ResearchService(db)
        
        # Process research dataset request
        dataset_response = await research_service.request_dataset(
            researcher_id=current_user.id,
            dataset_request=dataset_request
        )
        
        logger.info(f"Research dataset requested by user {current_user.id}")
        return dataset_response
    
    except Exception as e:
        logger.error(f"Research dataset request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request research dataset"
        )


@router.post("/participate")
async def participate_in_research(
    participation_request: ResearchParticipationRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Participate in research study"""
    try:
        research_service = ResearchService(db)
        
        # Process research participation
        participation_response = await research_service.participate_in_study(
            user_id=current_user.id,
            participation_request=participation_request
        )
        
        logger.info(f"User {current_user.id} participated in research study")
        return participation_response
    
    except Exception as e:
        logger.error(f"Research participation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to participate in research"
        )


@router.get("/studies", response_model=List[dict])
async def get_available_studies(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get available research studies"""
    try:
        research_service = ResearchService(db)
        
        # Get available studies
        studies = await research_service.get_available_studies()
        
        return studies
    
    except Exception as e:
        logger.error(f"Get studies error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve research studies"
        )
