"""
Authentication service for MediLedger Nexus
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from ..core.config import get_settings
from ..models.user import User
from ..schemas.auth import Token, TokenData, UserCreate, UserResponse

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        """Verify and decode a JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(username=username, scopes=token_scopes)
        except JWTError:
            raise credentials_exception
        
        return token_data
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        # This would typically query the database
        # For now, return None as we don't have a database session
        return None
    
    @staticmethod
    def create_user(user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # This would typically create a user in the database
        # For now, return a mock response
        return UserResponse(
            id=1,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def get_current_user(token: str) -> User:
        """Get the current user from a JWT token"""
        # This would typically decode the token and get the user from the database
        # For now, return a mock user
        return User(
            id=1,
            username="test_user",
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )
