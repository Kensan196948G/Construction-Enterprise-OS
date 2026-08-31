"""Allow the statuses used by the case workflow and specification."""

from alembic import op

revision = "workflow010"
down_revision = "workflow009"
branch_labels = None
depends_on = None

_STATUSES = (
    "draft",
    "submitted",
    "received",
    "in_progress",
    "deficiency_review",
    "rejected",
    "resubmission_pending",
    "forwarded",
    "pending_approval",
    "processing",
    "approved",
    "completed",
    "stored",
    "cancelled",
)


def upgrade() -> None:
    op.drop_constraint(
        "ck_workflow_instances_status", "workflow_instances", schema="workflow"
    )
    values = ", ".join(f"'{status}'" for status in _STATUSES)
    op.create_check_constraint(
        "ck_workflow_instances_status",
        "workflow_instances",
        f"status IN ({values})",
        schema="workflow",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_workflow_instances_status", "workflow_instances", schema="workflow"
    )
    op.create_check_constraint(
        "ck_workflow_instances_status",
        "workflow_instances",
        "status IN ('draft', 'in_progress', 'approved', 'rejected', 'cancelled')",
        schema="workflow",
    )
