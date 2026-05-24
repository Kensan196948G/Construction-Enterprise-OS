"""CEO-OS Analytics Service — データレイク管理・BI分析サービス

データソース管理、ETLパイプライン、BIレポート機能を提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import datasources, health, pipelines, reports
from .config import get_settings
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Analytics Service on {settings.HOST}:{settings.PORT}")
    yield
    logger.info("Shutting down Analytics Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS Analytics Service",
        description="建設業統合OS アナリティクスサービス — データレイク管理・ETL・BI",
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(
        datasources.router, prefix="/api/v1/analytics", tags=["datasources"]
    )
    app.include_router(
        pipelines.router, prefix="/api/v1/analytics", tags=["pipelines"]
    )
    app.include_router(
        reports.router, prefix="/api/v1/analytics", tags=["reports"]
    )

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
