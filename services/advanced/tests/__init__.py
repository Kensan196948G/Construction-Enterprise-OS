from unittest.mock import AsyncMock, MagicMock


class MockScalarResult:
    def __init__(self, return_value=None, return_values=None):
        self._return_value = return_value
        self._return_values = return_values or []

    def scalar_one_or_none(self):
        return self._return_value

    def scalars(self):
        return self

    def all(self):
        if isinstance(self._return_value, list):
            return self._return_value
        return [self._return_value] if self._return_value else []

    def first(self):
        return self._return_value

    def scalar(self):
        return self._return_value


def make_mock_user(sub="00000000-0000-0000-0000-000000000001"):
    user = MagicMock()
    user.sub = sub
    user.type = "user"
    user.org = "00000000-0000-0000-0000-000000000001"
    user.roles = ["admin"]
    user.scopes = []
    return user


def make_mock_db_execute(return_value=None, return_values=None):
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=MockScalarResult(return_value, return_values))
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.delete = MagicMock()
    return mock_db
