"""Add a stable receipt number for cross-system workflow references."""

from alembic import op
import sqlalchemy as sa

revision = "workflow005"
down_revision = "workflow004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS workflow.workflow_receipt_seq")
    op.add_column(
        "workflow_instances",
        sa.Column("receipt_no", sa.String(30), nullable=True),
        schema="workflow",
    )
    op.execute(
        """
        WITH numbered AS (
            SELECT id, format('SAW-%s-%s', EXTRACT(YEAR FROM created_at)::int,
                lpad(row_number() OVER (ORDER BY created_at, id)::text, 6, '0')) AS receipt_no
            FROM workflow.workflow_instances
        )
        UPDATE workflow.workflow_instances AS instance
        SET receipt_no = numbered.receipt_no
        FROM numbered
        WHERE instance.id = numbered.id
        """
    )
    op.execute(
        "SELECT setval('workflow.workflow_receipt_seq', GREATEST(COALESCE((SELECT count(*) FROM workflow.workflow_instances), 0), 1), true)"
    )
    op.alter_column("workflow_instances", "receipt_no", nullable=False, schema="workflow")
    op.create_unique_constraint(
        "uq_workflow_instances_receipt_no", "workflow_instances", ["receipt_no"], schema="workflow"
    )


def downgrade() -> None:
    op.drop_constraint("uq_workflow_instances_receipt_no", "workflow_instances", schema="workflow")
    op.drop_column("workflow_instances", "receipt_no", schema="workflow")
    op.execute("DROP SEQUENCE IF EXISTS workflow.workflow_receipt_seq")
