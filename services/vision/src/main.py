"""
CEO-OS Vision Service

建設・土木業向けOCR・画像AI・ベクトルDB管理サービス。
OCR processing, image AI analysis, and vector database management.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import health, image_ai, ocr, vectors
from .config import get_settings
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Vision Service on {settings.HOST}:{settings.PORT}")
    yield
    logger.info("Shutting down Vision Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS Vision Service",
        description="建設業統合OS OCR・画像AI・ベクトルDB管理",
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

    app.include_router(ocr.router, prefix="/api/v1", tags=["ocr"])
    app.include_router(image_ai.router, prefix="/api/v1", tags=["image-ai"])
    app.include_router(vectors.router, prefix="/api/v1", tags=["vectors"])
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
