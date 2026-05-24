"""ワークフローAPI エンドポイント"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    ApprovalAction,
    WorkflowDefinitionCreate,
    WorkflowInstanceCreate,
)
from ..services import approval_service, workflow_service

router = APIRouter()


def _definition_to_response(d) -> dict:
    return {
        "id": str(d.id),
        "organization_id": str(d.organization_id),
        "name": d.name,
        "description": d.description,
        "category": d.category,
        "steps": d.steps if isinstance(d.steps, list) else [],
        "is_active": d.is_active,
        "created_by": str(d.created_by) if d.created_by else None,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    }


def _instance_to_response(instance) -> dict:
    result = {
        "id": str(instance.id),
        "definition_id": str(instance.definition_id) if instance.definition_id else None,
        "organization_id": str(instance.organization_id),
        "title": instance.title,
        "description": instance.description,
        "category": instance.category,
        "status": instance.status,
        "priority": instance.priority,
        "reference_type": instance.reference_type,
        "reference_id": str(instance.reference_id) if instance.reference_id else None,
        "metadata": instance.metadata_ if isinstance(instance.metadata_, dict) else {},
        "submitted_by": str(instance.submitted_by),
        "submitted_at": instance.submitted_at.isoformat() if instance.submitted_at else None,
        "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
        "created_at": instance.created_at.isoformat() if instance.created_at else None,
        "updated_at": instance.updated_at.isoformat() if instance.updated_at else None,
    }
    return result


def _approval_to_response(a) -> dict:
    return {
        "id": str(a.id),
        "instance_id": str(a.instance_id),
        "step_order": a.step_order,
        "approver_id": str(a.approver_id) if a.approver_id else None,
        "approver_role": a.approver_role,
        "status": a.status,
        "comment": a.comment,
        "approved_at": a.approved_at.isoformat() if a.approved_at else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


# ——— Workflow Definitions ———


@router.post("/definitions", status_code=status.HTTP_201_CREATED)
async def create_definition(
    body: WorkflowDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    steps = [s.model_dump() for s in body.steps]
    definition = await workflow_service.create_definition(
        db,
        organization_id=body.organization_id,
        name=body.name,
        description=body.description,
        category=body.category,
        steps=steps,
        created_by=UUID(current_user.sub),
    )
    return APIResponse(data=_definition_to_response(definition))


@router.get("/definitions")
async def list_definitions(
    organization_id: UUID | None = Query(None),
    category: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    definitions = await workflow_service.get_definitions(
        db,
        organization_id=organization_id,
        category=category,
        is_active=is_active,
    )
    return APIResponse(data=[_definition_to_response(d) for d in definitions])


# ——— Workflow Instances ———


@router.post("/instances", status_code=status.HTTP_201_CREATED)
async def create_instance(
    body: WorkflowInstanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    try:
        instance = await workflow_service.start_workflow(
            db,
            definition_id=body.definition_id,
            submitted_by=UUID(current_user.sub),
            organization_id=body.organization_id,
            title=body.title,
            description=body.description,
            priority=body.priority,
            reference_type=body.reference_type,
            reference_id=body.reference_id,
            metadata=body.metadata,
        )
        instance_full = await workflow_service.get_instance_with_chain(db, instance.id)
        data = _instance_to_response(instance_full)
        data["approvals"] = [
            _approval_to_response(a) for a in instance_full.approvals
        ]
        return APIResponse(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": str(e)})


@router.get("/instances")
async def list_instances(
    organization_id: UUID | None = Query(None),
    status: str | None = Query(None),
    category: str | None = Query(None),
    submitted_by: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instances = await workflow_service.get_instances(
        db,
        organization_id=organization_id,
        status=status,
        category=category,
        submitted_by=submitted_by,
    )
    return APIResponse(data=[_instance_to_response(i) for i in instances])


@router.get("/instances/pending")
async def get_pending_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instances = await workflow_service.get_pending_approvals(
        db, user_roles=current_user.roles
    )
    return APIResponse(data=[_instance_to_response(i) for i in instances])


@router.get("/instances/{instance_id}")
async def get_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instance = await workflow_service.get_instance_with_chain(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ワークフローが見つかりません。"},
        )
    data = _instance_to_response(instance)
    data["approvals"] = [
        _approval_to_response(a) for a in instance.approvals
    ]
    return APIResponse(data=data)


@router.get("/instances/{instance_id}/history")
async def get_history(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instance = await workflow_service.get_instance_with_chain(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ワークフローが見つかりません。"},
        )
    return APIResponse(data=[_approval_to_response(a) for a in instance.approvals])


# ——— Workflow Actions ———


@router.post("/instances/{instance_id}/submit")
async def submit_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    try:
        instance = await workflow_service.submit_workflow(
            db, instance_id, UUID(current_user.sub)
        )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": str(e)})


@router.post("/instances/{instance_id}/approve")
async def approve_step(
    instance_id: UUID,
    step_order: int = Query(..., description="Approval step order to approve"),
    body: ApprovalAction | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    try:
        comment = body.comment if body else None
        instance = await approval_service.approve_step(
            db,
            instance_id=instance_id,
            step_order=step_order,
            user_id=UUID(current_user.sub),
            comment=comment,
            user_roles=current_user.roles,
        )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": str(e)})


@router.post("/instances/{instance_id}/reject")
async def reject_step(
    instance_id: UUID,
    step_order: int = Query(..., description="Approval step order to reject"),
    body: ApprovalAction | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    try:
        comment = body.comment if body else None
        instance = await approval_service.reject_step(
            db,
            instance_id=instance_id,
            step_order=step_order,
            user_id=UUID(current_user.sub),
            comment=comment,
            user_roles=current_user.roles,
        )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": str(e)})


@router.post("/instances/{instance_id}/cancel")
async def cancel_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    try:
        instance = await workflow_service.cancel_workflow(
            db, instance_id, UUID(current_user.sub)
        )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": str(e)})
