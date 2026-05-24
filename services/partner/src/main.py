"""
Construction-Enterprise-OS 協力会社コラボレーションプラットフォーム (Partner Service)

建設・土木業向け統合OSの協力会社管理サービス。
協力会社の登録・管理、契約管理、評価、プロジェクトアサインを担当する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import partners, contracts, evaluations, assignments, health
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Partner Service on {settings.HOST}:{settings.PORT}")

    # Initialize shared auth middleware
    try:
        from construction_enterprise_os_auth import configure_auth  # type: ignore[import-not-found]
        configure_auth(
            jwt_public_key=getattr(settings, 'jwt_public_key', getattr(settings, 'JWT_PUBLIC_KEY', "dev-key")),
            jwt_algorithm=getattr(settings, 'JWT_ALGORITHM', "HS256"),
        )
    except ImportError:
        pass  # Auth package not installed, using local middleware

    yield
    logger.info("Shutting down Partner Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Construction-Enterprise-OS Partner Service",
        description="建設業統合OS 協力会社コラボレーションプラットフォーム",
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

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(assignments.project_router, prefix="/api/v1/projects", tags=["project-assignments"])
    app.include_router(contracts.router, prefix="/api/v1/partners/contracts", tags=["contracts"])
    app.include_router(evaluations.eval_router, prefix="/api/v1/partners/evaluations", tags=["evaluations"])
    app.include_router(assignments.assign_router, prefix="/api/v1/partners/assignments", tags=["assignments"])
    app.include_router(partners.router, prefix="/api/v1/partners", tags=["partners"])

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
