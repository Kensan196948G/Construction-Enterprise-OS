"""CEOS 読み取り専用 MCP ツール定義（第1増分）

公開するのは以下の 5 ツールのみ。書き込み・承認・確定（R2/R3/R4）は公開しない。

| ツール名 | 上流エンドポイント |
| --- | --- |
| ``ceos.wbs.get_tree`` | GET /api/v1/construction/wbs/tree |
| ``ceos.schedule.get_gantt`` | GET /api/v1/construction/projects/{project_id}/gantt |
| ``ceos.cost.list`` | GET /api/v1/erp/ledger/{ledger_id}/costs |
| ``ceos.ledger.get_summary`` | GET /api/v1/erp/ledger/summary |
| ``ceos.contract.list`` | GET /api/v1/erp/invoices |

注記（上流パスの確認結果）:
    指示上の ``ceos.cost.list`` は ``GET /api/v1/erp/costs`` とされていたが、
    ``services/erp`` のルーターを確認したところ当該パスは存在せず、原価明細の
    読み取りは ``GET /api/v1/erp/ledger/{ledger_id}/costs`` のみである。
    存在しないパスを公開すると常に 404 になるため、実在する読み取りルートへ
    対応付けた（ADR-0002 に記載）。
"""

from .models import ToolDefinition

# 固定した definition_sha256。
# 定義本体（name/description/inputSchema/effect/tier/upstream）を正規化 JSON にした
# SHA-256 であり、変更時はハッシュも更新しなければレジストリのロードが失敗する。
_WBS_GET_TREE_SHA256 = "33f9590213b625e02bafc0435737a374b550fdb4936fa5d81d7aae319d682e3f"
_SCHEDULE_GET_GANTT_SHA256 = "2bc365f79857295766b06fe68e11f21e44565c265f35ad3e758b2b2db5dc1a5f"
_COST_LIST_SHA256 = "819f6b59b49cceffdb609b102ed4164ff0fb6d87c6a740cc285371f7bbdf8135"
_LEDGER_GET_SUMMARY_SHA256 = "407b36dfec84f59c1ea395e2b5df45ea2f145e90f9c31e79ade8fcf9bd5ee60b"
_CONTRACT_LIST_SHA256 = "e5af172a544d09de7d26cfb13ee85cec92356a4012b0381f54d39e771ff9e066"


TOOL_DEFINITIONS: tuple[ToolDefinition, ...] = (
    ToolDefinition(
        name="ceos.wbs.get_tree",
        description=(
            "案件の WBS（Work Breakdown Structure）ツリーを取得する（読み取り専用）。"
            "工程の階層構造と進捗の参照に用いる。"
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "対象案件 ID（MCIP が発番）",
                }
            },
            "required": ["project_id"],
            "additionalProperties": False,
        },
        effect="read",
        tier="R0",
        upstream_service="construction",
        upstream_method="GET",
        upstream_path="/api/v1/construction/wbs/tree",
        definition_sha256=_WBS_GET_TREE_SHA256,
    ),
    ToolDefinition(
        name="ceos.schedule.get_gantt",
        description=(
            "案件の工程ガントデータを取得する（読み取り専用）。"
            "工程の期間・依存関係の参照に用いる。"
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "対象案件 ID",
                }
            },
            "required": ["project_id"],
            "additionalProperties": False,
        },
        effect="read",
        tier="R0",
        upstream_service="construction",
        upstream_method="GET",
        upstream_path="/api/v1/construction/projects/{project_id}/gantt",
        definition_sha256=_SCHEDULE_GET_GANTT_SHA256,
    ),
    ToolDefinition(
        name="ceos.cost.list",
        description=(
            "工事台帳に紐づく原価明細の一覧を取得する（読み取り専用）。"
            "原価の参照のみを行い、承認・更新・削除は行わない。"
        ),
        input_schema={
            "type": "object",
            "properties": {
                "ledger_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "対象の工事台帳 ID",
                },
                "status": {
                    "type": "string",
                    "description": "原価明細ステータスで絞り込む（任意）",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                    "description": "ページ番号（任意）",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                    "description": "1 ページあたりの件数（任意）",
                },
            },
            "required": ["ledger_id"],
            "additionalProperties": False,
        },
        effect="read",
        tier="R0",
        upstream_service="erp",
        upstream_method="GET",
        upstream_path="/api/v1/erp/ledger/{ledger_id}/costs",
        definition_sha256=_COST_LIST_SHA256,
    ),
    ToolDefinition(
        name="ceos.ledger.get_summary",
        description=(
            "全社の工事台帳 財務サマリー（売上・原価・利益）を取得する（読み取り専用）。"
        ),
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        effect="read",
        tier="R0",
        upstream_service="erp",
        upstream_method="GET",
        upstream_path="/api/v1/erp/ledger/summary",
        definition_sha256=_LEDGER_GET_SUMMARY_SHA256,
    ),
    ToolDefinition(
        name="ceos.contract.list",
        description=(
            "契約・請求（invoice）の一覧を取得する（読み取り専用）。"
            "支払・更新は行わない。"
        ),
        input_schema={
            "type": "object",
            "properties": {
                "organization_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "組織 ID で絞り込む（任意）",
                },
                "ledger_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "工事台帳 ID で絞り込む（任意）",
                },
                "invoice_type": {
                    "type": "string",
                    "description": "請求種別で絞り込む（任意）",
                },
                "status": {
                    "type": "string",
                    "description": "ステータスで絞り込む（任意）",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                    "description": "ページ番号（任意）",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                    "description": "1 ページあたりの件数（任意）",
                },
            },
            "additionalProperties": False,
        },
        effect="read",
        tier="R0",
        upstream_service="erp",
        upstream_method="GET",
        upstream_path="/api/v1/erp/invoices",
        definition_sha256=_CONTRACT_LIST_SHA256,
    ),
)
