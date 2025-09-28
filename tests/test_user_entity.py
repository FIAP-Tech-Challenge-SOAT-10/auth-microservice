from src.domain.entities.user import User


class TestUserEntity:
    """Test cases for the User entity."""

    def test_user_entity_creation(self):
        """Test User entity creation with all attributes."""
        # Arrange
        user_id = 1
        username = "testuser"
        full_name = "Test User"
        cpf = "12345678901"
        email = "test@example.com"
        password_hash = "hashed_password"

        # Act
        user = User(
            user_id=user_id,
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password_hash=password_hash,
        )

        # Assert
        assert user.id == user_id
        assert user.username == username
        assert user.full_name == full_name
        assert user.cpf == cpf
        assert user.email == email
        assert user.password_hash == password_hash

    def test_user_entity_repr(self):
        """Test User entity __repr__ method."""
        # Arrange
        user = User(
            user_id=1,
            username="testuser",
            full_name="Test User",
            cpf="12345678901",
            email="test@example.com",
            password_hash="hashed_password",
        )

        # Act
        repr_str = repr(user)

        # Assert
        expected_repr = "User(name=Test User, cpf=12345678901, email=test@example.com)"
        assert repr_str == expected_repr

    def test_user_entity_with_different_data(self):
        """Test User entity with different data."""
        # Arrange
        user_id = 42
        username = "another_user"
        full_name = "Another User"
        cpf = "98765432100"
        email = "another@example.com"
        password_hash = "another_hashed_password"

        # Act
        user = User(
            user_id=user_id,
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password_hash=password_hash,
        )

        # Assert
        assert user.id == user_id
        assert user.username == username
        assert user.full_name == full_name
        assert user.cpf == cpf
        assert user.email == email
        assert user.password_hash == password_hash

    def test_user_entity_repr_with_special_characters(self):
        """Test User entity __repr__ method with special characters."""
        # Arrange
        user = User(
            user_id=1,
            username="test_user",
            full_name="José da Silva",
            cpf="11122233344",
            email="jose.silva@example.com",
            password_hash="hashed_password",
        )

        # Act
        repr_str = repr(user)

        # Assert
        expected_repr = (
            "User(name=José da Silva, cpf=11122233344, email=jose.silva@example.com)"
        )
        assert repr_str == expected_repr
