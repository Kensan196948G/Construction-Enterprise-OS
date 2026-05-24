"""
Construction-Enterprise-OS 文書管理基盤 (Document Service)

建設・土木業向け統合OSの文書管理サービス。
ファイルストレージ（MinIO）、メタデータ管理（PostgreSQL）、バージョン管理を提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import documents
from .api.health import router as health_router
from .models.base import engine
from .services.storage_service import initialize_bucket

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    _settings = get_settings()
    logger.info(f"Starting Document Service on {_settings.HOST}:{_settings.PORT}")

    # Initialize shared auth middleware
    try:
        from construction_enterprise_os_auth import configure_auth
        configure_auth(
            jwt_public_key=getattr(_settings, 'jwt_public_key', getattr(_settings, 'JWT_PUBLIC_KEY', "dev-key")),
            jwt_algorithm=getattr(_settings, 'JWT_ALGORITHM', "HS256"),
        )
    except ImportError:
        pass  # Auth package not installed, using local middleware

    if _settings.ENVIRONMENT == "development":
        try:
            initialize_bucket()
            logger.info("MinIO bucket initialized")
        except Exception:
            logger.exception("Failed to initialize MinIO bucket — storage may not be ready")

    yield

    logger.info("Shutting down Document Service")
    await engine.dispose()


def create_app() -> FastAPI:
    _settings = get_settings()

    app = FastAPI(
        title="Construction-Enterprise-OS Document Service",
        description="建設業統合OS 文書管理サービス",
        version="0.1.0",
        docs_url="/docs" if _settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if _settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, tags=["health"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "内部エラーが発生しました。管理者に連絡してください。",
                },
            },
        )

    return app


app = create_app()
