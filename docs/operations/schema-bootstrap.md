# スキーマのブートストラップと DDL の同期

## 背景

以前は、ORM モデルを持つ 21 サービスのうち基盤 DDL がリポジトリにあるのは
`auth` / `workflow`（alembic）と `document`（SQL）だけで、**残り 17 サービスは
モデルはあるがテーブルを作る手段が存在しなかった**。`docker compose up` をしても
マイグレーションは一切実行されないため、空のデータベースでは
`relation "..." does not exist` で全リクエストが失敗する。

現在は各サービスが `migrations/000_base_schema.sql` を持ち、空のデータベースから
再現できる。DDL は ORM モデルから**自動生成**されるため、モデルとの乖離が起きない。

## 手順（空のデータベースから起動する）

```sh
# 1) スキーマ + テーブル + インデックスを作成（冪等・再実行可）
DATABASE_URL="postgresql://user:pass@host:5432/db" make schema-bootstrap

# 2) auth と workflow は alembic 管理のため別途実行
(cd services/auth     && alembic upgrade head)
(cd services/workflow && alembic upgrade head)

# 3) 必要に応じてシード（auth の管理ユーザ等）
(cd services/auth && python -m src.seed)
```

必要な PostgreSQL 拡張:

| 拡張 | 必要なサービス | 備考 |
|---|---|---|
| `postgis` | `gis`, `bim` | DDL 内で `CREATE EXTENSION IF NOT EXISTS postgis` を実行 |
| `vector` (pgvector) | `ai` | DDL 内で `CREATE EXTENSION IF NOT EXISTS vector` を実行 |

> `postgis` と `pgvector` を同時に持たないイメージを使う場合は、拡張を必要と
> するサービスだけ別のデータベースへ適用する（`make schema-check` は拡張の
> 有無に関係なく実行できる）。

## DDL の再生成と検証

`migrations/000_base_schema.sql` は**手で編集しない**。編集しても次の生成で
上書きされる。モデルを変更したら再生成する。

```sh
make schema-generate   # ORM モデルから全サービスの 000_base_schema.sql を再生成
make schema-check      # 生成物がモデルと一致するか検証（乖離があれば exit 1）
```

CI (`.github/workflows/ci.yml`) の各サービスのジョブが `--check` を実行するため、
モデルだけ変更して DDL を更新し忘れると CI が失敗する。

## 生成物の性質

- **冪等**: `CREATE SCHEMA IF NOT EXISTS` / `CREATE TABLE IF NOT EXISTS` /
  `CREATE INDEX IF NOT EXISTS` / `DO $$ ... to_regtype(...) IS NULL ... $$` により、
  再適用しても既存オブジェクトとデータを変更しない。
- **additive のみ**: `DROP` / `TRUNCATE` / 既存列の型変更を含まない。
- `SET search_path TO <schema>, public;` を先頭で固定する。これは SQLAlchemy が
  スキーマ未指定の `Enum` を非修飾名で扱うのと同じ解決規則にするため。

## 検証記録（2026-09-18）

- 空の PostgreSQL 16 (PostGIS) / pgvector に対して全 21 ファイルを適用 → エラー 0、
  2 回連続適用（冪等性）でもエラー 0。
- 適用後のスキーマを ORM メタデータと機械的に比較（テーブル・列・NULL 許容・
  索引・主キー・外部キー）→ **対象 18 サービスすべて一致**。
- 生成 DDL だけで構築したデータベースに対して Document サービスの実機 E2E
  （アップロード → 正本保存 → 作業領域保存 → 実ファイル内容一致 → DB 記録 →
  失敗時の 502 と失敗記録）を実行し、全項目 PASS。

## 生成の過程で見つかった既存モデルの不具合

DDL を実際に適用したことで、いずれも `create_all` でも失敗する本物の不具合が出た。
本リポジトリで修正済み。

| サービス | 内容 |
|---|---|
| `ai` | `server_default=func.false()` / `func.true()` が `DEFAULT false()` / `DEFAULT true()` となり**構文エラー**（`false()` / `true()` に修正） |
| `notification` | ENUM がテーブルのスキーマに作られず参照が解決できなかった（`SET search_path` で解決） |
| `bim` | `bim_elements.model_id` に外部キーが無く mapper 構成が `NoForeignKeysError` で失敗 |
