"""Add workflow status transition history."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "workflow002"
down_revision = "workflow001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_status_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("instance_id", UUID(as_uuid=True), sa.ForeignKey("workflow.workflow_instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_status", sa.String(20)),
        sa.Column("to_status", sa.String(20), nullable=False),
        sa.Column("changed_by", UUID(as_uuid=True), nullable=False),
        sa.Column("comment", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="workflow",
    )
    op.create_index("ix_workflow_status_history_instance_id", "workflow_status_history", ["instance_id"], schema="workflow")
    op.create_index("ix_workflow_status_history_created_at", "workflow_status_history", ["created_at"], schema="workflow")


def downgrade() -> None:
    op.drop_table("workflow_status_history", schema="workflow")
