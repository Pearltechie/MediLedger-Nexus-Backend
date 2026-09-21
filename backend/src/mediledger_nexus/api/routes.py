"""
Main API router for MediLedger Nexus
"""

from fastapi import APIRouter

from mediledger_nexus.api.endpoints import (
    auth,
    health_vault,
    consent,
    medical_records,
    ai_diagnostics,
    emergency,
    research,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health_vault.router, prefix="/vault", tags=["health-vault"])
api_router.include_router(consent.router, prefix="/consent", tags=["consent"])
api_router.include_router(medical_records.router, prefix="/records", tags=["medical-records"])
api_router.include_router(ai_diagnostics.router, prefix="/ai", tags=["ai-diagnostics"])
api_router.include_router(emergency.router, prefix="/emergency", tags=["emergency"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
