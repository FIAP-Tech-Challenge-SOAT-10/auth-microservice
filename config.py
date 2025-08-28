from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Auth Microservice"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Security settings
    SECRET_KEY: str = (
        "your_default_secret_key"  # Replace with a secure value or load from env
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:123456@localhost:5432/authdb"

    # CORS settings
    ALLOWED_HOSTS: list[str] | str = ["*"]

    def get_allowed_hosts(self) -> list[str]:
        if isinstance(self.ALLOWED_HOSTS, str):
            if self.ALLOWED_HOSTS == "*":
                return ["*"]
            return [host.strip() for host in str(self.ALLOWED_HOSTS).split(",")]
        elif isinstance(self.ALLOWED_HOSTS, list):
            return self.ALLOWED_HOSTS
        else:
            raise ValueError(
                "ALLOWED_HOSTS must be a list or a comma-separated string."
            )

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
