"""Add mfa_session_uses table for single-use MFA session tokens.

Revision ID: 004
Revises: 003
"""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None

SCHEMA = "auth"


def upgrade() -> None:
    op.create_table(
        "mfa_session_uses",
        sa.Column("jti", sa.String(64), primary_key=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_mfa_session_uses_expires_at",
        "mfa_session_uses",
        ["expires_at"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mfa_session_uses_expires_at",
        table_name="mfa_session_uses",
        schema=SCHEMA,
    )
    op.drop_table("mfa_session_uses", schema=SCHEMA)
