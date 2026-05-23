"""
CEO-OS 統合認証基盤 (Auth Service)

建設・土木業向け統合OSの認証・認可サービス。
全サービスの認証起点として機能する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import auth, users, roles, permissions, clients, audit
from .models.base import engine, Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションライフサイクル管理"""
    settings = get_settings()
    logger.info(f"Starting Auth Service on {settings.HOST}:{settings.PORT}")

    # 開発環境: テーブル自動作成 (本番ではAlembicマイグレーションを使用)
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            # 本番ではAlembicを使うのでコメントアウト推奨
            pass

    yield

    logger.info("Shutting down Auth Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CEO-OS Auth Service",
        description="建設業統合OS 認証・認可サービス",
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ルーター登録
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
    app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["permissions"])
    app.include_router(clients.router, prefix="/api/v1/api-clients", tags=["api-clients"])
    app.include_router(audit.router, prefix="/api/v1/audit-logs", tags=["audit"])

    # ヘルスチェック
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "auth-service"}

    # グローバルエラーハンドラ
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
