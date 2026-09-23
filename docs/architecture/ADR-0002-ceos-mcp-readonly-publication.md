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

| ツール名 | 上流エンドポイント | definition_sha256（Core 規約） |
| --- | --- | --- |
| `ceos.wbs.get_tree` | GET `/api/v1/construction/wbs/tree` | `6c252544ae59cb2663882bb3059a8849b567dde9a3323dd363fd0855caddab0a` |
| `ceos.schedule.get_gantt` | GET `/api/v1/construction/projects/{project_id}/gantt` | `7fe9f7e72b24a8a301f81d8bbd94d6efe755a31266c82c53191fe50ab83bcbc2` |
| `ceos.cost.list` | GET `/api/v1/erp/ledger/{ledger_id}/costs` | `f2604ab4de678cb321b5eab55b4296e9d9eb2bf4f745d6b147ed728d918bdf8a` |
| `ceos.ledger.get_summary` | GET `/api/v1/erp/ledger/summary` | `277f1746714a954798202fb73befdb6cf4771ada365c94e688c1512da72af307` |
| `ceos.contract.list` | GET `/api/v1/erp/invoices` | `43feb3d72c81522bfe3895130f98ef42ac0b82c76b779c83ec663a82996c70ad` |

**上流パスの確認結果**: `ceos.cost.list` は当初 `GET /api/v1/erp/costs` と想定していたが、
`services/erp/src/api/costs.py` に当該ルートは存在せず、原価明細の読み取りは
`GET /api/v1/erp/ledger/{ledger_id}/costs` のみである。常に 404 になるツールを公開しないため、
実在する読み取りルートへ対応付けた（ツール名・役割は不変）。

### 3. ハッシュ固定（hash-pinning）

- 各ツールは 2 つのハッシュを固定保持する（RFC 8785 JCS で正規化した JSON の SHA-256）。
  - `definition_sha256`: **Mirai-Harness-Core のツール定義ハッシュ規約**（対象キー
    `name・title・description・inputSchema・outputSchema・annotations・x-mirai`）。
    Core の Allowlist（`registries/mcp-allowlist.yaml`）に登録する値と同一。
  - `binding_sha256`: `name` と上流（`service・method・path`）。Core 規約の対象外である
    CEOS 内部の上流差し替えを検知する。
- レジストリは **いずれかのハッシュの欠落・不一致、禁止 effect、非 GET、R0 以外、
  readOnlyHint と effect の矛盾を検知したらロードを拒否**し、サーバーを起動しない（fail-closed）。
- 改訂履歴: 第1増分の初版（PR #90/#91）は独自正規化（`json.dumps(sort_keys=True)`、
  effect/tier/upstream をトップレベルに含む）で、Core の整合検査（VA-03-3）で必ず不一致となるため
  Issue #93 で Core 規約へ移行した。ツールの名前・入力・上流・読み取り専用性は不変。

### 3.1 Core 契約の固定参照（Issue #79 / #93）

- Core 形式のツール契約を `contracts/mcp-tools/ceos.json`（`server_id: ceos`）として
  レジストリから生成し、CI でドリフトを検査する。
- Core v0.6.0（tag `v0.6.0` / commit `1fe396a`）の必要成果物を
  `contracts/vendor/harness-core/v0.6.0/` へ無改変で vendoring し、
  `contracts/harness-core.lock.json` にファイル SHA-256 を固定する。CI は
  (1) 手編集検知、(2) CEOS ハッシュ実装と Core `tool_def_hash.py` の一致、
  (3) Core 登録済み `mcip` ハッシュの再現（golden vector）、
  (4) `registries/systems.yaml` の `ceos.mcp_server_id` とツール名接頭辞の一致（VA-04）、
  (5) effect/tier の Core 制約（read ⇒ R0）を検査する。
- Core の署名付き配布（O-03/O-04）公開後は `mhc pull` / `mhc verify` と
  `contracts.lock.json` による正規方式へ置き換える。

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
- **MCIP 側のツール登録 / Tool Gateway 連携**の実装
- **`x-mirai.operation` の確定（BLOCKED・Core 判断）**: Core 承認階層表
  （`approval-tiers/tiers.yaml` の `operations`）に CEOS の工程・原価・契約の読み取りに
  対応するカテゴリが無い。推測で既存カテゴリ（`document.search` 等）を流用せず未設定とした。
  Core がカテゴリを追加した後、`operation` を付与してハッシュを更新し、Core の
  `contracts/mcp-tools/ceos.json` と `registries/mcp-allowlist.yaml`（trust / surfaces / scopes を含む）
  への登録を Core リポジトリへ提案する。
- ADR-0001 は引き続き **Proposed** であり、本増分はその境界判断を前提とする。

## 参照

- [ADR-0001: CEOS の責任範囲（工程・原価・契約の正本）とシステム間境界](./ADR-0001-ceos-responsibility-boundary.md)
- `services/mcp/README.md`
- `services/construction/src/api/{wbs,schedule,resources}.py`
- `services/erp/src/api/{costs,ledger,invoices}.py`
