# セキュリティ対応事項(2026-09-18 時点の棚卸し)

> この文書は**対応が必要な項目の所在と手順**をまとめたもので、秘密情報は含まない。
> 「対応済み」は本リポジトリで修正済みの項目。「要対応」は運用上の判断・操作が必要な項目。

## 要対応(運用判断・資格情報のローテーションが必要)

### 1. 稼働中の admin 資格情報が平文でコミットされている

> **進捗 (2026-09-18)**: リポジトリ内の平文記載は**全4箇所から削除済み**（`git grep` で 0 件を確認）。
> `seed.py` は環境変数必須化、`e2e/api.spec.ts` は未設定時に該当テストをスキップ、
> `e2e.yml` は GitHub Secrets を参照するよう変更済み。
> **残作業: 実際のパスワードのローテーション（運用操作）と GitHub Secrets
> `E2E_ADMIN_EMAIL` / `E2E_ADMIN_PASSWORD` の設定**。Secrets 未設定の間は
> 認証系E2Eがスキップされる（CI は green のまま）。

**元の所在**(同じ値が 4 箇所):

- `README.md`(ログイン手順の記載)
- `docs/operations/api-auth-db-verification.md`
- `services/auth/src/seed.py`(`ADMIN_PASSWORD` 定数)
- `e2e/api.spec.ts`(`E2E_ADMIN_PASSWORD` のフォールバック値)

`e2e.yml` はこの資格情報で公開 URL へログインするため、**GitHub Actions の実行ログにも当たる可能性がある**。

**対応手順**:

1. 本番 / MVP の admin パスワードをローテーションする(リポジトリ外の操作)
2. `seed.py` を `ADMIN_PASSWORD` 環境変数必須化に変更(未設定なら seed を失敗させる)
3. 上記 4 箇所から値を削除し、`e2e.yml` は GitHub Secrets(`E2E_ADMIN_EMAIL` / `E2E_ADMIN_PASSWORD`)必須にしてフォールバックを削除する
4. git 履歴に残るため、**ローテーション前の値は無効とみなす**

**ロールバック**: コード変更は revert 可能。ローテーションは不可逆(旧パスワードは復元不可)。

### 2. JWT 検証鍵が未設定の場合、公開された開発用既定値へフォールバックする

**所在**: 全 22 サービスの `src/config.py`(例: `services/auth/src/config.py:52-64`)と
`services/*/src/middleware/auth.py`。既定値は `.env.example` のプレースホルダと同一文字列。
`docker-compose.yml` はどのサービスにも `JWT_*` を注入していない。

**影響**: 鍵を設定しないまま起動すると、第三者が既知の値で署名した JWT を受け入れる。

**対応手順**:

1. `ENVIRONMENT != development` のとき `JWT_PUBLIC_KEY` / `JWT_SECRET_KEY` が空なら**起動を拒否**する(fail-fast)を全サービスへ追加
2. `docker-compose.yml` の `x-db-env` 相当に `JWT_PUBLIC_KEY` を配線し、Secrets から注入する
3. 鍵名の二重管理を解消する(`JWT_PUBLIC_KEY` に統一。※ `workflow` / `maintenance` / `security` / `safety` / `vision` の 5 サービスは両対応済み — 2026-09-18)
4. 中長期: HS256 共有鍵から **RS256 / EdDSA + `kid` ローテーション**へ移行
5. `require_permission` の `admin_bypass` 既定を、機密リソースでは `False` にする

**ロールバック**: revert 可能。ただし fail-fast 化は鍵未注入の環境でサービスが起動しなくなる。

### 3. 稼働ツリーに生きた DB 資格情報ファイルが存在する

**所在**(git 未追跡・`.gitignore` 済み):

- `services/auth/.env`(ローカル PostgreSQL のアプリ用ロール)
- `services/auth/.env.bak-20260829`(**Neon クラウド DB のオーナーロール**接続文字列)

**対応手順**:

1. `.env.bak-20260829` を削除する
2. Neon のオーナーパスワードをローテーションする(バックアップファイル経由で共有された可能性を考慮)
3. 本番は**最小権限の専用ロール**へ分離する(owner ロールを使わない)
4. git 履歴への混入有無は未確認(`git log --diff-filter=A` による確認を推奨)

**ロールバック**: ファイル削除は可逆(内容は`.env`とほぼ同じ)。ローテーションは不可逆。

### 4. auth サービスの systemd ユニットが旧パスを指している(運用障害)

**症状**: `construction-os-auth.service` が環境ファイルの読み込み失敗と
起動コマンドの不在で crash-loop 状態(再起動失敗 272,517 回以上)。
トンネル `construction-os-api.mirai-dx-platform.com` は `127.0.0.1:18002` を参照するため、
**MVP の `/api/v1/*` が 502 になる**(2026-09-18 に実際に発生。手動起動で復旧済み)。

**原因**: ユニット定義の `WorkingDirectory` / `EnvironmentFile` / `ExecStart` が
移転前のパス `/home/kensan/Projects/Mirai-DX-Project/...` を指している
(現パスは `/home/kensan/Projects/Mirai-Admin-Platform/...`)。

**対応手順(root権限が必要)**: ユニット定義を編集して上記3箇所を現行パスへ置換し、
デーモンの設定を再読込してからユニットを再起動する。その後 `systemctl is-active`
で active を確認する。

修正までの間は手動起動で運用継続中(作業ディレクトリ `services/auth` で
`.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 18002` を detached 起動し、
ログを `services/logs/auth-18002.log` へ出力)。

> 注意: 手動起動はセッション終了後も継続するが、OS再起動後は自動起動しない。
> systemd ユニットの修正を推奨。

## 対応済み(2026-09-18 のセッションで修正済み)

| 項目                                                                                 | PR                         |
| ------------------------------------------------------------------------------------ | -------------------------- |
| 無認証で公開されていたデータ系エンドポイント **27 件**を保護(ルート単位の機械棚卸し) | #48 / #49 / #50            |
| `GET /users/{user_id}` の認可漏れ(`users:read` を要求)                               | #45                        |
| 全 20 サービスの `/health` で DB 到達性を検証(常時 200 だった)                       | #44                        |
| gateway の公開パスに境界を追加(前方一致での意図しない公開を防止)                     | #53                        |
| JWT 鍵の環境変数名分裂(5 サービスが一括設定を無視する)                               | #52                        |
| レート制限の追跡キー未削除によるメモリ枯渇余地                                       | #43                        |
| ユーザー一覧のテナント境界                                                           | **要仕様判断** → Issue #46 |

## 仕様判断が必要なため未着手の項目

- **ユーザー一覧のテナントスコープ**(Issue #46): 単一組織スコープか、組織ツリー(本社→事業部→現場)スコープかで実装が変わる
- **正本・作業領域保存の実 OneDrive 接続**(Issue #41): `CANONICAL_STORAGE_ROOT` への実体保存は実装・検証済み。OneDrive への転送は資格情報の提供待ち
- 保護したエンドポイントの多くは**固定データを返すスタブ**。実データ化する際は `require_permission` による権限ベースの認可へ格上げすること
