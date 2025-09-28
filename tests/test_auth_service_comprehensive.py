from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.api.schemas.auth import Token
from src.domain.use_cases.auth_service import AuthService
from src.infrastructure.database.models.roles import UserRole
from src.infrastructure.database.models.user import User as UserModel


class TestAuthServiceComprehensive:
    """Comprehensive test cases for AuthService to improve coverage."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_refresh_token_repository(self):
        """Create a mock refresh token repository."""
        return AsyncMock()

    @pytest.fixture
    def auth_service(self, mock_user_repository, mock_refresh_token_repository):
        """Create AuthService with mocked repositories."""
        return AuthService(mock_user_repository, mock_refresh_token_repository)

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=UserModel)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.password_hash = "hashed_password"
        user.is_active = True
        user.role = UserRole.USER
        return user

    @pytest.mark.asyncio
    async def test_register_user_with_admin_role(
        self, auth_service, mock_user_repository
    ):
        """Test user registration with admin role."""
        # Arrange
        mock_user_repository.get_user_by_email.return_value = None
        mock_user_repository.get_user_by_username.return_value = None

        expected_user = Mock()
        mock_user_repository.register_user.return_value = expected_user

        # Act
        with patch(
            "src.domain.use_cases.auth_service.get_password_hash",
            return_value="hashed_pass",
        ) as mock_hash:
            result = await auth_service.register_user(
                username="admin",
                full_name="Admin User",
                cpf="12345678901",
                email="admin@example.com",
                password="password123",
                role="admin",
            )

        # Assert
        assert result == expected_user
        mock_hash.assert_called_once_with("password123")
        mock_user_repository.register_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_user(
        self, auth_service, mock_user_repository
    ):
        """Test authentication with inactive user."""
        # Arrange
        inactive_user = Mock()
        inactive_user.is_active = False
        inactive_user.password_hash = "hashed_password"
        mock_user_repository.get_user_by_username.return_value = inactive_user

        # Act & Assert
        with patch(
            "src.domain.use_cases.auth_service.verify_password", return_value=True
        ):
            with pytest.raises(ValueError, match="User account is disabled"):
                await auth_service.authenticate_user("testuser", "password")

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, auth_service, mock_user_repository, mock_user
    ):
        """Test authentication with wrong password."""
        # Arrange
        mock_user_repository.get_user_by_username.return_value = mock_user

        # Act & Assert
        with patch(
            "src.domain.use_cases.auth_service.verify_password", return_value=False
        ):
            with pytest.raises(ValueError, match="Invalid username or password"):
                await auth_service.authenticate_user("testuser", "wrongpassword")

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent_user(
        self, auth_service, mock_user_repository
    ):
        """Test authentication with non-existent user."""
        # Arrange
        mock_user_repository.get_user_by_username.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid username or password"):
            await auth_service.authenticate_user("nonexistent", "password")

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_token(
        self, auth_service, mock_refresh_token_repository
    ):
        """Test refresh token with invalid token."""
        # Arrange
        mock_refresh_token_repository.get_refresh_token_by_jti.return_value = None

        # Act & Assert
        with patch(
            "src.domain.use_cases.auth_service.decode_refresh_token",
            return_value={"sub": "1", "jti": "invalid"},
        ):
            with pytest.raises(ValueError, match="Invalid refresh token"):
                await auth_service.refresh_access_token("invalid_token")

    @pytest.mark.asyncio
    async def test_refresh_access_token_inactive_token(
        self, auth_service, mock_refresh_token_repository
    ):
        """Test refresh token with inactive token."""
        # Arrange
        inactive_token = Mock()
        inactive_token.is_active = False
        inactive_token.token_hash = "hash"
        mock_refresh_token_repository.get_refresh_token_by_jti.return_value = (
            inactive_token
        )

        # Act & Assert
        with patch(
            "src.domain.use_cases.auth_service.decode_refresh_token",
            return_value={"sub": "1", "jti": "test"},
        ):
            with patch(
                "src.domain.use_cases.auth_service.verify_refresh_token",
                return_value=False,
            ):
                with pytest.raises(ValueError, match="Invalid refresh token"):
                    await auth_service.refresh_access_token("inactive_token")

    @pytest.mark.asyncio
    async def test_refresh_access_token_expired_token(
        self, auth_service, mock_refresh_token_repository
    ):
        """Test refresh token with expired token."""
        # Arrange
        expired_token = Mock()
        expired_token.is_active = True
        expired_token.token_hash = "hash"
        expired_token.expires_at = datetime.now(UTC) - timedelta(days=1)  # Expired
        mock_refresh_token_repository.get_refresh_token_by_jti.return_value = (
            expired_token
        )

        # Act & Assert
        with patch(
            "src.domain.use_cases.auth_service.decode_refresh_token",
            return_value={"sub": "1", "jti": "test"},
        ):
            with patch(
                "src.domain.use_cases.auth_service.verify_refresh_token",
                return_value=True,
            ):
                with pytest.raises(ValueError, match="Refresh token has expired"):
                    await auth_service.refresh_access_token("expired_token")

        # Verify token was deactivated
        mock_refresh_token_repository.update_refresh_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_access_token_timezone_handling(
        self, auth_service, mock_refresh_token_repository, mock_user_repository
    ):
        """Test refresh token with timezone-naive datetime."""
        # Arrange
        valid_token = Mock()
        valid_token.is_active = True
        valid_token.token_hash = "hash"
        valid_token.expires_at = datetime.now() + timedelta(days=1)  # No timezone
        valid_token.user_id = 1
        mock_refresh_token_repository.get_refresh_token_by_jti.return_value = (
            valid_token
        )

        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        mock_user.role = Mock()
        mock_user.role.value = "user"
        mock_user_repository.get_user.return_value = mock_user

        # Act & Assert
        with patch(
            "src.domain.use_cases.auth_service.decode_refresh_token",
            return_value={"sub": "1", "jti": "test"},
        ):
            with patch(
                "src.domain.use_cases.auth_service.verify_refresh_token",
                return_value=True,
            ):
                with patch(
                    "src.domain.use_cases.auth_service.create_access_token",
                    return_value="new_token",
                ):
                    result = await auth_service.refresh_access_token("valid_token")

                    assert isinstance(result, Token)
                    assert result.access_token == "new_token"
                    assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_access_token_inactive_user(
        self, auth_service, mock_refresh_token_repository, mock_user_repository
    ):
        """Test refresh token with inactive user."""
        # Arrange
        valid_token = Mock()
        valid_token.is_active = True
        valid_token.token_hash = "hash"
        valid_token.expires_at = datetime.now(UTC) + timedelta(days=1)
        valid_token.user_id = 1
        mock_refresh_token_repository.get_refresh_token_by_jti.return_value = (
            valid_token
        )

        inactive_user = Mock()
        inactive_user.is_active = False
        mock_user_repository.get_user.return_value = inactive_user

        # Act & Assert
        with patch(
            "src.domain.use_cases.auth_service.decode_refresh_token",
            return_value={"sub": "1", "jti": "test"},
        ):
            with patch(
                "src.domain.use_cases.auth_service.verify_refresh_token",
                return_value=True,
            ):
                with pytest.raises(ValueError, match="User not found or inactive"):
                    await auth_service.refresh_access_token("valid_token")

    @pytest.mark.asyncio
    async def test_refresh_access_token_nonexistent_user(
        self, auth_service, mock_refresh_token_repository, mock_user_repository
    ):
        """Test refresh token with non-existent user."""
        # Arrange
        valid_token = Mock()
        valid_token.is_active = True
        valid_token.token_hash = "hash"
        valid_token.expires_at = datetime.now(UTC) + timedelta(days=1)
        valid_token.user_id = 1
        mock_refresh_token_repository.get_refresh_token_by_jti.return_value = (
            valid_token
        )
        mock_user_repository.get_user.return_value = None

        # Act & Assert
        with patch(
            "src.domain.use_cases.auth_service.decode_refresh_token",
            return_value={"sub": "1", "jti": "test"},
        ):
            with patch(
                "src.domain.use_cases.auth_service.verify_refresh_token",
                return_value=True,
            ):
                with pytest.raises(ValueError, match="User not found or inactive"):
                    await auth_service.refresh_access_token("valid_token")

    @pytest.mark.asyncio
    async def test_logout_user_success(
        self, auth_service, mock_refresh_token_repository
    ):
        """Test successful user logout."""
        # Arrange
        token = Mock()
        token.is_active = True
        mock_refresh_token_repository.get_refresh_token_by_jti.return_value = token

        # Act
        with patch(
            "src.domain.use_cases.auth_service.decode_refresh_token",
            return_value={"jti": "test_jti"},
        ):
            await auth_service.logout_user("refresh_token")

        # Assert
        assert token.is_active is False
        mock_refresh_token_repository.update_refresh_token.assert_called_once_with(
            token
        )

    @pytest.mark.asyncio
    async def test_logout_user_nonexistent_token(
        self, auth_service, mock_refresh_token_repository
    ):
        """Test logout with non-existent token."""
        # Arrange
        mock_refresh_token_repository.get_refresh_token_by_jti.return_value = None

        # Act
        with patch(
            "src.domain.use_cases.auth_service.decode_refresh_token",
            return_value={"jti": "nonexistent"},
        ):
            await auth_service.logout_user("nonexistent_token")

        # Assert - should not raise error, just do nothing
        mock_refresh_token_repository.update_refresh_token.assert_not_called()
