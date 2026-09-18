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

### workflow006 / workflow009 / workflow010 のRollback時の注意

`workflow006`と`workflow010`のRollbackは、`upgrade`後に追加された状態を持つ運用データが
存在する場合、データを無断で削除・統合せず**Rollbackを中断**する設計です。中断時は
`RuntimeError`で該当データの件数・内容を明示します。`workflow009`は`NULL`の`receipt_no`を
既存の採番方式と衝突しない値で自動補完してから`NOT NULL`制約を復元し、Rollbackを継続します。

- **workflow006**（並列承認roleの許可）: Rollback前に`workflow.workflow_approvals`を
  `(instance_id, step_order)`で集計し、複数行(=複数role)が存在する組み合わせがないか
  検証します。重複がある場合、旧一意制約`uq_workflow_approvals_instance_step`を
  再作成できずRollbackは失敗（例外送出）します。
  - **手動復旧手順**: 例外メッセージに出力された`instance_id`/`step_order`ごとに、
    `SELECT * FROM workflow.workflow_approvals WHERE instance_id = ? AND step_order = ?`
    で該当承認行を確認してください。複数roleでの並列承認を今後使わないと判断し、
    意図的に1行へ統合・削除する場合は、業務担当者の承認を得たうえで、どの承認行を
    正とするかを個別に判断し、削除対象を明示したSQLを別途実行してから
    再度`alembic downgrade`を実行してください（本migrationは統合ロジックを自動実行しません）。

- **workflow010**（案件ステータス拡張）: Rollback前に`workflow.workflow_instances`を
  旧status集合（`draft`, `in_progress`, `approved`, `rejected`, `cancelled`）に
  含まれないstatusで検索します。該当案件がある場合、旧CHECK制約を再作成できず
  Rollbackは失敗します。
  - **手動復旧手順**: 例外メッセージに出力されたstatusごとに、
    `SELECT id, status FROM workflow.workflow_instances WHERE status = ?`
    で該当案件を確認してください。旧status集合へ意図的にマッピングする場合
    （例: `submitted`→`in_progress`）は、業務上の妥当性を個別に判断したうえで
    `UPDATE`文を実行し、その後に`alembic downgrade`を再実行してください。

- **workflow009**（提出時受付番号採番・下書きのNULL許容）: Rollbackは
  `receipt_no`が`NULL`の下書き案件を**自動的にバックフィル**してからNOT NULL制約を
  復元します。採番は`workflow005`と同じ形式（`SAW-YYYY-NNNNNN`、
  `row_number() OVER (ORDER BY created_at, id)`）を用い、既存の(NULLでない)最大の
  受付番号の次の値から採番するため、`uq_workflow_instances_receipt_no`
  （`workflow005`で作成、本migrationでは変更しない）との衝突はありません。
  中断は発生しませんが、Rollback後は下書き案件にも受付番号が付与される点に
  注意してください（再度`upgrade`すると当該番号はそのまま残ります）。
