"""
Tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestAuthSignup:
    """Test cases for user signup endpoint."""

    @pytest.mark.asyncio
    async def test_successful_signup(self, client: AsyncClient, test_user_data: dict):
        """Test successful user registration."""
        response = await client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == 201
        data = response.json()

        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be in response

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(
        self, client: AsyncClient, test_user_data: dict, created_user: dict
    ):
        """Test signup with duplicate email fails."""
        # Try to create another user with same email
        duplicate_data = {
            "username": "different_username",
            "email": test_user_data["email"],  # Same email
            "full_name": "Different User",
            "password": "differentpassword",
        }

        response = await client.post("/api/v1/auth/signup", json=duplicate_data)

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_signup_duplicate_username(
        self, client: AsyncClient, test_user_data: dict, created_user: dict
    ):
        """Test signup with duplicate username fails."""
        # Try to create another user with same username
        duplicate_data = {
            "username": test_user_data["username"],  # Same username
            "email": "different@example.com",
            "full_name": "Different User",
            "password": "differentpassword",
        }

        response = await client.post("/api/v1/auth/signup", json=duplicate_data)

        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]


class TestAuthLogin:
    """Test cases for user login endpoint."""

    @pytest.mark.asyncio
    async def test_successful_login(
        self, client: AsyncClient, test_user_data: dict, created_user: dict
    ):
        """Test successful user login."""
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_username(
        self, client: AsyncClient, created_user: dict
    ):
        """Test login with invalid username fails."""
        login_data = {"username": "nonexistent_user", "password": "testpassword123"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]


class TestAuthMe:
    """Test cases for the protected /me endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_with_valid_token(
        self,
        client: AsyncClient,
        test_user_data: dict,
        auth_token: str,
    ):
        """Test accessing /me with valid authentication token."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]


class TestRefreshTokens:
    """Test refresh token creation, validation, and management."""

    @pytest.mark.asyncio
    async def test_refresh_token_endpoint(self, client: AsyncClient, test_user_data, created_user):
        """Test the refresh token endpoint returns new access token."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]

        refresh_response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert refresh_response.status_code == status.HTTP_200_OK
        refresh_data = refresh_response.json()

        assert "access_token" in refresh_data
        assert "token_type" in refresh_data
        assert refresh_data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_logout_revokes_refresh_token(
        self, client: AsyncClient, test_user_data, created_user
    ):
        """Test that logout properly revokes refresh tokens."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        logout_response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_response.status_code == status.HTTP_200_OK
        assert "Successfully logged out" in logout_response.json()["message"]

        refresh_response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
