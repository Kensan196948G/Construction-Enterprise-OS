"""db_retry モジュールのユニットテスト(R6対策)"""

from sqlalchemy.exc import InterfaceError, OperationalError


def _make_error(
    exc_cls: type,
    message: str,
    sqlstate: str | None = None,
    pgcode: str | None = None,
) -> Exception:
    """orig 付き SQLAlchemy エラーを構築する"""
    class _Orig:
        def __init__(self):
            self.sqlstate = sqlstate
            self.pgcode = pgcode

        def __str__(self):
            return message

    return exc_cls(message, None, _Orig())


def test_operational_error_with_transient_sqlstate_is_transient():
    from src.db_retry import is_transient_db_error

    exc = _make_error(OperationalError, "connection failed", sqlstate="08006")
    assert is_transient_db_error(exc)


def test_operational_error_with_shutdown_sqlstate_is_transient():
    from src.db_retry import is_transient_db_error

    exc = _make_error(OperationalError, "server shutting down", sqlstate="57P03")
    assert is_transient_db_error(exc)


def test_operational_error_with_connection_message_is_transient():
    from src.db_retry import is_transient_db_error

    # sqlstate なしでも接続系メッセージなら過渡的と判定する
    exc = _make_error(OperationalError, "connection refused: server is not running")
    assert is_transient_db_error(exc)


def test_interface_error_is_transient():
    from src.db_retry import is_transient_db_error

    exc = _make_error(InterfaceError, "connection is closed")
    assert is_transient_db_error(exc)


def test_non_connection_operational_error_is_not_transient():
    from src.db_retry import is_transient_db_error

    # 通常のクエリエラー(構文エラー等)はリトライ対象外
    exc = _make_error(OperationalError, "syntax error at or near SELECT", sqlstate="42601")
    assert not is_transient_db_error(exc)


def test_non_db_exception_is_not_transient():
    from src.db_retry import is_transient_db_error

    assert not is_transient_db_error(ValueError("boom"))
    assert not is_transient_db_error(RuntimeError("boom"))


def test_rollback_safely_ignores_rollback_failure():
    from src.db_retry import rollback_safely

    class BrokenSession:
        async def rollback(self):
            raise RuntimeError("rollback failed")

    # 例外を握りつぶして正常終了すること
    import asyncio

    asyncio.run(rollback_safely(BrokenSession()))  # type: ignore[arg-type]
