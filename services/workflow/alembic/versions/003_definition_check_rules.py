"""Add master-driven submission check rules to workflow definitions."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "workflow003"
down_revision = "workflow002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workflow_definitions",
        sa.Column("check_rules", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        schema="workflow",
    )


def downgrade() -> None:
    op.drop_column("workflow_definitions", "check_rules", schema="workflow")
