"""CEO-OS ERP Service — 建設業向け統合ERP基幹サービス

工事台帳、予算管理、原価管理、請求管理を提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import budget, costs, health, invoices, ledger
from .config import get_settings
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting ERP Service on {settings.HOST}:{settings.PORT}")

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
    logger.info("Shutting down ERP Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS ERP Service",
        description="建設業統合OS ERPサービス — 工事台帳・原価管理・請求管理",
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(ledger.router, prefix="/api/v1/erp", tags=["ledger"])
    app.include_router(budget.router, prefix="/api/v1/erp", tags=["budget"])
    app.include_router(costs.router, prefix="/api/v1/erp", tags=["costs"])
    app.include_router(invoices.router, prefix="/api/v1/erp", tags=["invoices"])

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
