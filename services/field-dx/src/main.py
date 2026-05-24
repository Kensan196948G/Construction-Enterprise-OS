"""CEO-OS Field DX Service — 現場DX基幹サービス

作業日報、出来形・進捗管理、品質管理を提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import health, progress, quality, reports
from .config import get_settings
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Field DX Service on {settings.HOST}:{settings.PORT}")

    # Initialize shared auth middleware
    try:
        from ceo_os_auth import configure_auth
        configure_auth(
            jwt_public_key=getattr(settings, 'jwt_public_key', getattr(settings, 'JWT_PUBLIC_KEY', "dev-key")),
            jwt_algorithm=getattr(settings, 'JWT_ALGORITHM', "HS256"),
        )
    except ImportError:
        pass  # Auth package not installed, using local middleware

    yield
    logger.info("Shutting down Field DX Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS Field DX Service",
        description="建設業統合OS 現場DXサービス — 作業日報・進捗管理・品質管理",
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(reports.router, prefix="/api/v1/field", tags=["reports"])
    app.include_router(progress.router, prefix="/api/v1/field", tags=["progress"])
    app.include_router(quality.router, prefix="/api/v1/field", tags=["quality"])

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
