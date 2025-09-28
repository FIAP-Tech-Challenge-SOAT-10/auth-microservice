from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domain.interfaces.user_repository import UserRepository as UserRepo
from src.infrastructure.database.models.user import User


class UserRepository(UserRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(
        self,
        username: str,
        full_name: str,
        cpf: str,
        email: str,
        password: str,
        role: str = "user",
    ) -> User:
        new_user = User(
            username=username,
            full_name=full_name,
            cpf=cpf,
            email=email,
            password_hash=password,
            role=role,
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def get_user(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).filter(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def update_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        await self.session.execute(delete(User).filter(User.id == user_id))
        await self.session.commit()
