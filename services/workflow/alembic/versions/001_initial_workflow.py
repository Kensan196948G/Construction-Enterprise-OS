"""Create the workflow schema and tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "workflow001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS workflow")

    op.create_table(
        "workflow_definitions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("steps", JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_by", UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="workflow",
    )
    op.create_index("ix_workflow_definitions_organization_id", "workflow_definitions", ["organization_id"], schema="workflow")
    op.create_index("ix_workflow_definitions_category", "workflow_definitions", ["category"], schema="workflow")

    op.create_table(
        "workflow_instances",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("definition_id", UUID(as_uuid=True), sa.ForeignKey("workflow.workflow_definitions.id")),
        sa.Column("organization_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("reference_type", sa.String(100)),
        sa.Column("reference_id", UUID(as_uuid=True)),
        sa.Column("metadata", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("submitted_by", UUID(as_uuid=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('draft', 'in_progress', 'approved', 'rejected', 'cancelled')", name="ck_workflow_instances_status"),
        sa.CheckConstraint("priority IN ('low', 'normal', 'high', 'urgent')", name="ck_workflow_instances_priority"),
        schema="workflow",
    )
    op.create_index("ix_workflow_instances_organization_id", "workflow_instances", ["organization_id"], schema="workflow")
    op.create_index("ix_workflow_instances_status", "workflow_instances", ["status"], schema="workflow")
    op.create_index("ix_workflow_instances_submitted_by", "workflow_instances", ["submitted_by"], schema="workflow")

    op.create_table(
        "workflow_approvals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("instance_id", UUID(as_uuid=True), sa.ForeignKey("workflow.workflow_instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_order", sa.Integer, nullable=False),
        sa.Column("approver_id", UUID(as_uuid=True)),
        sa.Column("approver_role", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("comment", sa.Text),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("step_order > 0", name="ck_workflow_approvals_step_order"),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_workflow_approvals_status"),
        sa.UniqueConstraint("instance_id", "step_order", name="uq_workflow_approvals_instance_step"),
        schema="workflow",
    )
    op.create_index("ix_workflow_approvals_instance_id", "workflow_approvals", ["instance_id"], schema="workflow")
    op.create_index("ix_workflow_approvals_status", "workflow_approvals", ["status"], schema="workflow")


def downgrade() -> None:
    op.drop_table("workflow_approvals", schema="workflow")
    op.drop_table("workflow_instances", schema="workflow")
    op.drop_table("workflow_definitions", schema="workflow")
    op.execute("DROP SCHEMA workflow")
