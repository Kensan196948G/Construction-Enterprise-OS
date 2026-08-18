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
