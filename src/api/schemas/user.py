from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.infrastructure.database.models.roles import UserRole


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    cpf: str # Added cpf


class UserCreate(UserBase):
    password: str
    role: UserRole | None = UserRole.USER


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    password_hash: str