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
    PORT: int = 8005
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://construction-os:construction-os_dev@localhost:5432/construction-os"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT
    JWT_PUBLIC_KEY: str = ""
    JWT_SECRET_KEY: str = "dev-only-do-not-use-in-production"
    JWT_ALGORITHM: str = "HS256"


    # JWT_PUBLIC_KEY と JWT_SECRET_KEY の両方を受け付ける。
    # 他17サービスは JWT_PUBLIC_KEY を参照しており、これら5サービスだけが
    # JWT_SECRET_KEY を参照していたため、JWT_PUBLIC_KEY を一括設定しても
    # 反映されず(公開された開発用既定値のまま)、鍵ローテーションが無言で
    # 失敗していた。JWT_PUBLIC_KEY を優先し、未設定なら JWT_SECRET_KEY を使う。
    @property
    def jwt_public_key(self) -> str:
        if self.JWT_PUBLIC_KEY:
            return self.JWT_PUBLIC_KEY
        return self.JWT_SECRET_KEY or "dev-only-do-not-use-in-production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
