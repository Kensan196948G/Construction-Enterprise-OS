"""CEO-OS Construction Service — 施工管理サービス

WBS、資源管理、工程スケジュール、施工計画書を提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import health, methods, resources, schedule, wbs
from .config import get_settings
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Construction Service on {settings.HOST}:{settings.PORT}")

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
    logger.info("Shutting down Construction Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS Construction Service",
        description="建設業統合OS 施工管理サービス — WBS・資源管理・工程管理・施工計画書",
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(wbs.router, prefix="/api/v1/construction", tags=["wbs"])
    app.include_router(resources.router, prefix="/api/v1/construction", tags=["resources"])
    app.include_router(schedule.router, prefix="/api/v1/construction", tags=["schedule"])
    app.include_router(methods.router, prefix="/api/v1/construction", tags=["methods"])

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
