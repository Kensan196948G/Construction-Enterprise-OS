"""自律実行タスク管理エンドポイント"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import get_current_user
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
)
from ..services.autonomous_service import (
    create_task,
    get_task_by_id,
    get_tasks_paginated,
)

router = APIRouter()


def _task_to_response(task) -> TaskResponse:
    return TaskResponse.model_validate(task)


@router.post("", response_model=APIResponse[TaskResponse], status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    request: Request,
    body: TaskCreateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    task = await create_task(db, body.model_dump())
    return APIResponse(data=_task_to_response(task))


@router.get("", response_model=APIResponse[TaskListResponse])
async def list_tasks(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    task_type: str | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    agent_id: UUID | None = Query(None),
    organization_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    tasks, total = await get_tasks_paginated(
        db,
        page=page,
        per_page=per_page,
        task_type=task_type,
        status=status,
        priority=priority,
        agent_id=agent_id,
        organization_id=organization_id,
    )
    total_pages = max((total + per_page - 1) // per_page, 1) if total > 0 else 0

    return APIResponse(
        data=TaskListResponse(
            tasks=[_task_to_response(t) for t in tasks],
            total=total,
        ),
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )


@router.get("/{task_id}", response_model=APIResponse[TaskResponse])
async def get_task(
    request: Request,
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TASK_NOT_FOUND", "message": "タスクが見つかりません。"},
        )
    return APIResponse(data=_task_to_response(task))
