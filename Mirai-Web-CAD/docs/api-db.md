# API/DBメモ

## 予定API

| Method | Path | 用途 |
| --- | --- | --- |
| `GET` | `/api/health` | 実装済み。API/Auth/DB modeを返す |
| `GET` | `/api/drawings/demo` | 実装済み。デモ図面取得 |
| `POST` | `/api/drawings` | 実装済み。図面作成 |
| `GET` | `/api/drawings/:drawingId` | 実装済み。図面取得 |
| `POST` | `/api/drawings/:drawingId/transactions` | 実装済み。CAD Coreコマンド一括適用 |
| `POST` | `/api/drawings/:drawingId/agent-runs` | 実装済み。AI提案作成 |
| `POST` | `/api/agent-runs/:runId/approve` | 実装済み。AI提案を人の承認で適用 |
| `POST` | `/api/drawings/:drawingId/review` | 実装済み。レビュー提出、承認、新版 |
| `GET` | `/api/audit-logs` | 実装済み。承認系権限のみ |

## DB設計方針

- 図面は`drawings`、版は`drawing_versions`、操作は`command_events`へ分離
- AIは`agent_runs`にPrompt、Skill、Proposal、Riskを保存し、直接図面を書き換えない
- 承認は`reviews`へ記録し、承認済み版の上書きを禁止する
- 監査は`audit_logs`へ追記し、次Roundでhash chainを追加する
- Preview APIは現時点でメモリストアを使用する。Neon接続時はこのAPI契約を維持して永続化層だけ差し替える

## セキュリティ方針

- Cloudflare Access/JWT検証をWorker境界でfail-closed
- `Idempotency-Key`と`expectedVersion`を更新APIへ要求
- Tool CallはJSON Schema検証後、サーバー側で再認可
- 図面内文字列はPrompt命令ではなく非信頼データとして扱う

## ローカルAPI検証

```bash
npm run build
wrangler pages dev dist --port=4176
curl http://127.0.0.1:4176/api/health
```
