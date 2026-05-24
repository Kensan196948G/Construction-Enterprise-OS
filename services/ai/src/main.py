"""
CEO-OS AI 共通基盤 (AI Service)

建設・土木業向け統合OSのAIプラットフォーム。
LLM統合、RAG、ベクトル検索、プロンプト管理を提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import health, llm, embeddings, rag, prompts
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    _settings = get_settings()
    logger.info(f"Starting AI Service on {_settings.HOST}:{_settings.PORT}")
    yield
    logger.info("Shutting down AI Service")
    await engine.dispose()


def create_app() -> FastAPI:
    _settings = get_settings()

    app = FastAPI(
        title="CEO-OS AI Service",
        description="建設業統合OS AI共通基盤",
        version="0.1.0",
        docs_url="/docs" if _settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if _settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(llm.router, prefix="/api/v1/ai", tags=["llm"])
    app.include_router(embeddings.router, prefix="/api/v1/ai", tags=["embeddings"])
    app.include_router(rag.router, prefix="/api/v1/ai", tags=["rag"])
    app.include_router(prompts.router, prefix="/api/v1/ai", tags=["prompts"])

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
