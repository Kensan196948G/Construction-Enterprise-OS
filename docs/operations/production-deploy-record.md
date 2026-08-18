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
