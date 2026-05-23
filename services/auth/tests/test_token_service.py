"""トークンサービス ユニットテスト（JWT作成・検証）"""

import pytest

from src.services.token_service import (
    create_access_token,
    create_m2m_token,
    decode_token,
)
from src.schemas import TokenData


def test_create_access_token():
    token = create_access_token(
        subject="user-123",
        org="org-456",
        roles=["admin", "editor"],
        device_id="device-001",
    )
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    token = create_access_token(
        subject="user-123",
        org="org-456",
        roles=["admin"],
        device_id="device-001",
    )
    token_data = decode_token(token)
    assert token_data is not None
    assert token_data.sub == "user-123"
    assert token_data.org == "org-456"
    assert "admin" in token_data.roles
    assert token_data.type == "user"


def test_create_m2m_token():
    token = create_m2m_token(
        client_id="client-abc",
        org="org-456",
        scopes=["read:users", "write:users"],
    )
    assert isinstance(token, str)


def test_decode_m2m_token():
    token = create_m2m_token(
        client_id="client-abc",
        org="org-456",
        scopes=["read:users"],
    )
    token_data = decode_token(token)
    assert token_data is not None
    assert token_data.sub == "client-abc"
    assert token_data.type == "client"
    assert "read:users" in token_data.scopes


def test_decode_invalid_token():
    token_data = decode_token("invalid-token-string")
    assert token_data is None


def test_token_type_user():
    token = create_access_token(
        subject="user-123",
        roles=["viewer"],
    )
    token_data = decode_token(token)
    assert token_data is not None
    assert token_data.type == "user"


def test_token_type_client():
    token = create_m2m_token(
        client_id="client-xyz",
        org="org-1",
        scopes=["read"],
    )
    token_data = decode_token(token)
    assert token_data is not None
    assert token_data.type == "client"


def test_token_roles_default_empty():
    token = create_access_token(subject="user-no-roles")
    token_data = decode_token(token)
    assert token_data is not None
    assert token_data.roles == []
