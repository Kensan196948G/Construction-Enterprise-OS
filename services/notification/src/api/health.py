"""ヘルスチェック エンドポイント"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.base import get_db

router = APIRouter()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc

    settings = get_settings()
    neo_configured = bool(
        not settings.NEO_ENABLED
        or (settings.NEO_API_URL and settings.NEO_API_KEY)
    )
    return {
        "status": "healthy" if neo_configured else "degraded",
        "service": "notification-service",
        "integrations": {
            "neo": "disabled" if not settings.NEO_ENABLED else (
                "configured" if neo_configured else "misconfigured"
            )
        },
    }
