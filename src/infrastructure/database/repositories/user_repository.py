from src.domain.interfaces.user_repository import UserRepository as UserRepo
from src.infrastructure.database.models.user import User
from src.infrastructure.database.session import AsyncSessionLocal


class UserRepository(UserRepo):

    def register_user(
        self,
        username: str,
        full_name: str,
        cpf: str,
        email: str,
        password: str,
    ) -> User:
        user = User(
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password_hash=password,
        )
        return user

    def get_user(self, user_id: int) -> User:
        return User(id=user_id)

    def update_user(self, user: User) -> User:
        user = User(id=user.id)
        new_user = User(
            id=user.id,
            username=user.username or None,
            full_name=user.full_name or None,
            cpf=user.cpf or None,
            email=user.email or None,
            password_hash=user.password_hash or None,
        )
        return new_user

    def delete_user(self, user_id: int) -> None:
        pass
