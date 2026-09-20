"""MCP サービスの公開スキーマ（ヘルスチェック・エラー応答）"""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str
    service: str
    server_enabled: bool
    registered_tools: list[str]
    allowlist: list[str] | None = None
