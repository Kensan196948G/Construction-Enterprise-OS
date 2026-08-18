# デプロイ・ドメイン運用

## 1. ドメイン方針(2026-08-18 確定)

| 用途 | サブドメイン | 状態 |
|---|---|---|
| 本番環境 | `construction-os.mirai-dx-platform.com` | 新規取得 |
| MVPプロトタイプ | `construction-os-mvp.mirai-dx-platform.com` | 新規取得 |

- 親ドメイン `mirai-dx-platform.com` は Cloudflare(取得済み・active)。
- DNS は Cloudflare Pages/Worker のカスタムドメインとして管理。

## 2. デプロイアーキテクチャ(家族パターン準拠)

既存プロジェクト(OBCDA/PIMM/CEOP)のパターンを踏襲:

| 層 | 方式 |
|---|---|
| フロントエンド | Cloudflare Pages(`construction-os-web` / `construction-os-mvp`) |
| バックエンド API | FastAPI サービス群を docker-compose で稼働 + Cloudflare Tunnel で公開(CEOP 方式) |
| データベース | Neon PostgreSQL(`construction-enterprise-os` プロジェクト) |

- MVP プロトタイプ: OpenDesign スタンドアロンプロトタイプ(単一HTML)を Pages で即時公開
- 本番: Next.js ビルドを Pages へ、API を Tunnel 経由で接続

## 3. デプロイ手順(未実施項目は実施時に更新)

- [ ] Pages プロジェクト作成(`construction-os-web`, `construction-os-mvp`)
- [ ] カスタムドメイン追加(上記サブドメイン)
- [ ] GitHub Actions から Pages への自動デプロイ(workflow 追加)
- [ ] Tunnel 用 cloudflared 設定(API 公開)
- [ ] ロールバック手順(前回デプロイへの即時復帰)の確立

## 4. ロールバック方針

- Pages: 直前の正常デプロイメントへ Rollback(Cloudflare API 対応済み)
- Tunnel: コンテナのタグ指定による再起動
- DB: Neon の Point-in-Time 復元 / ブランチ切り替え
