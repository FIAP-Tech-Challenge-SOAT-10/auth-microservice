from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, text
from sqlalchemy.orm import relationship

from src.infrastructure.database.session import Base
from src.infrastructure.database.models.roles import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    cpf = Column(String(11), unique=True, index=True, nullable=True) # Added cpf
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship to RefreshToken
    refresh_tokens = relationship("RefreshToken", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"