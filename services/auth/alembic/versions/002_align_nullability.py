"""Align auth column nullability with the ORM models.

`001_initial_auth` で作成したテーブルの一部カラムは `nullable=False` を
指定していなかったため、実際のスキーマでは NULL を許容していた。一方
`services/auth/src/models/__init__.py` は `Mapped[str]` / `Mapped[bool]`
(非 Optional)として定義しており、NOT NULL を意図している。

この乖離は、DB 側にだけ NULL が入った場合に読み取り API が
バリデーションエラー(HTTP 500)になる余地を残す。モデルに合わせて
NOT NULL を付与する。

NULL が既に存在するカラムがあれば **ALTER は失敗する**(データを書き換えない)。
その場合は NULL 行を解消してから再実行すること。

Revision ID: 002
Revises: 001
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

SCHEMA = "auth"

# (テーブル, カラム, 事前に NULL を埋めるための server_default 式 or None)
NOT_NULL_COLUMNS: list[tuple[str, str, str | None]] = [
    ("audit_logs", "created_at", "now()"),
    ("organizations", "status", None),
    ("organizations", "created_at", "now()"),
    ("organizations", "updated_at", "now()"),
    ("api_clients", "status", None),
    ("api_clients", "created_at", "now()"),
    ("api_clients", "updated_at", "now()"),
    ("roles", "organization_id", None),
    ("roles", "is_system", "false"),
    ("roles", "created_at", "now()"),
    ("users", "locale", "'ja'"),
    ("users", "status", None),
    ("users", "mfa_enabled", "false"),
    ("users", "password_changed_at", "now()"),
    ("users", "login_attempts", "0"),
    ("users", "created_at", "now()"),
    ("users", "updated_at", "now()"),
    ("refresh_tokens", "created_at", "now()"),
    ("user_roles", "assigned_at", "now()"),
]


def _null_count(table: str, column: str) -> int:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(f'SELECT count(*) FROM {SCHEMA}."{table}" WHERE "{column}" IS NULL')
    )
    return int(result.scalar() or 0)


def upgrade() -> None:
    orphans = [
        f"{table}.{column}"
        for table, column, _ in NOT_NULL_COLUMNS
        if _null_count(table, column) > 0
    ]
    if orphans:
        # データを勝手に書き換えない。解消してから再実行してもらう。
        raise RuntimeError(
            "NULL が存在するため NOT NULL を付与できません。先に解消してください: "
            + ", ".join(orphans)
        )

    for table, column, _ in NOT_NULL_COLUMNS:
        op.alter_column(
            table,
            column,
            schema=SCHEMA,
            existing_type=None,
            nullable=False,
        )


def downgrade() -> None:
    for table, column, _ in NOT_NULL_COLUMNS:
        op.alter_column(
            table,
            column,
            schema=SCHEMA,
            existing_type=None,
            nullable=True,
        )
