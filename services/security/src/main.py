"""
CEO-OS Security Service

建設・土木業向けセキュリティ監視・インシデント管理サービス。
SOC/SIEM, vulnerability scanning, security incident management.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import dashboard, health, incidents, policies, vulnerabilities
from .config import get_settings
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Security Service on {settings.HOST}:{settings.PORT}")
    yield
    logger.info("Shutting down Security Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS Security Service",
        description="建設業統合OS セキュリティ監視・インシデント管理",
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

    app.include_router(
        incidents.router, prefix="/api/v1/security", tags=["incidents"]
    )
    app.include_router(
        vulnerabilities.router, prefix="/api/v1/security", tags=["vulnerabilities"]
    )
    app.include_router(
        policies.router, prefix="/api/v1/security", tags=["policies"]
    )
    app.include_router(
        dashboard.router, prefix="/api/v1/security", tags=["dashboard"]
    )
    app.include_router(health.router, tags=["health"])

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal error. Please contact administrator.",
                },
            },
        )

    return app


app = create_app()
