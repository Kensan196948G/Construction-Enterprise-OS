"""Persist duplicate judgement and canonical storage state."""

from alembic import op
import sqlalchemy as sa


revision = "workflow008"
down_revision = "workflow007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workflow_instances",
        sa.Column("duplicate_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
        schema="workflow",
    )
    op.add_column(
        "workflow_instances",
        sa.Column("canonical_stored_at", sa.DateTime(timezone=True), nullable=True),
        schema="workflow",
    )
    op.add_column(
        "workflow_instances",
        sa.Column("canonical_error", sa.Text(), nullable=True),
        schema="workflow",
    )
    op.alter_column("workflow_instances", "duplicate_flag", server_default=None, schema="workflow")


def downgrade() -> None:
    op.drop_column("workflow_instances", "canonical_error", schema="workflow")
    op.drop_column("workflow_instances", "canonical_stored_at", schema="workflow")
    op.drop_column("workflow_instances", "duplicate_flag", schema="workflow")
