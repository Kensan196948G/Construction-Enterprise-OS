"""
CEO-OS Maintenance Service

建設業向け維持管理・災害復旧サービス。
災害報告、復旧計画、維持管理記録、点検スケジュール。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import disasters, health, inspections, maintenance
from .config import get_settings
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Maintenance Service on {settings.HOST}:{settings.PORT}")
    yield
    logger.info("Shutting down Maintenance Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS Maintenance Service",
        description="建設業統合OS 維持管理・災害復旧",
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
        disasters.router, prefix="/api/v1/maintenance", tags=["disasters"]
    )
    app.include_router(
        maintenance.router, prefix="/api/v1/maintenance", tags=["maintenance"]
    )
    app.include_router(
        inspections.router, prefix="/api/v1/maintenance", tags=["inspections"]
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
