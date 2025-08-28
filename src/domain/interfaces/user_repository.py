from abc import ABC, abstractmethod

from src.domain.entities.user import User


class UserRepository(ABC):

    @abstractmethod
    def register_user(
        self,
        username: str,
        full_name: str,
        cpf: str,
        email: str,
        password: str,
    ) -> User:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass
