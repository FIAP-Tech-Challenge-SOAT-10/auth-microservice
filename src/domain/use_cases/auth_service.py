from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from auth import create_access_token, get_password_hash, verify_password
from config import settings
from models.user import User
from schemas.auth import UserCreate, UserLogin


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, user: UserCreate):
        # Check if user already exists
        db_user = (
            self.db.query(User)
            .filter((User.username == user.username) | (User.email == user.email))
            .first()
        )

        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    async def authenticate_user(self, user: UserLogin):
        db_user = self.db.query(User).filter(User.username == user.username).first()

        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.username}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    async def get_user_by_username(self, username: str):
        db_user = self.db.query(User).filter(User.username == username).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return db_user
