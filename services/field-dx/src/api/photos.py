"""現場写真 API — stub"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class SitePhoto(BaseModel):
    id: str
    filename: str
    taken_at: str
    zone: str
    tags: list[str]
    uploader: str
    needs_review: bool
    description: str | None = None


_MOCK_PHOTOS = [
    SitePhoto(
        id="ph1",
        filename="IMG_20240520_083045.jpg",
        taken_at="2024-05-20T08:30:45",
        zone="第1工区",
        tags=["コンクリート", "打設前"],
        uploader="山田 太郎",
        needs_review=False,
        description="コンクリート打設前の型枠状況",
    ),
    SitePhoto(
        id="ph2",
        filename="IMG_20240521_101500.jpg",
        taken_at="2024-05-21T10:15:00",
        zone="第2工区",
        tags=["鉄筋", "検査"],
        uploader="鈴木 次郎",
        needs_review=True,
        description="鉄筋かぶり厚確認",
    ),
    SitePhoto(
        id="ph3",
        filename="IMG_20240522_140000.jpg",
        taken_at="2024-05-22T14:00:00",
        zone="第3工区",
        tags=["型枠", "完了"],
        uploader="佐藤 三郎",
        needs_review=False,
        description="型枠設置完了状況",
    ),
    SitePhoto(
        id="ph4",
        filename="IMG_20240523_090000.jpg",
        taken_at="2024-05-23T09:00:00",
        zone="第1工区",
        tags=["品質検査", "強度試験"],
        uploader="高橋 五郎",
        needs_review=True,
        description="コンクリート強度試験サンプル",
    ),
]


@router.get("/photos")
async def list_photos(
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    start = (page - 1) * per_page
    items = _MOCK_PHOTOS[start : start + per_page]
    return {"items": [p.model_dump() for p in items], "total": len(_MOCK_PHOTOS)}
