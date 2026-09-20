# ADR-0002: CEOS MCP サーバーの読み取り専用公開（第1増分）

- **状態**: Proposed（承認待ち）
- **日付**: 2026-09-20
- **対象リポジトリ**: Construction-Enterprise-OS（CEOS）
- **関連**: [ADR-0001: CEOS の責任範囲とシステム間境界](./ADR-0001-ceos-responsibility-boundary.md)

## 背景

ADR-0001 は「CEOS は工程・原価・契約の正本を持ち、統合入口は MCIP、他システムとは
**公開 API（MCP サーバー公開）**で連携する」と定めた。本 ADR は、その最初の実装増分として
**読み取り専用 MCP サーバー**（`services/mcp`）を追加し、その公開範囲・統制・非対象を記録する。

第1増分の目的は、MCIP / MCAH（Tool Gateway 経由）が CEOS の工程・原価・契約データを
安全に参照できる経路を、責任境界を変えずに追加することにある。

## 決定

### 1. スコープ（読み取り専用 第1増分）

- `services/mcp` を **追加のみ**で新設する。既存サービス・スキーマ・DB は変更しない。
- 公開するのは **読み取り専用ツール 5 件のみ**（`effect="read"`, `tier="R0"`, HTTP GET）。
- 書き込み・承認・支払・確定・削除（R2/R3/R4）は公開しない。R4 は恒久的に拒否する。
- モデル鍵・LLM 呼び出し・承認ロジックは保持しない（MCAH の責務）。

### 2. 公開ツール（5 件）

| ツール名 | 上流エンドポイント | definition_sha256 |
| --- | --- | --- |
| `ceos.wbs.get_tree` | GET `/api/v1/construction/wbs/tree` | `33f9590213b625e02bafc0435737a374b550fdb4936fa5d81d7aae319d682e3f` |
| `ceos.schedule.get_gantt` | GET `/api/v1/construction/projects/{project_id}/gantt` | `2bc365f79857295766b06fe68e11f21e44565c265f35ad3e758b2b2db5dc1a5f` |
| `ceos.cost.list` | GET `/api/v1/erp/ledger/{ledger_id}/costs` | `819f6b59b49cceffdb609b102ed4164ff0fb6d87c6a740cc285371f7bbdf8135` |
| `ceos.ledger.get_summary` | GET `/api/v1/erp/ledger/summary` | `407b36dfec84f59c1ea395e2b5df45ea2f145e90f9c31e79ade8fcf9bd5ee60b` |
| `ceos.contract.list` | GET `/api/v1/erp/invoices` | `e5af172a544d09de7d26cfb13ee85cec92356a4012b0381f54d39e771ff9e066` |

**上流パスの確認結果**: `ceos.cost.list` は当初 `GET /api/v1/erp/costs` と想定していたが、
`services/erp/src/api/costs.py` に当該ルートは存在せず、原価明細の読み取りは
`GET /api/v1/erp/ledger/{ledger_id}/costs` のみである。常に 404 になるツールを公開しないため、
実在する読み取りルートへ対応付けた（ツール名・役割は不変）。

### 3. ハッシュ固定（hash-pinning）

- 各ツールは `definition_sha256`（name・description・inputSchema・effect・tier・upstream を
  `sort_keys=True, separators=(",", ":"), ensure_ascii=False` で正規化した JSON の SHA-256）を持つ。
- レジストリは **ハッシュ欠落・不一致・禁止 effect・非 GET・R0 以外を検知したらロードを拒否**し、
  サーバーを起動しない（fail-closed）。定義変更時はハッシュ更新が必須となる。

### 4. 認証

- `services/construction` と同じ JWT/OIDC パターン。すべての MCP リクエストに有効な
  ユーザー Bearer トークンを必須とする（欠落・不正は 401、ユーザー以外は 403）。
- 呼び出し元の `Authorization` を上流へ転送し、最終認可（組織・案件・ロール）は上流に委ねる。

### 5. キルスイッチ

- `MCP_ENABLED=0` でサーバー全体を停止する（全リクエスト 503）。
- `MCP_TOOL_ALLOWLIST` で個別ツールを許可制にする。未登録・非列挙ツールは
  `tools/call` 時に拒否する（fail-closed、黙って通さない）。

### 6. トランスポート

- 公式 MCP Python SDK（`mcp`）の低レベル `Server` と `StreamableHTTPSessionManager` による
  **MCP over Streamable HTTP**（`POST /mcp/`）。`initialize` / `tools/list` / `tools/call` を提供する。

### 7. 監査

- `tools/call` ごとに caller・tool・latency・result_code・http_status を INFO で記録する。
- 応答本文（業務データ）は INFO で記録しない。

## 結果（Consequences）

- **正**: 責任境界を変えずに、MCIP / MCAH が CEOS の工程・原価・契約を参照する経路を追加できる。
  読み取り専用・ハッシュ固定・キルスイッチ・監査により、公開範囲と改ざん検知を統制できる。
- **負**: 第1増分では参照のみで、CEOS 側の確定・承認フローは自動化されない（人間が実施）。
  MCIP 側のツール登録・Tool Gateway 連携は未実装であり、別途対応が必要。
- **境界への影響**: なし。本増分は ADR-0001 の決定を変更しない。

## 未決・確認事項（第2増分以降）

- 書き込み・承認・確定ツール（**第2増分**。R2/R3 は人間承認と組で別 ADR を要する）
- **OAuth 2.1 のフルフロー**（動的クライアント登録・スコープ・トークン交換）
- **SBOM・成果物署名**（サプライチェーン統制）
- **MCIP 側のツール登録 / Tool Gateway 連携**の実装と契約の版管理
- ADR-0001 は引き続き **Proposed** であり、本増分はその境界判断を前提とする。

## 参照

- [ADR-0001: CEOS の責任範囲（工程・原価・契約の正本）とシステム間境界](./ADR-0001-ceos-responsibility-boundary.md)
- `services/mcp/README.md`
- `services/construction/src/api/{wbs,schedule,resources}.py`
- `services/erp/src/api/{costs,ledger,invoices}.py`
