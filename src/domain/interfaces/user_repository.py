from abc import ABC, abstractmethod

from src.domain.entities.user import User


class UserRepository(ABC):

    @abstractmethod
    async def register_user(
        self,
        username: str,
        full_name: str,
        cpf: str,
        email: str,
        password: str,
    ) -> User:
        pass

    @abstractmethod
    async def get_user(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        pass