# 本番デプロイ記録(リリース確認)

## リリース日時
- 2026-08-18(ラウンド2)

## デプロイ構成(本番)

| 項目 | 値 |
|---|---|
| 本番 URL | https://construction-os.mirai-dx-platform.com |
| Pages プロジェクト | `construction-os-web` |
| 配信内容 | OpenDesign WebUI(単一HTML、index.html として配信) + `_redirects`(SPA フォールバック) |
| 直近デプロイメント | `5412f327`(pages.dev エイリアス) |
| 自動デプロイ | `.github/workflows/pages-deploy.yml`(main への `webui/**` push) |
| DB | Neon `construction-enterprise-os`(main ブランチ、Migration+Seed 適用済み) |

## リリース後確認結果

| 確認項目 | 結果 | 証拠 |
|---|---|---|
| ヘルスチェック(HTTP) | ✅ HTTP 200、9,092,141 bytes | curl 確認 |
| 主要画面(/) | ✅ ダッシュボード KPI・サイドバー表示 | E2E 18/18 PASS |
| 主要ルート(SPA フォールバック) | ✅ /erp/cost・/workflow/approval 等 200 | curl 確認 |
| E2E(Playwright、本番 URL 対象) | ✅ **18/18 PASS**(desktop 9 + mobile 9) | `E2E_BASE_URL=https://construction-os.mirai-dx-platform.com npx playwright test` |
| ロールバック手順 | ✅ 手順確立(docs/operations/deployment.md §5) | Pages rollback API 対応確認 |

## ロールバック手順(実地)

1. Cloudflare ダッシュボード: Pages → construction-os-web → Deployments → 直前の正常版 → Rollback
   (API: `POST /accounts/{account_id}/pages/projects/construction-os-web/deployments/{id}/rollback`)
2. コンテンツ更新は Pages が全デプロイを保持するため、即時復帰可能
3. DB は Neon の Point-in-Time 復元 / ブランチ切替で対応

## 残課題(次フェーズ)

- 本番 API バックエンド(FastAPI + Tunnel)と認証(JWT + Neon)の接続
- Next.js 実装への置換(現状は OpenDesign プロトタイプを配信)

---

# ラウンド4追記(2026-08-19): R6 対応デプロイと検証

## 実施内容
- PR #11(`fix/auth-db-retry-r6` → main squash merge、commit `628ed1b`)で
  auth サービスに以下を実装し、稼働中サービス(127.0.0.1:18002、Tunnel 経由)を
  **修正コードで再起動して反映済み**:
  1. engine: `pool_pre_ping=True` + 接続タイムアウト 10s
  2. login/refresh: 過渡的DBエラー(接続断・タイムアウト)を検出し、新セッションで自動リトライ
  3. グローバル例外ハンドラ: ログにメソッド/パス/クライアントを記録
  4. テスト10件追加(auth サービス合計 40 PASS)

## 検証結果(修正適用後・HTTPS 経由)

| 確認項目 | 結果 | 証拠 |
|---|---|---|
| 連続ログイン 30 回 | ✅ **30/30 成功・INTERNAL_ERROR ゼロ** | curl 10回 + 間隔1s×20回(修正前は初回失敗が観測されていた) |
| API E2E(本番 URL) | ✅ **16/16 PASS**(修正前はログインが 1 flaky) | `npx playwright test e2e/api.spec.ts` |
| MVP E2E(プレビュー URL) | ✅ **9/9 PASS**(desktop) | `npx playwright test e2e/mvp.spec.ts --project=desktop` |
| CI(PR #11) | ✅ **25/25 GREEN**(22×python + frontend + security-scan + docker-build) | GitHub Actions run `32197594005` |
| サービスログ | ✅ エラー・リトライ警告なし | `/tmp/auth-svc.log`(INSERT/COMMIT のみ) |

## 備考
- R6 の実証: 修正前、初回ログインが稀に INTERNAL_ERROR になる事象を
  本番 HTTPS 経由で再現確認(再試行で即成功)。修正後は 30 連続成功。
- WebUI(Pages)は変更なし(webui/ 未変更のため再デプロイ不要)。
- DB(Neon)へのスキーマ変更なし(コードのみの修正)。

---

# ラウンド5(2026-08-19): WebUI データ層 + 全ページ CRUD 実装とデプロイ

## 実施内容
- **`webui/app.html`(新SPA、単一HTML・依存ゼロ)を新規実装**し、Pages デプロイ対象を
  OpenDesign プロトタイプ(スタンドアロン)から切り替え(プロトタイプは
  `standalone-prototype.html` として保全)。
- **全ページ(13 カテゴリ・約 90 ルート)の右側コンテンツで CRUD を実装**:
  - データ取得(ロード・検索フィルタ・一覧/カード表示・KPI 集計)
  - 新規作成(モーダルフォーム、必須バリデーション)
  - 編集(既存データの更新)
  - 削除(確認ダイアログ)
  - 空状態・入力エラー・トースト通知・localStorage 永続化
- データ層: localStorage 永続化ストア(30 コレクションのシードデータ)。
  auth API(`/api/v1/health` 等)は実接続。他サービス API 未稼働のため
  同一インターフェースのローカルストアで代替(将来 API へ差し替え可)。
- 既存 E2E との整合: ダッシュボード KPI・ワークフロー稟議・現場DX・ロール切替・
  通知パネル・モバイル・ダークモードを再現。

## 検証結果(ローカル → デプロイ後)

| 確認項目 | 結果 |
|---|---|
| 既存 E2E(mvp.spec.ts) | ローカル 16/16(SPA フォールバック除く)→ デプロイ後 18/18 確認 |
| CRUD E2E(crud.spec.ts、新規) | 26/26 PASS(一覧/新規/編集/削除/検索/必須エラー/空状態/永続化/KPI 連動) |
| CI | PR で 25/25 GREEN 確認予定 |
| Pages 自動デプロイ | main push(webui/**)で MVP + 本番両方へ反映 |

---

# ラウンド6(2026-08-19): 正本バンドルへの CRUD 統合とデプロイ

## 実施内容
- **OpenDesign 正本バンドル(`Construction-Enterprise-OS---Standalone-_1_.html`)のスタイルを一切変更せず**、
  そのバンドル自体に「データ層(localStorage 永続化ストア)+全ページ CRUD」を統合した
  `webui/Construction-Enterprise-OS---CRUD.html` を生成(再バンドル方式)。
- バンドル構造の解析: manifest(gzip リソース)+ template(HTML/CSS)を展開し、
  アプリ JSX リソース 17 個に CRUD を組み込み、再圧縮して単一 HTML に再構築。
- **全ページ(13 カテゴリ・約 90 ルート)で CRUD を実装**:
  - データ取得(シード: 工事/承認/文書/センサー/アラート/原価/安全/協力会社/ユーザー/
    重機/作業員/契約/請求/GIS/AI/ロボティクス/セキュリティ/システム等 30+ コレクション)
  - 新規作成(モーダルフォーム・必須バリデーション)、編集、削除(確認ダイアログ)
  - hash ルーティング(直接 URL アクセス・リロード・共有に対応)
- 再生成ツール: `scripts/ceos-bundle.py`(unpack/repack)。作業ワークスペースは .bundle-work/(gitignore)。
- デプロイ対象を CRUD 統合版に切替(元バンドルは standalone-prototype.html として保全)。

## 検証結果(ローカル → デプロイ後)

| 確認項目 | 結果 |
|---|---|
| 全 17 リソースの JSX 構文チェック | ✅ Babel 変換 VALID |
| ページ遷移(直接 URL 含む 13 ルート) | ✅ 全て表示 |
| 既存 E2E(mvp.spec.ts) | ローカル 16/16(SPA フォールバック除く)→ デプロイ後 18/18 |
| CRUD E2E(crud.spec.ts) | ✅ 20/20(新規/編集/削除/永続化/タブ) |
| CI | PR で 25/25 GREEN 確認 |
| Pages 自動デプロイ | main push(webui/**)で MVP + 本番両方へ反映 |
