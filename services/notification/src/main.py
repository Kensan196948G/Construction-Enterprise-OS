"""
Construction-Enterprise-OS 統合通知基盤 (Notification Service)

建設・土木業向け統合OSの通知サービス。
全サービスからの通知を集約し、各種チャネル（アプリ内・メール等）で配信する。
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import notifications, templates, webhooks
from .api.health import router as health_router
from .models.base import engine
from .models.base import async_session
from .services.template_service import ensure_default_templates

logger = logging.getLogger(__name__)

# 起動時のテンプレート投入リトライ (DB がまだ起動していない場合に備える)
_TEMPLATE_SEED_ATTEMPTS = 3
_TEMPLATE_SEED_RETRY_SECONDS = 2.0


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Notification Service on {settings.HOST}:{settings.PORT}")

    # Initialize shared auth middleware
    try:
        from construction_enterprise_os_auth import configure_auth  # type: ignore[import-not-found]

        configure_auth(
            jwt_public_key=getattr(
                settings,
                "jwt_public_key",
                getattr(settings, "JWT_PUBLIC_KEY", "dev-key"),
            ),
            jwt_algorithm=getattr(settings, "JWT_ALGORITHM", "HS256"),
        )
    except ImportError:
        pass  # Auth package not installed, using local middleware

    # 既定テンプレートは環境を問わず用意する (ensure_default_templates は冪等)。
    # development 限定にすると docker compose (ENVIRONMENT=docker) で
    # テンプレートが未投入のままになり、通知送信が常に 422 で失敗する。
    #
    # シードに失敗したまま起動を続けると、/health は healthy を返すのに
    # 通知だけが TEMPLATE_NOT_FOUND で失敗し続ける。上限付きで再試行し、
    # それでも失敗する場合は起動自体を失敗させる (fail-fast)。
    last_error: Exception | None = None
    for attempt in range(_TEMPLATE_SEED_ATTEMPTS):
        try:
            async with async_session() as db:
                await ensure_default_templates(db)
                await db.commit()
            logger.info("Default notification templates seeded")
            last_error = None
            break
        except Exception as exc:  # noqa: BLE001 - 起動失敗として扱う
            last_error = exc
            logger.exception(
                "Failed to seed default templates (attempt %d/%d)",
                attempt + 1,
                _TEMPLATE_SEED_ATTEMPTS,
            )
            if attempt < _TEMPLATE_SEED_ATTEMPTS - 1:
                await asyncio.sleep(_TEMPLATE_SEED_RETRY_SECONDS * (attempt + 1))

    if last_error is not None:
        raise RuntimeError(
            "既定テンプレートを投入できませんでした。通知は TEMPLATE_NOT_FOUND で"
            "失敗するため起動を中止します。DB と notification スキーマの"
            "マイグレーション適用状況を確認してください。"
        ) from last_error

    yield

    logger.info("Shutting down Notification Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Construction-Enterprise-OS Notification Service",
        description="建設業統合OS 通知サービス",
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
    app.include_router(
        notifications.router, prefix="/api/v1/notifications", tags=["notifications"]
    )
    app.include_router(
        templates.router, prefix="/api/v1/notification-templates", tags=["templates"]
    )
    app.include_router(
        webhooks.router, prefix="/api/v1/notification/webhooks", tags=["webhooks"]
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
