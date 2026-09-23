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

# 固定したハッシュ（RFC 8785 JCS で正規化した JSON の SHA-256）。
# - *_SHA256: Core のツール定義ハッシュ規約（name/title/description/inputSchema/
#   outputSchema/annotations/x-mirai）。Core Allowlist へ登録する値と同一。
# - *_BINDING_SHA256: 上流バインディング（name と upstream service/method/path）。
# 定義を変更したらハッシュも更新しなければレジストリのロードが失敗する（fail-closed）。
_WBS_GET_TREE_SHA256 = "6c252544ae59cb2663882bb3059a8849b567dde9a3323dd363fd0855caddab0a"
_WBS_GET_TREE_BINDING_SHA256 = (
    "1e919de993d668c8527d8c57bdfeac6661a2944ac8700e0ea2bc5c62371434be"
)
_SCHEDULE_GET_GANTT_SHA256 = "7fe9f7e72b24a8a301f81d8bbd94d6efe755a31266c82c53191fe50ab83bcbc2"
_SCHEDULE_GET_GANTT_BINDING_SHA256 = (
    "ab9ac41c85ed74fcddcaef357746a9a9a1b5593fa21d078d17233113cf271479"
)
_COST_LIST_SHA256 = "f2604ab4de678cb321b5eab55b4296e9d9eb2bf4f745d6b147ed728d918bdf8a"
_COST_LIST_BINDING_SHA256 = (
    "e7c46c28ff87e94dc784db7b0395d43a696007cf0b7f40d89a6a113991726356"
)
_LEDGER_GET_SUMMARY_SHA256 = "277f1746714a954798202fb73befdb6cf4771ada365c94e688c1512da72af307"
_LEDGER_GET_SUMMARY_BINDING_SHA256 = (
    "0635d260a65a65a259da3be2f2dc839323b5f1cca2c5f0fd8790218174eae8fe"
)
_CONTRACT_LIST_SHA256 = "43feb3d72c81522bfe3895130f98ef42ac0b82c76b779c83ec663a82996c70ad"
_CONTRACT_LIST_BINDING_SHA256 = (
    "8e0f4ab43bae9e60dfe27e3eab2961f84f7d1fad7f948f0dbd334d28990e393d"
)


TOOL_DEFINITIONS: tuple[ToolDefinition, ...] = (
    ToolDefinition(
        name="ceos.wbs.get_tree",
        title="WBSツリーの取得",
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
        binding_sha256=_WBS_GET_TREE_BINDING_SHA256,
    ),
    ToolDefinition(
        name="ceos.schedule.get_gantt",
        title="工程ガントの取得",
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
        binding_sha256=_SCHEDULE_GET_GANTT_BINDING_SHA256,
    ),
    ToolDefinition(
        name="ceos.cost.list",
        title="原価明細の一覧",
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
        binding_sha256=_COST_LIST_BINDING_SHA256,
    ),
    ToolDefinition(
        name="ceos.ledger.get_summary",
        title="工事台帳 財務サマリーの取得",
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
        binding_sha256=_LEDGER_GET_SUMMARY_BINDING_SHA256,
    ),
    ToolDefinition(
        name="ceos.contract.list",
        title="契約・請求の一覧",
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
        binding_sha256=_CONTRACT_LIST_BINDING_SHA256,
    ),
)
