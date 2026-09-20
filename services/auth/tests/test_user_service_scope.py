"""組織ツリースコープのテスト"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.user_service import get_organization_scope

A, B, C, D, E = (uuid.uuid4() for _ in range(5))


def _db(rows):
    db = AsyncMock()
    result = MagicMock()
    result.all.return_value = rows
    db.execute = AsyncMock(return_value=result)
    return db


@pytest.mark.asyncio
async def test_scope_includes_self_and_descendants():
    rows = [(A, None), (B, A), (C, A), (D, B), (E, uuid.uuid4())]

    scope = await get_organization_scope(_db(rows), A)

    assert set(scope) == {A, B, C, D}


@pytest.mark.asyncio
async def test_scope_excludes_other_branches():
    rows = [(A, None), (B, A), (D, B), (E, uuid.uuid4())]

    scope = await get_organization_scope(_db(rows), B)

    assert set(scope) == {B, D}


@pytest.mark.asyncio
async def test_scope_of_leaf_is_itself():
    rows = [(A, None), (B, A)]

    scope = await get_organization_scope(_db(rows), B)

    assert scope == [B]
