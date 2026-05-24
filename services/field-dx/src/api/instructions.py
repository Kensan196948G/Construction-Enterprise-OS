"""作業指示 API — stub"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class WorkInstruction(BaseModel):
    id: str
    number: str
    title: str
    zone: str
    priority: str
    deadline: str
    status: str
    assignee: str


_MOCK_INSTRUCTIONS = [
    WorkInstruction(
        id="wi1",
        number="WI-2024-001",
        title="第1工区 コンクリート打設作業指示",
        zone="第1工区",
        priority="critical",
        deadline="2024-05-24",
        status="in_progress",
        assignee="山田 太郎",
    ),
    WorkInstruction(
        id="wi2",
        number="WI-2024-002",
        title="第2工区 鉄筋是正作業",
        zone="第2工区",
        priority="high",
        deadline="2024-05-25",
        status="pending",
        assignee="鈴木 次郎",
    ),
    WorkInstruction(
        id="wi3",
        number="WI-2024-003",
        title="第3工区 型枠設置",
        zone="第3工区",
        priority="normal",
        deadline="2024-05-26",
        status="pending",
        assignee="佐藤 三郎",
    ),
    WorkInstruction(
        id="wi4",
        number="WI-2024-004",
        title="仮設工区 撤去作業",
        zone="仮設工区",
        priority="low",
        deadline="2024-05-30",
        status="completed",
        assignee="田中 花子",
    ),
]


@router.get("/instructions")
async def list_instructions(
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    start = (page - 1) * per_page
    items = _MOCK_INSTRUCTIONS[start : start + per_page]
    return {"items": [i.model_dump() for i in items], "total": len(_MOCK_INSTRUCTIONS)}
