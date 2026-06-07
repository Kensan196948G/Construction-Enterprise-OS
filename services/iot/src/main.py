"""
Construction-Enterprise-OS 統合IoT基盤 (IoT Service)

建設・土木業向け統合OSのIoTデバイス管理・センサーデータ収集サービス。
MQTT経由のテレメトリ投入、デバイス管理、アラートルール評価を提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import (
    devices,
    machines,
    sensors,
    sensors_standalone,
    telemetry,
    alerts,
    health,
)
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting IoT Service on {settings.HOST}:{settings.PORT}")

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

    yield
    logger.info("Shutting down IoT Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Construction-Enterprise-OS IoT Service",
        description="建設業統合OS IoTデバイス管理・テレメトリサービス",
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

    app.include_router(health.router, tags=["health"])
    app.include_router(devices.router, prefix="/api/v1/iot/devices", tags=["devices"])
    app.include_router(sensors.router, prefix="/api/v1/iot/devices", tags=["sensors"])
    app.include_router(
        telemetry.router, prefix="/api/v1/iot/telemetry", tags=["telemetry"]
    )
    app.include_router(alerts.router, prefix="/api/v1/iot", tags=["alerts"])
    app.include_router(machines.router, prefix="/api/v1/iot", tags=["machines"])
    app.include_router(
        sensors_standalone.router, prefix="/api/v1/iot", tags=["sensors-standalone"]
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
