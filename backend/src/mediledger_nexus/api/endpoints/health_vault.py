"""
Health Vault endpoints for MediLedger Nexus
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from mediledger_nexus.core.database import get_async_session
from mediledger_nexus.core.logging import get_logger
from ...models import User
from mediledger_nexus.schemas.health_vault import (
    HealthVaultCreate,
    HealthVaultResponse,
    HealthVaultUpdate,
    VaultAccessRequest,
    VaultAccessResponse
)
from mediledger_nexus.services.auth import AuthService
from mediledger_nexus.services.health_vault import HealthVaultService
from mediledger_nexus.services.encryption import EncryptionService
from mediledger_nexus.services.ipfs import IPFSService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/create", response_model=HealthVaultResponse)
async def create_vault(
    vault_data: HealthVaultCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Create a new health vault for the user"""
    try:
        vault_service = HealthVaultService(db)
        
        # Create vault on Hedera blockchain
        vault = await vault_service.create_vault(current_user.id, vault_data)
        
        logger.info(f"Health vault created for user {current_user.id}: {vault.id}")
        return HealthVaultResponse.from_orm(vault)
    
    except Exception as e:
        logger.error(f"Vault creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create health vault"
        )


@router.get("/", response_model=List[HealthVaultResponse])
async def get_user_vaults(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get all health vaults for the current user"""
    try:
        vault_service = HealthVaultService(db)
        vaults = await vault_service.get_user_vaults(current_user.id)
        
        return [HealthVaultResponse.from_orm(vault) for vault in vaults]
    
    except Exception as e:
        logger.error(f"Get vaults error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health vaults"
        )


@router.get("/{vault_id}", response_model=HealthVaultResponse)
async def get_vault(
    vault_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get a specific health vault"""
    try:
        vault_service = HealthVaultService(db)
        vault = await vault_service.get_vault(vault_id, current_user.id)
        
        if not vault:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health vault not found"
            )
        
        return HealthVaultResponse.from_orm(vault)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get vault error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health vault"
        )


@router.put("/{vault_id}", response_model=HealthVaultResponse)
async def update_vault(
    vault_id: UUID,
    vault_data: HealthVaultUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Update a health vault"""
    try:
        vault_service = HealthVaultService(db)
        vault = await vault_service.update_vault(vault_id, current_user.id, vault_data)
        
        if not vault:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health vault not found"
            )
        
        logger.info(f"Health vault updated: {vault_id}")
        return HealthVaultResponse.from_orm(vault)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update vault error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update health vault"
        )


@router.post("/{vault_id}/upload")
async def upload_medical_record(
    vault_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Upload a medical record to a health vault"""
    try:
        vault_service = HealthVaultService(db)
        encryption_service = EncryptionService()
        ipfs_service = IPFSService()
        
        # Verify vault ownership
        vault = await vault_service.get_vault(vault_id, current_user.id)
        if not vault:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health vault not found"
            )
        
        # Read and encrypt file content
        content = await file.read()
        encrypted_content = encryption_service.encrypt_data(content)
        
        # Upload to IPFS
        ipfs_hash = await ipfs_service.upload_data(encrypted_content)
        
        # Store record metadata
        record = await vault_service.add_medical_record(
            vault_id=vault_id,
            filename=file.filename,
            content_type=file.content_type,
            ipfs_hash=ipfs_hash,
            file_size=len(content)
        )
        
        logger.info(f"Medical record uploaded to vault {vault_id}: {record.id}")
        
        return {
            "record_id": record.id,
            "filename": file.filename,
            "ipfs_hash": ipfs_hash,
            "status": "uploaded"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload medical record"
        )


@router.post("/{vault_id}/access-request", response_model=VaultAccessResponse)
async def request_vault_access(
    vault_id: UUID,
    access_request: VaultAccessRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Request access to a health vault (for healthcare providers)"""
    try:
        vault_service = HealthVaultService(db)
        
        # Create access request with zk-SNARK proof
        access_response = await vault_service.request_access(
            vault_id=vault_id,
            requester_id=current_user.id,
            access_request=access_request
        )
        
        logger.info(f"Vault access requested: {vault_id} by {current_user.id}")
        return access_response
    
    except Exception as e:
        logger.error(f"Access request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request vault access"
        )


@router.delete("/{vault_id}")
async def delete_vault(
    vault_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Delete a health vault"""
    try:
        vault_service = HealthVaultService(db)
        success = await vault_service.delete_vault(vault_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health vault not found"
            )
        
        logger.info(f"Health vault deleted: {vault_id}")
        return {"message": "Health vault deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete vault error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete health vault"
        )
