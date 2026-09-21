"""
Configuration management for MediLedger Nexus
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import validator

# Try to import BaseSettings from pydantic_settings first
try:
    from pydantic_settings import BaseSettings
    print("Successfully imported BaseSettings from pydantic_settings")
except ImportError as e:
    print(f"Failed to import from pydantic_settings: {e}")
    # Try to install it dynamically
    import subprocess
    import sys
    try:
        print("Attempting to install pydantic-settings dynamically...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic-settings==2.0.3"])
        from pydantic_settings import BaseSettings
        print("Successfully installed and imported BaseSettings from pydantic_settings")
    except Exception as install_error:
        print(f"Failed to install pydantic-settings dynamically: {install_error}")
        raise ImportError(
            "pydantic-settings package is required but not installed. "
            "Please install it with: pip install pydantic-settings"
        ) from e


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Settings
    APP_NAME: str = "MediLedger Nexus"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./mediledger_nexus.db"
    DATABASE_ECHO: bool = False
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Hedera Configuration
    HEDERA_NETWORK: str = "testnet"
    HEDERA_ACCOUNT_ID: str = "0.0.0"
    HEDERA_PRIVATE_KEY: str
    HEDERA_PUBLIC_KEY: str = "default-public-key"
    
    # HCS Configuration
    HCS_TOPIC_ID: str = "0.0.0"
    
    # HTS Configuration
    HEAL_TOKEN_ID: str = "0.0.0"
    
    # IPFS Configuration
    IPFS_NODE_URL: str = "http://localhost:5001"
    IPFS_GATEWAY_URL: str = "http://localhost:8080"
    
    # Arweave Configuration
    ARWEAVE_NODE_URL: str = "https://arweave.net"
    ARWEAVE_WALLET_PATH: str = "./arweave-wallet.json"
    
    # Encryption Configuration
    ENCRYPTION_KEY: str
    ZK_SNARK_PROVING_KEY_PATH: str = "./zk/proving_key.json"
    ZK_SNARK_VERIFICATION_KEY_PATH: str = "./zk/verification_key.json"
    
    # AI/ML Configuration
    MODEL_PATH: str = "./models"
    FEDERATED_LEARNING_ROUNDS: int = 10
    MIN_PARTICIPANTS: int = 3
    
    # Groq AI Configuration
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-8b-8192"
    GROQ_MAX_TOKENS: int = 4096
    GROQ_TEMPERATURE: float = 0.7
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    CORS_HEADERS: str = "*"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 100  # MB
    ALLOWED_FILE_EXTENSIONS: str = ".pdf,.dcm,.fastq,.json,.xml"
    UPLOAD_PATH: str = "./uploads"
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = 30  # seconds
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090
    
    # Testing
    TEST_DATABASE_URL: Optional[str] = None
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        if not v or v == "your-secret-key-change-this-in-production":
            raise ValueError("SECRET_KEY must be set to a secure value")
        return v
    
    @validator("HEDERA_PRIVATE_KEY", pre=True)
    def validate_hedera_private_key(cls, v):
        if not v or v == "your-hedera-private-key":
            raise ValueError("HEDERA_PRIVATE_KEY must be set in the environment")
        return v
    
    @validator("ENCRYPTION_KEY", pre=True)
    def validate_encryption_key(cls, v):
        if not v or v == "your-aes-256-encryption-key":
            raise ValueError("ENCRYPTION_KEY must be set in the environment")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from environment


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
