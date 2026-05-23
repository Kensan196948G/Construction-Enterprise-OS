"""APIクライアント管理ビジネスロジック"""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ApiClient


def _generate_client_id() -> str:
    return f"ceo_{secrets.token_urlsafe(16)}"


def _generate_client_secret() -> str:
    return secrets.token_urlsafe(48)


def _hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


async def create_api_client(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    name: str,
    scopes: list[str],
) -> tuple[ApiClient, str]:
    client_id = _generate_client_id()
    plain_secret = _generate_client_secret()
    secret_hash = _hash_secret(plain_secret)

    client = ApiClient(
        id=uuid.uuid4(),
        organization_id=organization_id,
        name=name,
        client_id=client_id,
        client_secret_hash=secret_hash,
        scopes=scopes,
        status="active",
        created_at=datetime.now(timezone.utc),
    )
    db.add(client)
    return client, plain_secret


async def get_api_clients(
    db: AsyncSession, organization_id: uuid.UUID
) -> list[ApiClient]:
    result = await db.execute(
        select(ApiClient)
        .where(ApiClient.organization_id == organization_id)
        .order_by(ApiClient.created_at.desc())
    )
    return list(result.scalars().all())


async def get_api_client_by_id(
    db: AsyncSession, client_id: uuid.UUID
) -> ApiClient | None:
    result = await db.execute(
        select(ApiClient).where(ApiClient.id == client_id)
    )
    return result.scalar_one_or_none()


async def revoke_api_client(
    db: AsyncSession, client_id: uuid.UUID
) -> ApiClient | None:
    client = await get_api_client_by_id(db, client_id)
    if not client:
        return None
    client.status = "revoked"
    client.updated_at = datetime.now(timezone.utc)
    return client
