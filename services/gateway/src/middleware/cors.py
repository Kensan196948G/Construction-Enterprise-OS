"""CORSミドルウェア設定"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import get_settings

settings = get_settings()


def setup_cors(app: FastAPI) -> None:
    """CORSミドルウェアをアプリケーションに追加"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
