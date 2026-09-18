"""Issue receipt numbers at submission and keep yearly counters."""

from alembic import op
import sqlalchemy as sa

revision = "workflow009"
down_revision = "workflow008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_receipt_counters",
        sa.Column("receipt_year", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("next_value", sa.BigInteger(), nullable=False),
        schema="workflow",
    )
    op.execute(
        """
        INSERT INTO workflow.workflow_receipt_counters (receipt_year, next_value)
        SELECT EXTRACT(YEAR FROM created_at)::int,
               MAX(SUBSTRING(receipt_no FROM '[0-9]+$')::bigint) + 1
        FROM workflow.workflow_instances
        WHERE receipt_no IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM created_at)::int
        """
    )
    op.alter_column(
        "workflow_instances", "receipt_no", nullable=True, schema="workflow"
    )


def downgrade() -> None:
    # workflow005の採番方式(SAW-YYYY-NNNNNN, row_number() OVER (ORDER BY
    # created_at, id))と同じ形式でNULLのreceipt_noをバックフィルする。
    # 既存の(NULLでない)最大の受付番号の次から採番し、uq_workflow_instances_receipt_no
    # (workflow005で作成され、本migrationのupgrade/downgradeでは変更しない)との
    # 衝突を避ける。
    op.execute(
        """
        WITH max_receipt AS (
            SELECT COALESCE(
                MAX(SUBSTRING(receipt_no FROM '[0-9]+$')::bigint), 0
            ) AS max_no
            FROM workflow.workflow_instances
            WHERE receipt_no IS NOT NULL
        ),
        numbered AS (
            SELECT id, created_at,
                   row_number() OVER (ORDER BY created_at, id) AS rn
            FROM workflow.workflow_instances
            WHERE receipt_no IS NULL
        )
        UPDATE workflow.workflow_instances AS instance
        SET receipt_no = format(
            'SAW-%s-%s',
            EXTRACT(YEAR FROM numbered.created_at)::int,
            lpad((numbered.rn + max_receipt.max_no)::text, 6, '0')
        )
        FROM numbered, max_receipt
        WHERE instance.id = numbered.id
        """
    )
    op.alter_column(
        "workflow_instances", "receipt_no", nullable=False, schema="workflow"
    )
    op.drop_table("workflow_receipt_counters", schema="workflow")
