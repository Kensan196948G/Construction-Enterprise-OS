"""設定管理（環境変数ベース）"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # アプリケーション
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # データベース
    DATABASE_URL: str = "postgresql+asyncpg://construction-os:construction-os_dev@localhost:5432/construction-os"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT
    JWT_SECRET_KEY: str = "dev-only-do-not-use-in-production"
    JWT_ALGORITHM: str = "HS256"

    NOTIFICATION_SERVICE_URL: str = ""
    NOTIFICATION_INTERNAL_API_KEY: str = ""
    NOTIFICATION_TIMEOUT_SECONDS: float = 3.0
    INTERNAL_JOB_API_KEY: str = ""
    DOCUMENT_SERVICE_URL: str = ""
    DOCUMENT_INTERNAL_API_KEY: str = ""
    DOCUMENT_RETRY_COUNT: int = 3
    AUTH_SERVICE_URL: str = ""
    AUTH_INTERNAL_API_KEY: str = ""
    WORKLOAD_ALERT_RATIO: float = 1.5
    WORKLOAD_CAPACITY_PER_STAFF: int = 20


@lru_cache()
def get_settings() -> Settings:
    return Settings()
