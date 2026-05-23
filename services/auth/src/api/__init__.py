from fastapi import APIRouter

router = APIRouter()

# ルーター群は下位モジュールで定義
from . import auth, users, roles, permissions, clients, audit  # noqa: E402, F401
