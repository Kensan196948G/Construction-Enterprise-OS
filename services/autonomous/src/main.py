"""
Construction-Enterprise-OS 自律化エンジン (Autonomous Service)

建設・土木業向け統合OSのAIエージェント・デジタルツイン・自律施工サービス。
自律型AIエージェント管理、デジタルツイン、シミュレーションを提供する。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .api import (
    agents,
    controls,
    digital_twins,
    marine_robots,
    operations,
    simulations,
    tasks,
    health,
    machines,
    drone_flights,
    rpa_tasks,
    twin_sensors,
    activities,
    error_logs,
)
from .models.base import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(f"Starting Autonomous Service on {settings.HOST}:{settings.PORT}")

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
    logger.info("Shutting down Autonomous Service")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Construction-Enterprise-OS Autonomous Service",
        description="建設業統合OS 自律型AIエージェント・デジタルツイン・自律施工サービス",
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
    app.include_router(
        agents.router, prefix="/api/v1/autonomous/agents", tags=["agents"]
    )
    app.include_router(
        digital_twins.router,
        prefix="/api/v1/autonomous/digital-twins",
        tags=["digital-twins"],
    )
    app.include_router(tasks.router, prefix="/api/v1/autonomous/tasks", tags=["tasks"])
    app.include_router(
        simulations.router,
        prefix="/api/v1/autonomous/simulations",
        tags=["simulations"],
    )
    app.include_router(
        operations.router, prefix="/api/v1/autonomous/operations", tags=["operations"]
    )
    app.include_router(
        marine_robots.router,
        prefix="/api/v1/autonomous/marine-robots",
        tags=["marine-robots"],
    )
    app.include_router(
        controls.router, prefix="/api/v1/autonomous/controls", tags=["controls"]
    )
    app.include_router(
        machines.router, prefix="/api/v1/autonomous/machines", tags=["machines"]
    )
    app.include_router(
        drone_flights.router,
        prefix="/api/v1/autonomous/drone-flights",
        tags=["drone-flights"],
    )
    app.include_router(
        rpa_tasks.router, prefix="/api/v1/autonomous/rpa-tasks", tags=["rpa-tasks"]
    )
    app.include_router(
        twin_sensors.router,
        prefix="/api/v1/autonomous/twin-sensors",
        tags=["twin-sensors"],
    )
    app.include_router(
        activities.router, prefix="/api/v1/autonomous/activities", tags=["activities"]
    )
    app.include_router(
        error_logs.router, prefix="/api/v1/autonomous/error-logs", tags=["error-logs"]
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
