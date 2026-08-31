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
        sa.Column(
            "receipt_year", sa.Integer(), primary_key=True, autoincrement=False
        ),
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
    op.alter_column(
        "workflow_instances", "receipt_no", nullable=False, schema="workflow"
    )
    op.drop_table("workflow_receipt_counters", schema="workflow")
