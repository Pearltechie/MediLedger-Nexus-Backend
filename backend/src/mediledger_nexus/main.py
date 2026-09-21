"""
Main FastAPI application for MediLedger Nexus
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Add the src directory to Python path for deployment compatibility
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # Go up one level from mediledger_nexus to src
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from mediledger_nexus.api.routes import api_router
from mediledger_nexus.core.config import get_settings
from mediledger_nexus.core.database import init_db
from mediledger_nexus.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events"""
    logger.info("Starting MediLedger Nexus application...")
    
    # Initialize database
    await init_db()
    
    # Initialize blockchain connections
    # TODO: Initialize Hedera client
    
    # Initialize IPFS client
    # TODO: Initialize IPFS client
    
    logger.info("Application startup complete")
    
    yield
    
    logger.info("Shutting down MediLedger Nexus application...")
    # Cleanup resources here
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Decentralized Health Data Ecosystem on Hedera",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS.split(","),
        allow_headers=settings.CORS_HEADERS.split(","),
    )
    
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.mediledgernexus.com"]
        )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to MediLedger Nexus API",
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.DEBUG else "Documentation available at docs.mediledgernexus.com"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception handler caught: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    return app


# Create the app instance
app = create_app()


def main() -> None:
    """Main entry point for running the application"""
    uvicorn.run(
        "mediledger_nexus.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
