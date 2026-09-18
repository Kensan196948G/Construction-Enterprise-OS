"""ヘルスチェック

DB へ到達できない場合は 503 を返す。到達性を確認せずに常に 200 を返すと、
コンテナの healthcheck が DB 断を検知できず、監視が機能しない。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import get_db

router = APIRouter()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "healthy", "service": "document-service"}
