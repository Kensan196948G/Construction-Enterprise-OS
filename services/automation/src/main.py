"""
CEO-OS 自動化・RPAエンジン (Automation Service)

ワークフロー自動化、スケジュールタスク、イベントトリガーを提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import health, rules, tasks, triggers
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Automation Service on {settings.HOST}:{settings.PORT}")

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
    logger.info("Shutting down Automation Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS Automation Service",
        description="建設業統合OS ワークフロー自動化・スケジュールタスク・イベントトリガーサービス",
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(rules.router, prefix="/api/v1/automation/rules", tags=["rules"])
    app.include_router(tasks.router, prefix="/api/v1/automation/tasks", tags=["tasks"])
    app.include_router(triggers.router, prefix="/api/v1/automation/triggers", tags=["triggers"])

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
