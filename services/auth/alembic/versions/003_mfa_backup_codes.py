"""Add hashed MFA backup codes to auth.users.

Revision ID: 003
Revises: 002
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

SCHEMA = "auth"


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("mfa_backup_codes", postgresql.JSONB, nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("users", "mfa_backup_codes", schema=SCHEMA)
