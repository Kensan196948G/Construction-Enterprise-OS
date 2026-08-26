# Mirai Web CAD MVP Roundログ

## Round 1 / 2026-08-26

| 項目 | 内容 |
| --- | --- |
| 対象課題 | `Mirai-Web-CAD`配下が要件/設計HTMLのみで、実操作可能なMVPが未存在 |
| 判断理由 | 親リポジトリには大規模な既存差分があり、無関係な変更を混ぜるリスクが高い。対象ディレクトリ内で独立MVPを構築するのが最小安全単位 |
| 変更 | 静的SPA、CAD Core、Canvas UI、AI提案プレビュー、権限/承認、検査、測定、LocalStorage保存、JSON出力、migration/seed、検証スクリプトを追加 |
| 設計整合 | 要件書の「CAD Coreが正、AIは支援」「プレビュー後に人が適用」「ロックレイヤー/承認済み版/権限外更新拒否」をMVP実装へ反映 |
| 検証 | `npm run verify`を2回実行し、lint、Node標準テスト、静的buildが成功 |
| 証拠 | `tests/cad-core.test.js`でロック、権限、AI承認ゲート、承認不可、測定を検査。`curl -I http://127.0.0.1:4174/`でHTTP 200を確認 |
| 残存課題 | Cloudflare Workers API、Neon永続化接続、GitHub PR/CI、Cloudflare Preview、本番Deploy、E2E/Visual/A11y自動検査は未実施 |
| 次Round | Worker APIとNeon接続層を追加し、主要フローをブラウザ内保存からサーバー永続化へ拡張する |

## Completion Gate

| Gate | 状態 | 根拠 |
| --- | --- | --- |
| 主要業務フロー実操作 | CONTINUE | ブラウザMVPで作図、AI提案、レビュー、承認は可能 |
| OpenDesign/仕様整合 | CONTINUE | 仕様HTMLの色/画面領域/AI Gateを反映。OpenDesignの外部正本は未接続 |
| 正常/空/Error/権限別状態 | CONTINUE | 正常・Error・権限は実装。空状態の専用UIは今後強化 |
| Migration/Seed | CONTINUE | SQL雛形あり。実Neon適用は未検証 |
| 型検査/Lint/Test/E2E/Build | CONTINUE | `npm run verify`成功。JS MVPのため型検査は未対象。E2EはPlaywright未導入で未実施 |
| Responsive/Keyboard/A11y | CONTINUE | Responsive CSSと基本focusあり。体系的A11y検査は未実施 |
| Preview/本番Deploy | BLOCKER候補 | Cloudflare/Neon/GitHub権限・Secret確認が必要 |
| 文書更新 | CONTINUE | README、運用、API/DB、Roundログを追加 |
| Critical/High解消 | CONTINUE | Core検査ではCritical承認不可。セキュリティスキャン未実施 |

## 検証結果

| コマンド | 結果 | メモ |
| --- | --- | --- |
| `npm run lint` | PASS | 必須ファイル、JS構文、CSS未解決マーカーを確認 |
| `npm test` | PASS | 6 tests / 6 pass |
| `npm run build` | PASS | `dist/`生成 |
| `npm run verify` | PASS | lint + test + build |
| `curl -I http://127.0.0.1:4174/` | PASS | `HTTP/1.0 200 OK` |
| `rg`簡易secret scan | PASS相当 | 実Secret値なし。`DATABASE_URL`は手順書内の環境変数プレースホルダーのみ |

## Round 2 / 2026-08-26

| 項目 | 内容 |
| --- | --- |
| 対象課題 | ブラウザ内MVPだけで、Cloudflare/API/Auth/状態確認/Preview検証が未達 |
| 判断理由 | Completion Gateの「PreviewでUI/API/認証/DB接続確認」「正常・空・Error・権限別状態」を進めるため、Cloudflare Pages Functions互換APIと画面状態レビューを優先 |
| 変更 | `src/api-handler.js`、`functions/api/[[path]].js`、ローカルAPI統合サーバー、APIテスト、静的A11y検査、State Review UI、Cloudflare Pages Previewを追加 |
| 設計整合 | 更新APIへ`Idempotency-Key`/`expected-version`を要求。`AUTH_MODE=access`ではCloudflare Access情報なしをfail-closed。AIはPlan/Preview後に明示承認でTransaction化 |
| 検証 | `npm run verify`成功、`wrangler pages dev dist --port=4176`成功、Cloudflare Previewへデプロイしエッジ経由APIを確認 |
| 証拠 | Preview URL `https://mvp-round-2.mirai-web-cad.pages.dev/`。`/api/health`は`auth=demo`, `db=memory-preview`。AI承認は`entities=11`, `run=completed`。閲覧者Transactionは403相当の権限拒否 |
| 残存課題 | Neon実接続、Cloudflare Access実設定、GitHub PR/CI、実ブラウザE2E/Visual/axe、OpenDesign外部正本照合、本番Deploy/Release後確認は未完了 |
| 次Round | Neon永続化層、DB migration適用検証、GitHub PR/CI、Playwright導入によるPreview E2Eを進める |

## Round 2 検証結果

| コマンド/対象 | 結果 | メモ |
| --- | --- | --- |
| `npm run lint` | PASS | `src`、`functions`、`tests`、`scripts`のJS構文を確認 |
| `npm run a11y` | PASS | lang、viewport、aria、focus-visible、Responsive CSS等を静的検査 |
| `npm test` | PASS | 12 tests / 12 pass |
| `npm run build` | PASS | `dist/`生成 |
| `wrangler pages dev dist --port=4176` | PASS | Pages Functionsローカル互換起動 |
| Cloudflare Preview SPA | PASS | `https://mvp-round-2.mirai-web-cad.pages.dev/` がHTTP 200 |
| Cloudflare Preview API | PASS | `/api/health`、AI提案承認、viewer更新拒否を確認 |
| Neon migration実適用 | 未実施 | `DATABASE_URL`なし、ローカルPostgreSQL未起動。SQLは`create table if not exists`/`on conflict`で再実行可能性を静的確認 |

## Round 2 Completion Gate

| Gate | 状態 | 根拠 |
| --- | --- | --- |
| 主要業務フロー実操作 | CONTINUE | SPA + APIで作図、AI提案、承認フローを確認。DWG/DXF/PDFと高度CAD機能は未達 |
| OpenDesign/仕様整合 | CONTINUE | 仕様HTMLに沿った画面構成。外部OpenDesign正本は未接続 |
| 正常/空/Error/権限別状態 | CONTINUE | State Reviewと権限切替を実装。実ブラウザE2Eは未実施 |
| Migration/Seed | CONTINUE | SQLあり。実Neon適用未実施 |
| 型検査/Lint/Test/E2E/Build | CONTINUE | lint/a11y/test/build成功。型検査とPlaywright E2Eは未導入 |
| PreviewでUI/API/認証/DB | CONTINUE | Cloudflare PreviewでUI/API/Auth demo確認。DBは`memory-preview`でNeon未接続 |
| Critical/High解消 | CONTINUE | 権限/承認/ロックのCritical相当テストあり。依存脆弱性/Secret ScanのCI Gate未実施 |
