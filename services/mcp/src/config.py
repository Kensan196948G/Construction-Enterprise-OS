"""設定管理（環境変数ベース）

MCP サービスは CEOS の工程・原価・契約データを **読み取り専用** で公開する。
書き込み・承認・確定のツールは保持しない（ADR-0001 / ADR-0002）。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8022
    DEBUG: bool = True

    JWT_ALGORITHM: str = "HS256"
    JWT_PUBLIC_KEY: str = ""

    # --- MCP キルスイッチ ---
    # MCP_ENABLED=0 でサーバー全体を停止する（fail-closed）。
    # MCP_TOOL_ALLOWLIST が空の場合は登録済みの読み取り専用ツールをすべて許可する。
    # 値が設定された場合は、そこに列挙されたツールだけを許可する。
    MCP_ENABLED: bool = True
    MCP_TOOL_ALLOWLIST: str = ""

    # --- MCP トランスポート ---
    MCP_SERVER_NAME: str = "ceos-mcp"
    MCP_SERVER_VERSION: str = "0.1.0"
    MCP_STATELESS: bool = True

    # --- 上流 CEOS サービス ---
    CONSTRUCTION_SERVICE_URL: str = "http://localhost:8016"
    ERP_SERVICE_URL: str = "http://localhost:8020"
    UPSTREAM_TIMEOUT_SECONDS: float = 10.0

    @property
    def jwt_public_key(self) -> str:
        if self.JWT_PUBLIC_KEY:
            return self.JWT_PUBLIC_KEY
        return "dev-only-do-not-use-in-production"

    @property
    def mcp_enabled(self) -> bool:
        """MCP サーバー全体の有効／無効。"""
        return bool(self.MCP_ENABLED)

    @property
    def tool_allowlist(self) -> frozenset[str] | None:
        """ツール許可リスト。未設定（空）の場合は None（登録済み全ツールを許可）。"""
        raw = self.MCP_TOOL_ALLOWLIST.strip()
        if not raw:
            return None
        return frozenset(item.strip() for item in raw.split(",") if item.strip())

    def upstream_base_url(self, service: str) -> str:
        """上流サービスのベース URL を返す。"""
        if service == "construction":
            return self.CONSTRUCTION_SERVICE_URL.rstrip("/")
        if service == "erp":
            return self.ERP_SERVICE_URL.rstrip("/")
        raise ValueError(f"未知の上流サービスです: {service}")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    # 開発用既定鍵での起動を防止する。ENVIRONMENT が development/test の場合は
    # ローカル開発を妨げないようフォールバックを許容する。
    if settings.ENVIRONMENT not in ("development", "test"):
        resolved = settings.jwt_public_key
        if not resolved or "dev-only" in resolved:
            raise RuntimeError(
                "JWT_PUBLIC_KEY が未設定のため起動を中止します"
                f" (ENVIRONMENT={settings.ENVIRONMENT})。"
                "環境変数 JWT_PUBLIC_KEY を設定してください。"
            )
    return settings
