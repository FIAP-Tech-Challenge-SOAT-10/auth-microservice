from src.domain.entities.user import User
from src.domain.interfaces.user_repository import UserRepository


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(
        self, username: str, full_name: str, cpf: str, email: str, password: str
    ) -> User:
        return self.user_repository.register_user(
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password=password,
        )
