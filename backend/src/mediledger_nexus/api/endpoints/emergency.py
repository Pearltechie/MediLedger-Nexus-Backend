"""
Emergency response endpoints for MediLedger Nexus
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mediledger_nexus.core.database import get_async_session
from mediledger_nexus.core.logging import get_logger
from ...models import User
from mediledger_nexus.schemas.emergency import (
    EmergencyAccessRequest,
    EmergencyAccessResponse,
    EmergencyProfileUpdate
)
from mediledger_nexus.services.auth import AuthService
from mediledger_nexus.services.emergency import EmergencyService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/access", response_model=EmergencyAccessResponse)
async def emergency_access(
    access_request: EmergencyAccessRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Emergency access to critical health data"""
    try:
        emergency_service = EmergencyService(db)
        
        # Validate emergency access request
        access_response = await emergency_service.process_emergency_access(
            requester_id=current_user.id,
            access_request=access_request
        )
        
        logger.info(f"Emergency access granted for patient {access_request.patient_identifier}")
        return access_response
    
    except Exception as e:
        logger.error(f"Emergency access error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process emergency access"
        )


@router.put("/profile", response_model=dict)
async def update_emergency_profile(
    profile_data: EmergencyProfileUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Update emergency profile information"""
    try:
        emergency_service = EmergencyService(db)
        
        # Update emergency profile
        await emergency_service.update_emergency_profile(
            user_id=current_user.id,
            profile_data=profile_data
        )
        
        logger.info(f"Emergency profile updated for user {current_user.id}")
        return {"message": "Emergency profile updated successfully"}
    
    except Exception as e:
        logger.error(f"Update emergency profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update emergency profile"
        )


@router.get("/profile", response_model=dict)
async def get_emergency_profile(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get emergency profile information"""
    try:
        emergency_service = EmergencyService(db)
        
        # Get emergency profile
        profile = await emergency_service.get_emergency_profile(current_user.id)
        
        return profile
    
    except Exception as e:
        logger.error(f"Get emergency profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve emergency profile"
        )
