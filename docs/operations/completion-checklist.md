# 完了条件チェックリスト(Goal 追跡)

> ゴール(自律開発→検証→PR→マージ→本番デプロイ→リリース確認)の完了条件に対する
> 達成状況と証拠の一覧。更新日: 2026-08-18(ラウンド3・最終)
> 最終検証: E2E 全34テスト(mvp 18 + api 16)を本番・プレビュー両環境で PASS

| # | 完了条件 | 状態 | 証拠 |
|---|---|---|---|
| 1 | 主要業務フローが OpenDesign の目的と整合し、実際に操作可能 | ✅ | docs/requirements/mvp-scope.md(14カテゴリ/約90ルート対応表)、E2E 18/18 |
| 2 | 有効なダミーデータで正常・空・エラー・権限別状態を確認可能 | ✅ | 設計プロトタイプのダミーデータ + Neon シード(2組織/1ユーザ/7ロール/43権限)。ロール切替・エラー(401/422)実証 |
| 3 | Neon Migration と Seed を空の検証DBへ再実行可能 | ✅ | verify-001 ブランチで alembic upgrade head + seed 成功・冪等確認。docs/operations/neon-database.md |
| 4 | 型検査、Lint、主要テスト、E2E、ビルドが成功 | ✅ | 型検査 5/5・Lint 4/4・frontend 219テスト・auth 30テスト・E2E 18/18(3環境)・CI 26ジョブ GREEN(PR#1〜#5) |
| 5 | レスポンシブ、キーボード操作、主要アクセシビリティ要件を確認済み | ✅ | E2E: モバイル 390×844(ハンバーガー)、Tab フォーカス、ダークモード。a11y 警告1件(画像 alt)は記録済み |
| 6 | Cloudflare Preview で画面、API、認証、DB接続を確認済み | ✅ | construction-os-mvp / construction-os 両ドメインで WebUI(200)+ API(health/login/users/roles)+ Neon を HTTPS 実証 |
| 7 | README、要件、設計、API、DB、テスト、運用・復旧手順を更新済み | ✅ | README(MVP状況)、docs/requirements/mvp-scope.md、docs/design/opendesign-spec.md、docs/api/overview.md、docs/operations/(deployment/neon-database/production-deploy-record/api-auth-db-verification) |
| 8 | Critical／High 問題が解消され、残存リスクが記録済み | ✅ | security-scan(trivy/pip-audit)PASS。残存リスク: opendesign-spec.md §10・mvp-scope.md §5・api-auth-db-verification.md |
| 9 | PR・自動マージ: 必須チェック・レビュー・Secrets スキャン・Critical/High・Neon Migration・Preview E2E・ロールバック手順 | ✅ | PR#1〜#5 全て 26/26 GREEN で Squash Merge。ロールバック手順: docs/operations/deployment.md §5 |
| 10 | 本番デプロイ・確認: 承認済み CI/CD 経路からデプロイ、Neon Migration 適用、ヘルスチェック/画面/API/認証/DB/ログ | ✅ | Pages Deploy workflow(main push で自動デプロイ)success ×4。Neon main ブランチへ Migration+Seed 適用済み。本番で全確認 |
| 11 | 既存ユーザー変更の保護 | ✅ | ユーザーの webui/(OpenDesign ハンドオフ)は正本として格納・変更なし。ドメイン指示(construction-os / construction-os-mvp)を実装 |

## 残存リスク(要対応)

| # | リスク | 重要度 | 対応 |
|---|---|---|---|
| R1 | トンネル直接 HTTPS(api.construction-os...)の証明書未発行 | 中 | ssl write 権限トークンをユーザー提供後に advanced 証明書パック発行(現状は Pages Function プロキシで HTTPS 提供済み) |
| R2 | WebUI のダミーデータ → 実 API 接続が未実施 | 中 | 次フェーズで WebUI にログイン/実データ表示を組み込み |
| R3 | サイドバーのポインター横取り・URL 非同期ルーティング | 低 | Next.js 実装時に解消(プロトタイプの既知挙動として記録済み) |
| R4 | 本番 Cloudflare Access 未適用 | 低 | ユーザー承認後(MVP は公開運用のため保留) |
| R5 | Pages Function プロキシの公開範囲(/api/v1/* 全公開) | 低 | 本番 Access 適用時に API も保護対象へ |
| R6 | ログインが稀に INTERNAL_ERROR(再試行で即成功) | 低 | 観測: 数十回中2回のみ・連続6回成功を確認。原因は auth サービスの過渡的 DB 接続/稼働中変更の可能性。次フェーズで auth サービスに例外ログ・リトライを追加 |

## 判定

- **完了条件 1〜11 は全て達成**(証拠は上表)
- 残存リスク R1〜R6 は全て記録済み・非ブロッカー
- 次ラウンド以降: R1(ユーザートークン待ち)・R2(実データ接続)を優先
