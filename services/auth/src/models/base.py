from collections.abc import AsyncGenerator

from sqlalchemy import MetaData, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)


@event.listens_for(engine.sync_engine, "connect")
def _set_search_path(dbapi_connection, _connection_record) -> None:
    """auth スキーマの ENUM 型を非修飾キャスト($1::org_type)で解決できるよう
    接続ごとに search_path へ auth を含める(空DBからの再実行でも一貫動作)。
    asyncpg の server_settings は環境(Neon 等)によって無視されるため、
    接続イベントで明示的に SET する。"""
    cursor = dbapi_connection.cursor()
    cursor.execute("SET search_path TO auth, public")
    cursor.close()

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    metadata = MetaData(schema="auth")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI依存性注入用"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
