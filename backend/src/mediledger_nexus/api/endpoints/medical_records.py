"""
Medical Records endpoints for MediLedger Nexus
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mediledger_nexus.core.database import get_async_session
from mediledger_nexus.core.logging import get_logger
from ...models import User
from mediledger_nexus.schemas.medical_records import (
    MedicalRecordResponse,
    RecordAccessRequest,
    RecordShareRequest
)
from mediledger_nexus.services.auth import AuthService
from mediledger_nexus.services.medical_records import MedicalRecordService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[MedicalRecordResponse])
async def get_user_records(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get all medical records for the current user"""
    try:
        record_service = MedicalRecordService(db)
        records = await record_service.get_user_records(current_user.id)
        
        return [MedicalRecordResponse.from_orm(record) for record in records]
    
    except Exception as e:
        logger.error(f"Get records error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical records"
        )


@router.get("/{record_id}", response_model=MedicalRecordResponse)
async def get_record(
    record_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get a specific medical record"""
    try:
        record_service = MedicalRecordService(db)
        record = await record_service.get_record(record_id, current_user.id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )
        
        return MedicalRecordResponse.from_orm(record)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get record error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical record"
        )


@router.post("/{record_id}/access", response_model=dict)
async def request_record_access(
    record_id: UUID,
    access_request: RecordAccessRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Request access to a medical record (for healthcare providers)"""
    try:
        record_service = MedicalRecordService(db)
        
        # Create access request with zk-SNARK proof
        access_response = await record_service.request_access(
            record_id=record_id,
            requester_id=current_user.id,
            access_request=access_request
        )
        
        logger.info(f"Record access requested: {record_id} by {current_user.id}")
        return access_response
    
    except Exception as e:
        logger.error(f"Access request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request record access"
        )


@router.post("/{record_id}/share")
async def share_record(
    record_id: UUID,
    share_request: RecordShareRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Share a medical record with another user or provider"""
    try:
        record_service = MedicalRecordService(db)
        
        # Share record with specified user/provider
        share_response = await record_service.share_record(
            record_id=record_id,
            owner_id=current_user.id,
            share_request=share_request
        )
        
        logger.info(f"Record shared: {record_id} by {current_user.id}")
        return share_response
    
    except Exception as e:
        logger.error(f"Share record error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to share medical record"
        )
