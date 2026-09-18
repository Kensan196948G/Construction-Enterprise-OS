"""Allow multiple approval roles at the same workflow step."""

from alembic import op
import sqlalchemy as sa

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
    bind = op.get_bind()
    duplicates = bind.execute(
        sa.text(
            """
            SELECT instance_id, step_order, COUNT(*) AS cnt
            FROM workflow.workflow_approvals
            GROUP BY instance_id, step_order
            HAVING COUNT(*) > 1
            ORDER BY instance_id, step_order
            """
        )
    ).fetchall()
    if duplicates:
        detail = "; ".join(
            f"instance_id={row.instance_id} step_order={row.step_order} ({row.cnt}件)"
            for row in duplicates
        )
        raise RuntimeError(
            "workflow006のdowngradeを中断しました。"
            "同一案件・同一ステップに複数roleの承認行が存在するため、"
            "旧一意制約(instance_id, step_order)を再作成できません。"
            f"重複箇所: {detail}。"
            "復旧手順はalembic/README.mdを参照してください。"
        )
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
