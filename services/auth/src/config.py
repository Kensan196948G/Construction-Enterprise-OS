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
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # データベース
    DATABASE_URL: str = "postgresql+asyncpg://ceoos:ceoos_dev@localhost:5432/ceoos"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_PRIVATE_KEY: str = ""  # 本番では必ず設定
    JWT_PUBLIC_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    M2M_TOKEN_EXPIRE_HOURS: int = 24

    # MFA
    MFA_ISSUER: str = "CEO-OS"
    MFA_TOKEN_VALIDITY_SECONDS: int = 30

    # セキュリティ
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # 開発用JWT秘密鍵 (本番では絶対に使わないこと)
    @property
    def jwt_private_key(self) -> str:
        if self.JWT_PRIVATE_KEY:
            return self.JWT_PRIVATE_KEY
        # 開発用の固定鍵 (本番では必ず環境変数から注入)
        return "dev-only-do-not-use-in-production"

    @property
    def jwt_public_key(self) -> str:
        if self.JWT_PUBLIC_KEY:
            return self.JWT_PUBLIC_KEY
        return "dev-only-do-not-use-in-production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
