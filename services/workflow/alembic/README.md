# Workflow Database Migration

Workflow serviceのテーブルは、このディレクトリのAlembicで管理します。

```bash
cd services/workflow
alembic upgrade head
```

接続先は`DATABASE_URL`環境変数から取得します。Migrationは`workflow` Schemaと、定義・申請・承認・状態履歴のテーブル、定義マスタの提出チェックルール、案件期限、外部連携用の受付番号を管理します。`workflow002`以降は既存テーブルへ追加するMigrationで、既存データを削除しません。

定義作成時の`check_rules`には、例えば次のように必須項目・必要資料・期限ルールを設定できます。

```json
{
  "required_fields": ["construction_code", "target_year_month"],
  "required_attachments": ["申請書"],
  "deadline_rule": "MONTHLY_DAY:5"
}
```

案件作成時に`metadata.deadline`を指定すると、定義の期限ルールより優先されます。提出時の必須項目・資料不足はエラー、工事マスタ情報の不一致は警告として返します。

下書き作成時は`receipt_no`をNULLとし、提出トランザクション内で`SAW-YYYY-NNNNNN`形式の番号を採番します。年次カウンタは`workflow_receipt_counters`で管理し、受付番号は案件一覧・通知・外部ファイル連携で共通キーとして使用します。UUIDの内部IDとは分離します。

`workflow009`は既存受付番号を年別カウンタへ移行し、下書きの受付番号をNULL許容にします。`workflow010`は実装および仕様で使用する案件ステータスをDB制約へ反映します。

承認ステップは従来の`role`に加えて`roles`配列を指定できます。同じ`order`の複数roleは同時回付として別々の承認行に展開されます。`workflow006`は既存承認行を変更せず、同一案件・同一stepの複数roleを許可する制約へ変更します。

`workflow007`は案件単位の問い合わせ履歴を追加します。質問は`phone`、
`email`、`system`のチャネルを持ち、回答済みになると回答者と回答日時を保持します。
APIは次のとおりです。

- `POST /api/v1/workflow/instances/{instance_id}/inquiries`
- `GET /api/v1/workflow/instances/{instance_id}/inquiries`
- `POST /api/v1/workflow/instances/{instance_id}/inquiries/{inquiry_id}/answer`

Migration適用後にのみQ&A APIを有効化してください。既存案件と同じ組織の
問い合わせだけを参照・更新できます。

適用前に対象DBのバックアップまたは復旧地点を確認してください。Rollbackは、対象環境と適用済みRevisionを確認したうえで、次を実行します。

```bash
alembic downgrade -1
```

`alembic downgrade -1`は直前のMigrationだけを戻します。`workflow004`のRollbackは案件期限列のみ、`workflow003`のRollbackは定義チェックルール列のみを削除します。Workflow Schema全体を戻す場合は全RevisionのRollbackとなるため、Workflowデータが存在する環境では実行前承認が必要です。
