"""Construction-Enterprise-OS MCP Service — 読み取り専用 MCP サーバー

CEOS が正本を持つ工程・原価・契約データを、Model Context Protocol（Streamable HTTP）
の読み取り専用ツールとして公開する。書き込み・承認・確定（R2/R3/R4）は公開しない。
詳細は ``docs/architecture/ADR-0002-ceos-mcp-readonly-publication.md`` を参照。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import health
from .api.mcp import build_mcp_runtime
from .config import get_settings
from .middleware.mcp_guard import McpGuardMiddleware
from .services.upstream import close_upstream_client
from .tools import load_registry

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    # 定義ハッシュの欠落・不一致があればここで起動を中止する（fail-closed）
    registry = load_registry()
    runtime = build_mcp_runtime(settings, registry)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        logger.info(
            "Starting MCP Service on %s:%s (enabled=%s, tools=%d)",
            settings.HOST,
            settings.PORT,
            settings.mcp_enabled,
            len(registry.names),
        )
        try:
            async with runtime.session_manager.run():
                yield
        finally:
            await close_upstream_client()
            logger.info("Shutting down MCP Service")

    app = FastAPI(
        title="Construction-Enterprise-OS MCP Service",
        description=(
            "建設業統合OS MCPサービス — 工程・原価・契約の読み取り専用ツール公開"
            "（第1増分 / write・approve 非公開）"
        ),
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )

    app.include_router(health.router, tags=["health"])
    # MCP は Streamable HTTP サブアプリとして /mcp にマウントする。
    # キルスイッチと認証は McpGuardMiddleware が ASGI 層で強制する。
    app.mount("/mcp", McpGuardMiddleware(runtime.asgi_app))

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
