# API・認証・DB 接続の統合検証記録

## 日時
- 2026-08-18(ラウンド2)

## 構成
- auth サービス(FastAPI)をローカル起動(port 18002)
- DB: **Neon `construction-enterprise-os` main ブランチ**(Migration 001 + Seed 適用済み)
- 検証: 実 HTTP リクエスト(ログイン → JWT → 認証付き API)

## 検証結果

| 確認項目 | エンドポイント | 結果 |
|---|---|---|
| ヘルスチェック | `GET /api/v1/health/services` | ✅ 全サービス healthy(auth 12ms 等) |
| 認証(ログイン) | `POST /api/v1/auth/login` | ✅ JWT 発行(roles: [admin]、org 付き) |
| 認可(トークン検証) | `GET /api/v1/users`(Bearer) | ✅ シード済み管理ユーザーを Neon から返却 |
| 認可(ロール) | `GET /api/v1/roles?organization_id=...`(Bearer) | ✅ admin ロール + 権限(users.read 等)を返却 |
| DB 接続 | 上記 API 経由 | ✅ 全て Neon(PostgreSQL 18)から応答 |

## ログイン資格情報(シード)

- メール: `admin@mirai-dx-platform.com`
- パスワード: `AdminPass123!`(開発用)

## 発見・修正した問題

1. **シード管理ユーザーのメールアドレスが `.local` ドメイン**のため、
   `EmailStr` 検証(Pydantic)でログイン API が 422 を返す不具合を発見。
   - 修正: `services/auth/src/seed.py` の `ADMIN_EMAIL` を
     `admin@mirai-dx-platform.com` へ変更、既存 DB のレコードも UPDATE 済み
   - auth サービス pytest 30件 PASS で回帰なし

## 残課題(次フェーズ)

- API の恒久公開: cloudflared Tunnel で
  `api.construction-os.mirai-dx-platform.com` 等を公開し、Preview 配下で API 確認
- WebUI のダミーデータ → auth API 実データへの接続
- 本番用 JWT 鍵・MFA・Secrets 管理の整備

## HTTPS 経由の検証(本番ドメイン、Pages Function プロキシ)

`https://construction-os.mirai-dx-platform.com/api/v1/*` を Pages Function
(`webui/functions/api/[[path]].ts`)が Cloudflare Tunnel
(`api.construction-os.mirai-dx-platform.com`、HTTP)へ転送する構成。

| 確認項目 | 結果 |
|---|---|
| `GET /api/v1/health/services`(HTTPS) | ✅ 全サービス healthy |
| `POST /api/v1/auth/login`(HTTPS) | ✅ JWT 発行(roles: admin) |
| `GET /api/v1/users`(Bearer・HTTPS) | ✅ シード済みユーザーを Neon から返却 |
| `GET /api/v1/roles`(Bearer・HTTPS) | ✅ 7ロール返却 |

※ トンネルホスト名(api.construction-os...)自体の HTTPS 証明書は
ゾーンの advanced 証明書パック追加が必要(ssl write 権限がトークンに無いため未実施)。
Pages Function 経由で本番ドメインの HTTPS から API を利用可能。
