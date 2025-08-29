import pytest
from pydantic import ValidationError

from src.api.schemas.user import UserCreate


def test_schema_user_create():
    obj = UserCreate(username="abc", password="xyz", email="abc@example.com", cpf="12345678901")
    assert obj.username == "abc"
    assert obj.email == "abc@example.com"
    assert obj.password == "xyz"
    assert obj.cpf == "12345678901"

def test_user_create_schema_invalid_email():
    """Test UserCreate schema with invalid email."""
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="invalid-email",
            full_name="Test User",
            password="testpassword123",
            cpf="12345678901",
        )

def test_user_create_schema_optional_full_name():
    """Test UserCreate schema with optional full_name."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "cpf": "12345678901",
    }
    user = UserCreate(**user_data)
    assert user.full_name is None

def test_user_create_schema_missing_fields():
    """Test UserCreate schema with missing required fields."""
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", password="password")
