from abc import ABC, abstractmethod
from src.domain.entities.refresh_token import RefreshToken

class RefreshTokenRepository(ABC):
    @abstractmethod
    async def add_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        pass

    @abstractmethod
    async def get_refresh_token_by_jti(self, jti: str) -> RefreshToken | None:
        pass

    @abstractmethod
    async def update_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        pass

    @abstractmethod
    async def delete_refresh_token(self, jti: str) -> None:
        pass
