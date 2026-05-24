"""設定管理（環境変数ベース）"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    DATABASE_URL: str = "postgresql+asyncpg://ceoos:ceoos_dev@localhost:5432/ceoos"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    REDIS_URL: str = "redis://localhost:6379/1"

    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@ceo-os.local"
    SMTP_USE_TLS: bool = True

    JWT_PUBLIC_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"

    @property
    def jwt_public_key(self) -> str:
        if self.JWT_PUBLIC_KEY:
            return self.JWT_PUBLIC_KEY
        return "dev-only-do-not-use-in-production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
