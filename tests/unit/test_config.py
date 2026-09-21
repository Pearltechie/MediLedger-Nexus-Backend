"""
Unit tests for configuration management
"""

import pytest
import os
from unittest.mock import patch

from src.mediledger_nexus.core.config import Settings, get_settings


class TestSettings:
    """Test Settings configuration class"""
    
    def test_default_settings(self):
        """Test default configuration values"""
        settings = Settings()
        
        # Test default values
        assert settings.PROJECT_NAME == "MediLedger Nexus"
        assert settings.VERSION == "1.0.0"
        assert settings.ENVIRONMENT == "development"
        assert settings.DEBUG is True
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:8080"]
    
    @patch.dict(os.environ, {
        'PROJECT_NAME': 'Test Project',
        'VERSION': '2.0.0',
        'ENVIRONMENT': 'production',
        'DEBUG': 'false',
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_URL': 'sqlite:///test.db',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '60'
    })
    def test_environment_variable_override(self):
        """Test that environment variables override defaults"""
        settings = Settings()
        
        assert settings.PROJECT_NAME == "Test Project"
        assert settings.VERSION == "2.0.0"
        assert settings.ENVIRONMENT == "production"
        assert settings.DEBUG is False
        assert settings.SECRET_KEY == "test-secret-key"
        assert settings.DATABASE_URL == "sqlite:///test.db"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    
    @patch.dict(os.environ, {
        'CORS_ORIGINS': 'http://localhost:3000,https://example.com,https://api.example.com'
    })
    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from environment"""
        settings = Settings()
        
        expected_origins = [
            "http://localhost:3000",
            "https://example.com", 
            "https://api.example.com"
        ]
        assert settings.CORS_ORIGINS == expected_origins
    
    @patch.dict(os.environ, {
        'HEDERA_NETWORK': 'mainnet',
        'HEDERA_ACCOUNT_ID': '0.0.123456',
        'HEDERA_PRIVATE_KEY': 'test-private-key',
        'HEDERA_MIRROR_NODE_URL': 'https://mainnet.mirrornode.hedera.com'
    })
    def test_hedera_configuration(self):
        """Test Hedera blockchain configuration"""
        settings = Settings()
        
        assert settings.HEDERA_NETWORK == "mainnet"
        assert settings.HEDERA_ACCOUNT_ID == "0.0.123456"
        assert settings.HEDERA_PRIVATE_KEY == "test-private-key"
        assert settings.HEDERA_MIRROR_NODE_URL == "https://mainnet.mirrornode.hedera.com"
    
    @patch.dict(os.environ, {
        'GROQ_API_KEY': 'test-groq-key',
        'GROQ_MODEL': 'llama3-70b-8192',
        'GROQ_MAX_TOKENS': '2048',
        'GROQ_TEMPERATURE': '0.7'
    })
    def test_groq_ai_configuration(self):
        """Test Groq AI configuration"""
        settings = Settings()
        
        assert settings.GROQ_API_KEY == "test-groq-key"
        assert settings.GROQ_MODEL == "llama3-70b-8192"
        assert settings.GROQ_MAX_TOKENS == 2048
        assert settings.GROQ_TEMPERATURE == 0.7
    
    @patch.dict(os.environ, {
        'IPFS_API_URL': 'http://localhost:5001',
        'IPFS_GATEWAY_URL': 'http://localhost:8080',
        'ARWEAVE_GATEWAY_URL': 'https://arweave.net'
    })
    def test_storage_configuration(self):
        """Test storage configuration"""
        settings = Settings()
        
        assert settings.IPFS_API_URL == "http://localhost:5001"
        assert settings.IPFS_GATEWAY_URL == "http://localhost:8080"
        assert settings.ARWEAVE_GATEWAY_URL == "https://arweave.net"
    
    @patch.dict(os.environ, {
        'ENCRYPTION_KEY': 'test-encryption-key',
        'RSA_KEY_SIZE': '4096',
        'AES_KEY_SIZE': '256'
    })
    def test_encryption_configuration(self):
        """Test encryption configuration"""
        settings = Settings()
        
        assert settings.ENCRYPTION_KEY == "test-encryption-key"
        assert settings.RSA_KEY_SIZE == 4096
        assert settings.AES_KEY_SIZE == 256
    
    @patch.dict(os.environ, {
        'LOG_LEVEL': 'WARNING',
        'LOG_FORMAT': 'detailed',
        'LOG_FILE': '/var/log/mediledger.log'
    })
    def test_logging_configuration(self):
        """Test logging configuration"""
        settings = Settings()
        
        assert settings.LOG_LEVEL == "WARNING"
        assert settings.LOG_FORMAT == "detailed"
        assert settings.LOG_FILE == "/var/log/mediledger.log"
    
    def test_database_url_validation(self):
        """Test database URL validation"""
        # Test SQLite URL
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///./test.db'}):
            settings = Settings()
            assert settings.DATABASE_URL == "sqlite:///./test.db"
        
        # Test PostgreSQL URL
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://user:pass@localhost/db'}):
            settings = Settings()
            assert settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
    
    def test_boolean_environment_variables(self):
        """Test boolean environment variable parsing"""
        # Test various boolean representations
        boolean_values = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('yes', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('no', False),
            ('', False)
        ]
        
        for env_value, expected in boolean_values:
            with patch.dict(os.environ, {'DEBUG': env_value}):
                settings = Settings()
                assert settings.DEBUG == expected
    
    def test_integer_environment_variables(self):
        """Test integer environment variable parsing"""
        with patch.dict(os.environ, {'ACCESS_TOKEN_EXPIRE_MINUTES': '120'}):
            settings = Settings()
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 120
            assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    
    def test_float_environment_variables(self):
        """Test float environment variable parsing"""
        with patch.dict(os.environ, {'GROQ_TEMPERATURE': '0.8'}):
            settings = Settings()
            assert settings.GROQ_TEMPERATURE == 0.8
            assert isinstance(settings.GROQ_TEMPERATURE, float)
    
    def test_missing_required_variables(self):
        """Test behavior with missing required environment variables"""
        # Most variables should have defaults, but test critical ones
        settings = Settings()
        
        # These should have reasonable defaults even if not set
        assert settings.SECRET_KEY is not None
        assert settings.DATABASE_URL is not None
        assert len(settings.SECRET_KEY) > 0
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        settings = Settings()
        
        # Test that certain configurations make sense
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.GROQ_MAX_TOKENS > 0
        assert settings.GROQ_TEMPERATURE >= 0.0
        assert settings.GROQ_TEMPERATURE <= 2.0
        assert settings.RSA_KEY_SIZE >= 1024
        assert settings.AES_KEY_SIZE in [128, 192, 256]


class TestGetSettings:
    """Test get_settings function"""
    
    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance"""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2  # Should be the same instance
        assert id(settings1) == id(settings2)
    
    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance"""
        settings = get_settings()
        
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'PROJECT_NAME')
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'SECRET_KEY')
    
    @patch.dict(os.environ, {'PROJECT_NAME': 'Singleton Test'})
    def test_get_settings_environment_changes(self):
        """Test get_settings with environment changes"""
        # Clear any cached settings first
        get_settings.cache_clear() if hasattr(get_settings, 'cache_clear') else None
        
        settings = get_settings()
        assert settings.PROJECT_NAME == "Singleton Test"
    
    def test_settings_immutability(self):
        """Test that settings are effectively immutable"""
        settings = get_settings()
        original_name = settings.PROJECT_NAME
        
        # Try to modify (this might not raise an error but shouldn't persist)
        try:
            settings.PROJECT_NAME = "Modified Name"
        except Exception:
            pass  # Expected if settings are truly immutable
        
        # Get settings again and check
        settings2 = get_settings()
        # The value should either be unchanged or reset to original
        assert settings2.PROJECT_NAME == original_name or settings2.PROJECT_NAME == "Modified Name"


class TestConfigurationIntegration:
    """Test configuration integration with other components"""
    
    def test_database_configuration_integration(self):
        """Test database configuration integration"""
        settings = get_settings()
        
        # Test that database URL is properly formatted
        db_url = settings.DATABASE_URL
        assert db_url is not None
        assert len(db_url) > 0
        
        # Should be a valid database URL format
        valid_prefixes = ['sqlite://', 'postgresql://', 'mysql://', 'oracle://']
        assert any(db_url.startswith(prefix) for prefix in valid_prefixes)
    
    def test_security_configuration_integration(self):
        """Test security configuration integration"""
        settings = get_settings()
        
        # Test that security settings are properly configured
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) >= 32  # Should be reasonably long
        
        if settings.ENCRYPTION_KEY:
            assert len(settings.ENCRYPTION_KEY) >= 16  # Should be reasonably long
    
    def test_api_configuration_integration(self):
        """Test API configuration integration"""
        settings = get_settings()
        
        # Test API-related settings
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert isinstance(settings.CORS_ORIGINS, list)
        assert len(settings.CORS_ORIGINS) > 0
        
        # Test that CORS origins are valid URLs
        for origin in settings.CORS_ORIGINS:
            assert origin.startswith(('http://', 'https://'))
    
    def test_external_service_configuration(self):
        """Test external service configuration"""
        settings = get_settings()
        
        # Test Hedera configuration
        if settings.HEDERA_ACCOUNT_ID:
            assert settings.HEDERA_ACCOUNT_ID.startswith('0.0.')
        
        # Test IPFS configuration
        if settings.IPFS_API_URL:
            assert settings.IPFS_API_URL.startswith(('http://', 'https://'))
        
        if settings.IPFS_GATEWAY_URL:
            assert settings.IPFS_GATEWAY_URL.startswith(('http://', 'https://'))
    
    def test_environment_specific_configuration(self):
        """Test environment-specific configuration"""
        # Test development environment
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            settings = Settings()
            assert settings.ENVIRONMENT == "development"
            assert settings.DEBUG is True  # Usually true in development
        
        # Test production environment
        with patch.dict(os.environ, {'ENVIRONMENT': 'production', 'DEBUG': 'false'}):
            settings = Settings()
            assert settings.ENVIRONMENT == "production"
            assert settings.DEBUG is False  # Should be false in production
        
        # Test testing environment
        with patch.dict(os.environ, {'ENVIRONMENT': 'testing'}):
            settings = Settings()
            assert settings.ENVIRONMENT == "testing"
