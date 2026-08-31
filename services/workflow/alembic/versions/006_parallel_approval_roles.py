"""Allow multiple approval roles at the same workflow step."""

from alembic import op

revision = "workflow006"
down_revision = "workflow005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_workflow_approvals_instance_step",
        "workflow_approvals",
        schema="workflow",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_workflow_approvals_instance_step_role",
        "workflow_approvals",
        ["instance_id", "step_order", "approver_role"],
        schema="workflow",
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_workflow_approvals_instance_step_role",
        "workflow_approvals",
        schema="workflow",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_workflow_approvals_instance_step",
        "workflow_approvals",
        ["instance_id", "step_order"],
        schema="workflow",
    )
