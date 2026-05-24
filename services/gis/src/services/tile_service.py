"""マップタイル生成サービス（プレースホルダー）"""

from fastapi import HTTPException, status


async def generate_tile(
    z: int,
    x: int,
    y: int,
    layers: list[str] | None = None,
) -> bytes:
    """
    マップタイル生成（将来実装）
    現在はプレースホルダーとして未実装を通知
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "code": "NOT_IMPLEMENTED",
            "message": "タイル生成機能は未実装です。",
        },
    )


async def tilejson_metadata() -> dict:
    """TileJSONメタデータ（プレースホルダー）"""
    return {
        "tilejson": "3.0.0",
        "name": "CEO-OS GIS Tiles",
        "description": "建設業統合OS マップタイルサービス",
        "scheme": "xyz",
        "tiles": [],
        "minzoom": 0,
        "maxzoom": 22,
        "status": "not_implemented",
    }
