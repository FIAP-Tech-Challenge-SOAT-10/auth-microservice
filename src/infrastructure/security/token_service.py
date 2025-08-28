import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from src.config import settings
from src.infrastructure.security.password_service import get_password_hash, verify_password

def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(user_id: int, jti: str | None = None) -> tuple[str, str]:
    if jti is None:
        jti = str(uuid.uuid4())

    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_data = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "exp": expire,
        "iat": datetime.now(UTC),
    }

    refresh_token = jwt.encode(
        refresh_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return refresh_token, jti

def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except ExpiredSignatureError as e:
        raise e # Re-raise for specific handling
    except JWTError as e:
        raise e # Re-raise for specific handling

def decode_refresh_token(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise JWTError("Invalid token type")
    return payload

def generate_token_hash(token: str) -> str:
    return get_password_hash(token)

def verify_refresh_token(token: str, stored_hash: str) -> bool:
    return verify_password(token, stored_hash)