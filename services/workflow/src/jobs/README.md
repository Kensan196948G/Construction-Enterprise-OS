# Workflow jobs

期限通知は、外部Schedulerから内部APIを日次で呼び出します。Workflowと
Notificationの両方に同じ `NOTIFICATION_INTERNAL_API_KEY` を設定し、
Workflowには別途 `INTERNAL_JOB_API_KEY` を設定してください。

```sh
curl -fsS -X POST \
  -H "X-Internal-API-Key: ${WORKFLOW_INTERNAL_JOB_API_KEY}" \
"${WORKFLOW_SERVICE_URL}/api/v1/workflow/internal/jobs/deadline-notifications"
```

## Workload alerts

処理量集計ジョブは次の内部APIを定期実行する。

```text
POST ${WORKFLOW_SERVICE_URL}/api/v1/workflow/internal/jobs/workload-notifications
X-Internal-API-Key: ${WORKFLOW_INTERNAL_JOB_API_KEY}
```

案件metadataの`region`または`branch`単位で当月件数を集計し、直近12か月平均に対して
`WORKLOAD_ALERT_RATIO`を超えた場合に`workflow.load_alert`と`workflow.support_request`を送信する。
期限ジョブの対象は `in_progress`、`forwarded`、`pending_approval`、`processing` かつ期限が設定された案件で、期限7日前・3日前・
前日・当日・超過翌日に通知します。通知失敗はジョブの集計に含まれ、
Workflow本体の状態は変更しません。送信の重複防止はNotification側の
`idempotency_key` 一意インデックスに依存します。

両ジョブをcronから実行する場合は、Repositoryの`scripts/run-workflow-jobs.sh`を使用します。
`WORKFLOW_SERVICE_URL`と`WORKFLOW_INTERNAL_JOB_API_KEY`はSecret管理下から注入してください。

承認完了時の添付正本保存はDocument Serviceの内部APIを呼び出します。
通信障害・429・5xxは初回を含め最大4試行（最大3回リトライ）し、4xxは
即時失敗としてログへ記録します。`DOCUMENT_SERVICE_URL`、
`DOCUMENT_INTERNAL_API_KEY`、`DOCUMENT_RETRY_COUNT`を設定してください。
