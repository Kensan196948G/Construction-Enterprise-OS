"""Add calculated due dates to workflow instances."""

from alembic import op
import sqlalchemy as sa

revision = "workflow004"
down_revision = "workflow003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workflow_instances",
        sa.Column("due_date", sa.Date(), nullable=True),
        schema="workflow",
    )


def downgrade() -> None:
    op.drop_column("workflow_instances", "due_date", schema="workflow")
