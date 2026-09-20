"""
Construction-Enterprise-OS BIM/CIM Data Platform (BIM Service)

建設業向け統合OSのBIM/CIMデータプラットフォーム。
IFCモデル管理、3Dモデルメタデータ、点群データ、デジタルツイン統合、
施工シミュレーションを提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import models, elements, pointcloud
from .api.health import router as health_router
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting BIM Service on {settings.HOST}:{settings.PORT}")

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
    logger.info("Shutting down BIM Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Construction-Enterprise-OS BIM/CIM Service",
        description="建設業統合OS BIM/CIMデータプラットフォーム",
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

    app.include_router(health_router, tags=["health"])
    app.include_router(models.router, prefix="/api/v1/bim/models", tags=["models"])
    app.include_router(elements.router, prefix="/api/v1/bim", tags=["elements"])
    app.include_router(
        pointcloud.router, prefix="/api/v1/bim/pointclouds", tags=["pointclouds"]
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
