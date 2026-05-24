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
    PORT: int = 8016
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+asyncpg://ceoos:ceoos_dev@localhost:5432/ceoos"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    JWT_ALGORITHM: str = "HS256"
    JWT_PUBLIC_KEY: str = "dev-only-do-not-use-in-production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
