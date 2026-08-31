# desknet's NEO連携

Notification Serviceは、テンプレートの`neo`チャネルを
`NEO_API_URL`へHTTP POSTして配送します。desknet's NEO本体のAPI仕様や契約オプションは
導入環境で異なるため、接続先には社内のNEO APIゲートウェイを指定し、必要なユーザーID
変換・署名・固有payload変換はゲートウェイ側で行います。

## 設定

```sh
NEO_ENABLED=true
NEO_API_URL=https://internal.example.invalid/neo/notifications
NEO_API_KEY=<Secret Managerから注入>
NEO_TIMEOUT_SECONDS=5
```

`NEO_API_KEY`はRepository、ログ、URLクエリへ保存しません。`NEO_ENABLED=false`の場合は
アプリ内通知を維持し、NEO配送を行いません。`NEO_ENABLED=true`でURLまたはキーが欠けている
場合は通知を`failed`として、送信済みとは扱いません。

## Gateway契約

Requestは次のJSONとBearer認証で送信します。

```json
{
  "recipient_id": "user-uuid",
  "subject": "通知件名",
  "body": "通知本文",
  "metadata": {"source": "workflow"},
  "idempotency_key": "workflow-event-recipient"
}
```

GatewayはHTTP 2xxを受信成功とし、同じ`Idempotency-Key`を再送しても一度だけNEOへ
配信します。4xx/5xx、タイムアウト、TLSエラーはNotificationを`failed`として残し、
呼び出し元のジョブが再試行できるようにします。

## 開封・応答callback

NEO APIゲートウェイは`POST /api/v1/notification/webhooks/neo/callback`へ、JSON本文の
HMAC-SHA256 hex digestを`X-NEO-Signature`ヘッダーで送信します。署名鍵は
`NEO_WEBHOOK_SECRET`です。callbackでは`notification_id`と`idempotency_key`を照合し、
`opened`、`read`、`responded`、`acknowledged`を既読として記録し、応答内容・時刻を
`metadata.neo_callback`へ保存します。不正署名や照合不能な通知は拒否します。
Workflow ServiceのURLと内部ジョブキーを設定した場合、同じcallbackをWorkflowの
追記専用監査ログへ冪等反映します。開封・応答で案件ステータスは変更しません。

実NEOでの確認項目は、ユーザーID変換、受付番号を含む件名・本文、受信者表示、重複排除、
障害時の再送、開封・応答結果のWorkflow反映です。
