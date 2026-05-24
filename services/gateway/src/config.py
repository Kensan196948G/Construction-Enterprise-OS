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
    GATEWAY_HOST: str = "0.0.0.0"
    GATEWAY_PORT: int = 9000
    DEBUG: bool = True

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3100",
        "http://localhost:3101",
        "http://0.0.0.0:3100",
        "http://0.0.0.0:3101",
    ]

    JWT_PUBLIC_KEY: str = "dev-only-do-not-use-in-production"
    JWT_ALGORITHM: str = "HS256"

    RATE_LIMIT_PER_MINUTE: int = 100

    UPSTREAM_SERVICES: dict[str, str] = {
        "^/api/v1/auth": "http://localhost:8000",
        "^/api/v1/users": "http://localhost:8000",
        "^/api/v1/roles": "http://localhost:8000",
        "^/api/v1/permissions": "http://localhost:8000",
        "^/api/v1/api-clients": "http://localhost:8000",
        "^/api/v1/audit-logs": "http://localhost:8000",
        "^/api/v1/documents": "http://localhost:8001",
        "^/api/v1/workflow": "http://localhost:8002",
        "^/api/v1/gis": "http://localhost:8003",
        "^/api/v1/iot": "http://localhost:8004",
        "^/api/v1/ai": "http://localhost:8005",
        "^/api/v1/erp": "http://localhost:8020",
        "^/api/v1/construction": "http://localhost:8016",
        "^/api/v1/safety": "http://localhost:8007",
        "^/api/v1/search": "http://localhost:8006",
    }

    PUBLIC_PATHS: list[str] = [
        "^/health$",
        "^/api/v1/auth/login$",
        "^/api/v1/auth/mfa/verify$",
        "^/api/v1/auth/refresh$",
        "^/docs$",
        "^/openapi.json$",
        "^/redoc$",
    ]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
