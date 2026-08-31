"""Add case-scoped inquiry and answer history."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "workflow007"
down_revision = "workflow006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_inquiries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("instance_id", UUID(as_uuid=True), sa.ForeignKey("workflow.workflow_instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", UUID(as_uuid=True), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("channel", sa.String(20), nullable=False, server_default="system"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("asked_by", UUID(as_uuid=True), nullable=False),
        sa.Column("answered_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("channel IN ('phone', 'email', 'system')", name="ck_workflow_inquiries_channel"),
        sa.CheckConstraint("status IN ('open', 'answered')", name="ck_workflow_inquiries_status"),
        schema="workflow",
    )
    op.create_index("ix_workflow_inquiries_instance_id", "workflow_inquiries", ["instance_id"], schema="workflow")
    op.create_index("ix_workflow_inquiries_organization_id", "workflow_inquiries", ["organization_id"], schema="workflow")


def downgrade() -> None:
    op.drop_table("workflow_inquiries", schema="workflow")
