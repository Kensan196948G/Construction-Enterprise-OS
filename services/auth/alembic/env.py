"""Alembic 環境設定"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.config import get_settings
from src.models.base import Base

# Alembic Configオブジェクト
config = context.config

# ロギング設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# マイグレーション対象のメタデータ
target_metadata = Base.metadata

# 環境変数からDB設定を上書き
settings = get_settings()
url = settings.DATABASE_URL
# CREATE TYPE AS ENUM は拡張クエリプロトコル(Parse)で型を生成してしまうため、
# マイグレーション実行時は asyncpg の prepared statement を無効化する
# (PostgreSQL 既知の挙動: パース時に型が作られ Execute で "already exists" になる)
if "prepared_statement_cache_size" not in url:
    url += ("&" if "?" in url else "?") + "prepared_statement_cache_size=0"
config.set_main_option("sqlalchemy.url", url)


def include_name(name, type_, parent_names):
    """name が auth スキーマの場合のみ含める（オートジェネレート用）"""
    if type_ == "schema":
        return name in ("auth", None)
    return True


def run_migrations_offline() -> None:
    """オフラインマイグレーション（SQLスクリプト生成）"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
        version_table_schema="auth",
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        include_name=include_name,
        version_table_schema="auth",
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """非同期マイグレーション実行"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # 空の検証DBでも再実行可能にするため、
        # バージョンテーブル格納先スキーマ(auth)を事前作成する
        await connection.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        await connection.commit()
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """オンラインマイグレーション（DBに直接接続）"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
