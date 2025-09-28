from unittest.mock import Mock

import pytest

from src.domain.entities.user import User
from src.domain.use_cases.register_user_usecase import RegisterUserUseCase


class TestRegisterUserUseCase:
    """Test cases for the RegisterUserUseCase."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return Mock()

    @pytest.fixture
    def register_user_usecase(self, mock_user_repository):
        """Create a RegisterUserUseCase with mocked repository."""
        return RegisterUserUseCase(mock_user_repository)

    def test_register_user_success(self, register_user_usecase, mock_user_repository):
        """Test successful user registration."""
        # Arrange
        username = "testuser"
        full_name = "Test User"
        cpf = "12345678901"
        email = "test@example.com"
        password = "password123"

        expected_user = User(
            user_id=1,
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password_hash="hashed_password",
        )
        mock_user_repository.register_user.return_value = expected_user

        # Act
        result = register_user_usecase.register_user(
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password=password,
        )

        # Assert
        assert result == expected_user
        mock_user_repository.register_user.assert_called_once_with(
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password=password,
        )

    def test_register_user_calls_repository_with_correct_params(
        self, register_user_usecase, mock_user_repository
    ):
        """Test that register_user calls repository with correct parameters."""
        # Arrange
        username = "newuser"
        full_name = "New User"
        cpf = "98765432100"
        email = "new@example.com"
        password = "newpassword"

        # Act
        register_user_usecase.register_user(
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password=password,
        )

        # Assert
        mock_user_repository.register_user.assert_called_once_with(
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password=password,
        )
