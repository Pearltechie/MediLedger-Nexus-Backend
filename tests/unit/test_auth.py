"""
Unit tests for authentication functionality
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_user(self, client: TestClient, test_user_data):
        """Test user registration"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    def test_register_duplicate_user(self, client: TestClient, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register same user again
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, client: TestClient, test_user_data):
        """Test successful login"""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_get_current_user(self, client: TestClient, test_user_data):
        """Test getting current user information"""
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_refresh_token(self, client: TestClient, test_user_data):
        """Test token refresh"""
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        
        # Refresh token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/auth/refresh", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["access_token"] != token  # Should be a new token


@pytest.mark.asyncio
class TestAuthAsync:
    """Test authentication endpoints with async client"""
    
    async def test_register_user_async(self, async_client: AsyncClient, test_user_data):
        """Test user registration with async client"""
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert "id" in data
    
    async def test_login_async(self, async_client: AsyncClient, test_user_data):
        """Test login with async client"""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = await async_client.post("/api/v1/auth/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
