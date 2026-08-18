# デプロイ・ドメイン運用

## 1. ドメイン方針(2026-08-18 確定)

| 用途 | サブドメイン | 状態 |
|---|---|---|
| 本番環境 | `construction-os.mirai-dx-platform.com` | 新規取得・CNAME 設定済み |
| MVPプロトタイプ | `construction-os-mvp.mirai-dx-platform.com` | 新規取得・CNAME 設定済み |

- 親ドメイン `mirai-dx-platform.com` は Cloudflare(取得済み・active、zone: `e375e651e49a40801a305b89e297bff0`)。
- DNS: Pages カスタムドメインとして管理(CNAME + プロキシ)。

## 2. デプロイアーキテクチャ(家族パターン準拠)

既存プロジェクト(OBCDA/PIMM/CEOP)のパターンを踏襲:

| 層 | 方式 |
|---|---|
| フロントエンド | Cloudflare Pages(`construction-os-web` / `construction-os-mvp`) |
| バックエンド API | FastAPI サービス群を docker-compose で稼働 + Cloudflare Tunnel で公開(CEOP 方式) |
| データベース | Neon PostgreSQL(`construction-enterprise-os` プロジェクト / `lucky-art-65407624`) |

## 3. 現在の構成(2026-08-18 実施済み)

| 項目 | 値 |
|---|---|
| Pages プロジェクト(MVP) | `construction-os-mvp` → `construction-os-mvp.pages.dev` |
| Pages プロジェクト(本番) | `construction-os-web` → `construction-os-web.pages.dev` |
| MVP カスタムドメイン | `construction-os-mvp.mirai-dx-platform.com` → CNAME `construction-os-mvp.pages.dev` |
| 本番カスタムドメイン | `construction-os.mirai-dx-platform.com` → CNAME `construction-os-web.pages.dev` |
| MVP コンテンツ | `webui/`(OpenDesign ハンドオフ)を `index.html` としてデプロイ |
| 自動デプロイ | `.github/workflows/pages-deploy.yml`(main への `webui/**` push で MVP と本番の両 Pages へ deploy) |
| GitHub Secrets | `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` |

## 4. デプロイ対象プロジェクト(2026-08-18 拡張)

`pages-deploy.yml` は matrix(`construction-os-mvp` / `construction-os-web`)で
**MVP と本番の両プロジェクトへ同一内容を自動デプロイ**する。

- 本番(`construction-os-web`)は MVP フェーズではプロトタイプ(webui)を配信。
- 本番検証: `https://construction-os.mirai-dx-platform.com` で
  ヘルスチェック(HTTP 200)・主要画面・E2E を確認済み。

## 5. 手動デプロイ(MVP WebUI)

```bash
CLOUDFLARE_API_TOKEN=*** CLOUDFLARE_ACCOUNT_ID=4f1e888469df7e0b896bb4e211b12633 \
  wrangler pages deploy .deploy-webui --project-name construction-os-mvp --branch main
```

※ `.deploy-webui` の準備は `.github/workflows/pages-deploy.yml` の
「Prepare deploy directory」ステップと同一手順。本番へは
`--project-name construction-os-web` で同一内容をデプロイする。

## 6. ロールバック方針

- Pages: 直前の正常デプロイメントへ Rollback(Cloudflare API `POST /deployments/{id}/rollback` 対応済み)
- Tunnel: コンテナのタグ指定による再起動
- DB: Neon の Point-in-Time 復元 / ブランチ切り替え

## 7. 未実施(次フェーズ)

- [ ] 本番(`construction-os-web`)への Next.js ビルドデプロイ(現状は MVP プロトタイプを配信)
- [ ] Tunnel 用 cloudflared 設定(API 公開)
- [ ] Cloudflare Access による認証ゲート(MVP は公開、本番は Access 適用)
