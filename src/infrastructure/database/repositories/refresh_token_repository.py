from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domain.interfaces.refresh_token_repository import (
    RefreshTokenRepository as RefreshTokenRepo,
)
from src.infrastructure.database.models.refresh_token import RefreshToken


class RefreshTokenRepository(RefreshTokenRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).filter(RefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def update_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def delete_refresh_token(self, jti: str) -> None:
        await self.session.execute(delete(RefreshToken).filter(RefreshToken.jti == jti))
        await self.session.commit()
