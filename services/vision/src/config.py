"""Configuration management (env-based)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8011
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ceoos:ceoos_dev@localhost:5432/ceoos"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT
    JWT_SECRET_KEY: str = "dev-only-do-not-use-in-production"
    JWT_ALGORITHM: str = "HS256"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
