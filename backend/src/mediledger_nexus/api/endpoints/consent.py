"""
Consent management endpoints for MediLedger Nexus
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mediledger_nexus.core.database import get_async_session
from mediledger_nexus.core.logging import get_logger
from ...models import User
from mediledger_nexus.schemas.consent import (
    ConsentCreate,
    ConsentResponse,
    ConsentUpdate,
    ConsentRevoke
)
from mediledger_nexus.services.auth import AuthService
from mediledger_nexus.services.consent import ConsentService
from mediledger_nexus.services.blockchain import BlockchainService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/grant", response_model=ConsentResponse)
async def grant_consent(
    consent_data: ConsentCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Grant consent for data access with tokenized compensation"""
    try:
        consent_service = ConsentService(db)
        blockchain_service = BlockchainService()
        
        # Create consent record with smart contract
        consent = await consent_service.grant_consent(
            user_id=current_user.id,
            consent_data=consent_data
        )
        
        # Deploy consent smart contract on Hedera
        contract_id = await blockchain_service.deploy_consent_contract(
            consent_id=consent.id,
            patient_account=current_user.hedera_account_id,
            provider_account=consent_data.provider_account_id,
            record_types=consent_data.record_types,
            duration_hours=consent_data.duration_hours
        )
        
        # Update consent with contract ID
        await consent_service.update_contract_id(consent.id, contract_id)
        
        logger.info(f"Consent granted: {consent.id} for user {current_user.id}")
        return ConsentResponse.from_orm(consent)
    
    except Exception as e:
        logger.error(f"Grant consent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant consent"
        )


@router.get("/", response_model=List[ConsentResponse])
async def get_user_consents(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get all consents for the current user"""
    try:
        consent_service = ConsentService(db)
        consents = await consent_service.get_user_consents(current_user.id)
        
        return [ConsentResponse.from_orm(consent) for consent in consents]
    
    except Exception as e:
        logger.error(f"Get consents error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consents"
        )


@router.get("/{consent_id}", response_model=ConsentResponse)
async def get_consent(
    consent_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get a specific consent"""
    try:
        consent_service = ConsentService(db)
        consent = await consent_service.get_consent(consent_id, current_user.id)
        
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent not found"
            )
        
        return ConsentResponse.from_orm(consent)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get consent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consent"
        )


@router.put("/{consent_id}", response_model=ConsentResponse)
async def update_consent(
    consent_id: UUID,
    consent_data: ConsentUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Update a consent"""
    try:
        consent_service = ConsentService(db)
        consent = await consent_service.update_consent(
            consent_id, current_user.id, consent_data
        )
        
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent not found"
            )
        
        logger.info(f"Consent updated: {consent_id}")
        return ConsentResponse.from_orm(consent)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update consent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update consent"
        )


@router.post("/{consent_id}/revoke")
async def revoke_consent(
    consent_id: UUID,
    revoke_data: ConsentRevoke,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Revoke a consent"""
    try:
        consent_service = ConsentService(db)
        blockchain_service = BlockchainService()
        
        # Revoke consent in database
        success = await consent_service.revoke_consent(
            consent_id, current_user.id, revoke_data.reason
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent not found"
            )
        
        # Revoke consent on blockchain
        await blockchain_service.revoke_consent_contract(consent_id)
        
        logger.info(f"Consent revoked: {consent_id}")
        return {"message": "Consent revoked successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revoke consent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke consent"
        )


@router.get("/{consent_id}/earnings")
async def get_consent_earnings(
    consent_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get earnings from consent monetization"""
    try:
        consent_service = ConsentService(db)
        blockchain_service = BlockchainService()
        
        # Get consent details
        consent = await consent_service.get_consent(consent_id, current_user.id)
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent not found"
            )
        
        # Get earnings from blockchain
        earnings = await blockchain_service.get_consent_earnings(consent.contract_id)
        
        return {
            "consent_id": consent_id,
            "total_earnings": earnings.total_hbar,
            "heal_tokens": earnings.heal_tokens,
            "access_count": earnings.access_count,
            "last_access": earnings.last_access
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get earnings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consent earnings"
        )
