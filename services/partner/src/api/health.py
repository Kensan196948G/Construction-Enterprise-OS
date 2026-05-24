"""ヘルスチェックエンドポイント"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health():
    return {"status": "healthy", "service": "partner-service"}
