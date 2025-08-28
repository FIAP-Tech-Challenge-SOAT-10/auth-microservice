from datetime import UTC, datetime, timedelta

from src.domain.entities.user import User
from src.domain.interfaces.user_repository import UserRepository
from src.domain.interfaces.refresh_token_repository import RefreshTokenRepository
from src.infrastructure.security.password_service import get_password_hash, verify_password
from src.infrastructure.security.token_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_token_hash,
    verify_refresh_token,
)
from src.api.schemas.auth import Token, TokenWithRefresh
from src.infrastructure.database.models.refresh_token import RefreshToken # Needed for creating RefreshToken object

class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def register_user(
        self, username: str, full_name: str, cpf: str, email: str, password: str
    ) -> User:
        existing_user_by_email = await self.user_repository.get_user_by_email(email)
        if existing_user_by_email:
            raise ValueError("Email already registered")

        existing_user_by_username = await self.user_repository.get_user_by_username(username)
        if existing_user_by_username:
            raise ValueError("Username already taken")

        hashed_password = get_password_hash(password)
        new_user = await self.user_repository.register_user(
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password=hashed_password,
        )
        return new_user

    async def authenticate_user(self, username: str, password: str) -> TokenWithRefresh:
        user = await self.user_repository.get_user_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

        access_token = create_access_token(
            data={
                "sub": user.username,
                "email": user.email,
                "user_id": user.id,
                "role": user.role.value,
            }
        )

        refresh_token, jti = create_refresh_token(user.id)
        refresh_token_hash = generate_token_hash(refresh_token)

        db_refresh_token = RefreshToken(
            jti=jti,
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        await self.refresh_token_repository.add_refresh_token(db_refresh_token)

        return TokenWithRefresh(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    async def refresh_access_token(self, refresh_token_str: str) -> Token:
        payload = decode_refresh_token(refresh_token_str)
        user_id = int(payload.get("sub"))
        jti = payload.get("jti")

        db_refresh_token = await self.refresh_token_repository.get_refresh_token_by_jti(jti)

        if not db_refresh_token or not db_refresh_token.is_active or not verify_refresh_token( # Added db_refresh_token.is_active
            refresh_token_str, db_refresh_token.token_hash
        ):
            raise ValueError("Invalid refresh token")

        if db_refresh_token.expires_at.tzinfo is None:
            db_refresh_token.expires_at = db_refresh_token.expires_at.replace(tzinfo=UTC)

        if db_refresh_token.expires_at < datetime.now(UTC):
            db_refresh_token.is_active = False
            await self.refresh_token_repository.update_refresh_token(db_refresh_token)
            raise ValueError("Refresh token has expired")

        user = await self.user_repository.get_user(user_id)

        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        db_refresh_token.is_active = False
        await self.refresh_token_repository.update_refresh_token(db_refresh_token)

        access_token = create_access_token(
            data={
                "sub": user.username,
                "email": user.email,
                "user_id": user.id,
                "role": user.role.value,
            }
        )
        return Token(access_token=access_token, token_type="bearer")

    async def logout_user(self, refresh_token_str: str) -> None:
        payload = decode_refresh_token(refresh_token_str)
        jti = payload.get("jti")

        db_refresh_token = await self.refresh_token_repository.get_refresh_token_by_jti(jti)

        if db_refresh_token:
            db_refresh_token.is_active = False
            await self.refresh_token_repository.update_refresh_token(db_refresh_token)