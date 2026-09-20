"""ヘルスチェック

MCP サーバーの有効状態と登録ツール数を返す。業務データは返さない。
"""

from fastapi import APIRouter

from ..schemas.mcp import HealthResponse
from ..tools import REGISTRY, describe_policy, load_registry

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    if not REGISTRY.loaded:
        load_registry()
    policy = describe_policy(REGISTRY)
    return HealthResponse(
        status="healthy",
        service="ceos-mcp",
        server_enabled=policy["enabled"],
        registered_tools=policy["registered_tools"],
        allowlist=policy["allowlist"],
    )
