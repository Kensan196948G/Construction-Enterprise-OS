"""Allow the statuses used by the case workflow and specification."""

from alembic import op
import sqlalchemy as sa

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

_LEGACY_STATUSES = ("draft", "in_progress", "approved", "rejected", "cancelled")


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
    bind = op.get_bind()
    legacy_values = ", ".join(f"'{status}'" for status in _LEGACY_STATUSES)
    offending = bind.execute(
        sa.text(
            f"""
            SELECT status, COUNT(*) AS cnt
            FROM workflow.workflow_instances
            WHERE status NOT IN ({legacy_values})
            GROUP BY status
            ORDER BY status
            """
        )
    ).fetchall()
    if offending:
        detail = "; ".join(f"{row.status} ({row.cnt}件)" for row in offending)
        raise RuntimeError(
            "workflow010のdowngradeを中断しました。"
            "旧status集合に含まれない案件が存在するため、"
            "旧CHECK制約を再作成できません。"
            f"該当status: {detail}。"
            "復旧手順はalembic/README.mdを参照してください。"
        )
    op.drop_constraint(
        "ck_workflow_instances_status", "workflow_instances", schema="workflow"
    )
    op.create_check_constraint(
        "ck_workflow_instances_status",
        "workflow_instances",
        "status IN ('draft', 'in_progress', 'approved', 'rejected', 'cancelled')",
        schema="workflow",
    )
