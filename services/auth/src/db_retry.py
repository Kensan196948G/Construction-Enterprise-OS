"""DB 過渡エラー(接続断・タイムアウト等)の検出支援

R6対策: ログインが稀に INTERNAL_ERROR になる事象(1回目失敗→再試行で即成功)の
うち、プールされた失効コネクション由来のものは engine の pool_pre_ping で防ぎ、
それでも発生した接続過渡エラーはここで検出して、エンドポイント側で
新しいセッションによる再実行を行う。
"""

import logging

from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

#: 過渡的とみなす PostgreSQL SQLSTATE(接続系・系シャットダウン・リソース枯渇)
TRANSIENT_SQLSTATES = frozenset(
    {
        "08000",  # connection_exception
        "08001",  # sqlclient_unable_to_establish_sqlconnection
        "08003",  # connection_does_not_exist
        "08004",  # sqlserver_rejected_establishment_of_sqlconnection
        "08006",  # connection_failure
        "08007",  # transaction_resolution_unknown
        "53300",  # too_many_connections
        "57P01",  # admin_shutdown
        "57P02",  # crash_shutdown
        "57P03",  # cannot_connect_now
    }
)

#: ドライバ由来のエラーメッセージに含まれると過渡的と判定するキーワード
_CONNECTION_KEYWORDS = (
    "connection",
    "broken pipe",
    "gone away",
    "refused",
    "reset by peer",
    "ssl",
)


def is_transient_db_error(exc: BaseException) -> bool:
    """接続断・タイムアウト等、再試行で回復しうる DB エラーか判定する。

    ビジネス例外(HTTPException 等)や通常のクエリエラーは False を返す。
    """
    if not isinstance(exc, (OperationalError, InterfaceError)):
        return False
    orig = getattr(exc, "orig", None)
    sqlstate = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
    if sqlstate in TRANSIENT_SQLSTATES:
        return True
    message = str(orig or exc).lower()
    return any(k in message for k in _CONNECTION_KEYWORDS)


async def rollback_safely(db: AsyncSession) -> None:
    """セッションのロールバックを安全に実行する(失敗しても握りつぶす)。"""
    try:
        await db.rollback()
    except Exception:  # noqa: BLE001 - 既に異常系のためログのみ
        logger.warning("rollback failed during transient-error handling", exc_info=True)
