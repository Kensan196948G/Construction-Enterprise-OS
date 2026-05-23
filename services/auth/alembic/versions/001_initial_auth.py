"""Alembic 初期リビジョン - 認証スキーマ作成"""

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 初回は models/__init__.py の Base.metadata.create_all で作成
    # 本番ではここにDDLを記述
    pass


def downgrade() -> None:
    pass
