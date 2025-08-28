from datetime import timedelta, datetime, UTC

import pytest

from src.infrastructure.security.password_service import get_password_hash, verify_password
from src.infrastructure.security.token_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_token_hash,
    verify_refresh_token,
)


class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_password_hashing_and_verification(self):
        """Test that password hashing and verification work correctly."""
        plain_password = "testpassword123"

        # Hash the password
        hashed = get_password_hash(plain_password)

        # Verify the hashed password is not the same as plain text
        assert hashed != plain_password
        assert len(hashed) > 0

        # Verify the password
        assert verify_password(plain_password, hashed) is True

        # Verify wrong password fails
        assert verify_password("wrongpassword", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password123"
        password2 = "password456"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2

    def test_same_password_produces_different_hashes(self):
        """Test that same password produces different hashes due to salt."""
        password = "testpassword123"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Different hashes due to different salts
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        user_data = {"sub": "testuser", "email": "test@example.com", "user_id": 1}

        token = create_access_token(data=user_data)

        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT tokens have dots

    def test_create_access_token_with_custom_expiry(self):
        """Test JWT token creation with custom expiration."""
        user_data = {"sub": "testuser", "email": "test@example.com", "user_id": 1}

        # Create token with 5 minute expiry
        custom_expiry = timedelta(minutes=5)
        token = create_access_token(data=user_data, expires_delta=custom_expiry)

        assert isinstance(token, str)
        assert len(token) > 0


class TestRefreshTokenUtils:
    """Test refresh token utility functions."""

    @pytest.mark.asyncio
    async def test_create_refresh_token_function(self):
        """Test the create_refresh_token utility function."""
        user_id = 1

        token, jti = create_refresh_token(user_id=user_id)

        # Should return a JWT string and JTI
        assert isinstance(token, str)
        assert isinstance(jti, str)
        assert len(token) > 0
        assert len(jti) > 0

        # Should be decodeable
        payload = decode_refresh_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert payload["jti"] == jti
        assert "exp" in payload
        assert "iat" in payload

    @pytest.mark.asyncio
    async def test_refresh_token_expiration(self):
        """Test that refresh tokens have 7-day expiration."""
        user_id = 1

        token, _ = create_refresh_token(user_id=user_id)
        payload = decode_refresh_token(token)

        # Check expiration is approximately 7 days from now
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat = datetime.fromtimestamp(payload["iat"], tz=UTC)
        expected_duration = timedelta(days=7)
        actual_duration = exp - iat

        # Allow for small timing differences (within 1 minute)
        assert (
            abs(actual_duration.total_seconds() - expected_duration.total_seconds())
            < 60
        )

    @pytest.mark.asyncio
    async def test_verify_refresh_token_function(self):
        """Test the verify_refresh_token function."""
        user_id = 1

        # Create and store refresh token
        token, _ = create_refresh_token(user_id=user_id)

        # Create refresh token hash
        token_hash = generate_token_hash(token)

        # Test verification - verify_refresh_token checks token format against hash
        is_valid = verify_refresh_token(token, token_hash)
        assert is_valid is True

        # Test with invalid token
        is_valid = verify_refresh_token("invalid_token", token_hash)
        assert is_valid is False
