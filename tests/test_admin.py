"""
Tests for admin-only endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from src.infrastructure.database.models.roles import UserRole


@pytest.fixture
async def admin_user(client: AsyncClient, test_user_data: dict):
    """Fixture to create an admin user."""
    admin_data = test_user_data.copy()
    admin_data["username"] = "admin_user"
    admin_data["email"] = "admin@example.com"
    admin_data["role"] = UserRole.ADMIN
    response = await client.post("/api/v1/auth/signup", json=admin_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def user_user(client: AsyncClient, test_user_data: dict):
    """Fixture to create a regular user."""
    user_data = test_user_data.copy()
    user_data["username"] = "regular_user"
    user_data["email"] = "user@example.com"
    user_data["role"] = UserRole.USER
    response = await client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def admin_auth_token(client: AsyncClient, admin_user: dict, test_user_data: dict):
    """Fixture to get auth token for admin user."""
    login_data = {
        "username": admin_user["username"],
        "password": test_user_data["password"],
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def user_auth_token(client: AsyncClient, user_user: dict, test_user_data: dict):
    """Fixture to get auth token for regular user."""
    login_data = {
        "username": user_user["username"],
        "password": test_user_data["password"],
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


class TestAdminDashboard:
    """Test cases for the /admin/dashboard endpoint."""

    @pytest.mark.asyncio
    async def test_admin_access_dashboard(
        self, client: AsyncClient, admin_auth_token: str
    ):
        """Test admin can access dashboard."""
        headers = {"Authorization": f"Bearer {admin_auth_token}"}
        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert "Welcome to the admin dashboard" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_user_cannot_access_dashboard(
        self, client: AsyncClient, user_auth_token: str
    ):
        """Test regular user cannot access dashboard."""
        headers = {"Authorization": f"Bearer {user_auth_token}"}
        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_access_dashboard(self, client: AsyncClient):
        """Test unauthenticated user cannot access dashboard."""
        response = await client.get("/api/v1/admin/dashboard")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAdminUsers:
    """Test cases for the /admin/users endpoint."""

    @pytest.mark.asyncio
    async def test_admin_can_list_users(
        self, client: AsyncClient, admin_auth_token: str
    ):
        """Test admin can list users."""
        headers = {"Authorization": f"Bearer {admin_auth_token}"}
        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert "users" in response.json()

    @pytest.mark.asyncio
    async def test_user_cannot_list_users(
        self, client: AsyncClient, user_auth_token: str
    ):
        """Test regular user cannot list users."""
        headers = {"Authorization": f"Bearer {user_auth_token}"}
        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_list_users(self, client: AsyncClient):
        """Test unauthenticated user cannot list users."""
        response = await client.get("/api/v1/admin/users")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
