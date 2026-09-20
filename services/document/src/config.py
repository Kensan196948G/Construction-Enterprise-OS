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

    DATABASE_URL: str = "postgresql+asyncpg://construction-os:construction-os_dev@localhost:5432/construction-os"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "construction-enterprise-os-documents"
    MINIO_SECURE: bool = False
    MAX_UPLOAD_SIZE_MB: int = 500

    JWT_PUBLIC_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"

    INTERNAL_API_KEY: str = ""

    # 正本・作業領域の保存先。docker-compose.yml の同名環境変数と一致させる。
    # 未設定の場合、正本保存は fail-closed で 503 を返す(保存したことにしない)。
    CANONICAL_STORAGE_ROOT: str = ""
    CANONICAL_STORAGE_MAX_FILE_MB: int = 500

    # OneDrive (Microsoft Graph) 連携。ONEDRIVE_ENABLED=true の場合は
    # 4項目すべてが必須で、1つでも欠ければ fail-closed で 503 を返す。
    ONEDRIVE_ENABLED: bool = False
    ONEDRIVE_TENANT_ID: str = ""
    ONEDRIVE_CLIENT_ID: str = ""
    ONEDRIVE_CLIENT_SECRET: str = ""
    ONEDRIVE_DRIVE_ID: str = ""
    ONEDRIVE_ROOT_PATH: str = "Mirai-Site-Admin-Workflow"
    ONEDRIVE_GRAPH_TIMEOUT_SECONDS: float = 60.0

    @property
    def jwt_public_key(self) -> str:
        if self.JWT_PUBLIC_KEY:
            return self.JWT_PUBLIC_KEY
        return "dev-only-do-not-use-in-production"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    # 開発用既定鍵での起動を防止する。ENVIRONMENT が development/test の場合は
    # ローカル開発を妨げないようフォールバックを許容する。
    if settings.ENVIRONMENT not in ("development", "test"):
        resolved = settings.jwt_public_key
        if not resolved or "dev-only" in resolved:
            raise RuntimeError(
                f"JWT_PUBLIC_KEY が未設定のため起動を中止します"
                f" (ENVIRONMENT={settings.ENVIRONMENT})。"
                "環境変数 JWT_PUBLIC_KEY を設定してください。"
            )
    return settings
