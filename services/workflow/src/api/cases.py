"""受付番号を共通キーにする仕様互換API。"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas import APIResponse, CaseAction, DuplicateJudgement, WorkflowInstanceCreate
from ..services.approval_service import approve_step
from ..services.document_adapter import store_workflow_documents, store_workflow_work_area
from ..services import workflow_service
from ..services.check_service import SubmissionValidationError
from ..services.notification_adapter import (
    resolve_notification_recipients,
    send_workflow_notification,
    send_workflow_notifications,
)
from .workflows import _instance_to_response, _organization_id

router = APIRouter()

MANAGEMENT_ROLES = {"admin", "management"}


def _require_management(current_user: TokenData) -> None:
    if not MANAGEMENT_ROLES.intersection(current_user.roles):
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "管理部権限が必要です。"},
        )


def _deadline_value(instance) -> str:
    due_date = getattr(instance, "due_date", None)
    return due_date.isoformat() if due_date is not None else ""


async def _get_case(
    db: AsyncSession, receipt_no: str, current_user: TokenData
):
    instance = await workflow_service.get_instance_by_receipt(
        db, receipt_no, _organization_id(current_user)
    )
    # 下書きは受付番号未発行のため、提出操作だけ内部IDでも受け付ける。
    if instance is None:
        try:
            instance = await workflow_service.get_instance_with_chain(
                db, UUID(receipt_no), _organization_id(current_user)
            )
        except ValueError:
            instance = None
    if instance is not None and not workflow_service.can_view_instance(
        instance, UUID(current_user.sub), current_user.roles
    ):
        instance = None
    if not instance:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "案件が見つかりません。"},
        )
    return instance


@router.post("/cases", status_code=status.HTTP_201_CREATED)
async def create_case(
    body: WorkflowInstanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    organization_id = _organization_id(current_user)
    if body.organization_id != organization_id:
        raise HTTPException(status_code=403, detail={"code": "ORG_FORBIDDEN"})
    try:
        created_instance = await workflow_service.start_workflow(
            db,
            definition_id=body.definition_id,
            submitted_by=UUID(current_user.sub),
            organization_id=organization_id,
            title=body.title,
            description=body.description,
            priority=body.priority,
            reference_type=body.reference_type,
            reference_id=body.reference_id,
            metadata=body.metadata,
        )
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.create",
            event_data={"receipt_no": created_instance.receipt_no},
        )
        await db.commit()
        instance = await workflow_service.get_instance_with_chain(
            db, created_instance.id, organization_id
        )
        if instance is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "NOT_FOUND", "message": "作成した案件が見つかりません。"},
            )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": str(exc)}) from exc


@router.get("/cases")
async def list_cases(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instances = await workflow_service.get_instances(
        db, organization_id=_organization_id(current_user)
    )
    instances = [
        instance
        for instance in instances
        if workflow_service.can_view_instance(
            instance, UUID(current_user.sub), current_user.roles
        )
    ]
    return APIResponse(data=[_instance_to_response(instance) for instance in instances])


@router.get("/cases/{receipt_no}")
async def get_case(
    receipt_no: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instance = await _get_case(db, receipt_no, current_user)
    return APIResponse(data=_instance_to_response(instance))


@router.post("/cases/{receipt_no}/submit")
async def submit_case(
    receipt_no: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instance = await _get_case(db, receipt_no, current_user)
    try:
        instance = await workflow_service.submit_workflow(
            db, instance.id, UUID(current_user.sub)
        )
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.submit",
            event_data={"receipt_no": instance.receipt_no},
        )
        await db.commit()
        document_ids = (
            instance.metadata_.get("attachment_document_ids", [])
            if isinstance(instance.metadata_, dict)
            else []
        )
        if isinstance(document_ids, list) and document_ids:
            background_tasks.add_task(
                store_workflow_work_area,
                document_ids=document_ids,
                organization_id=_organization_id(current_user),
                receipt_no=instance.receipt_no,
            )
        approval_roles = {
            approval.approver_role
            for approval in getattr(instance, "approvals", [])
            if getattr(approval, "status", "pending") == "pending"
        }
        recipients = await resolve_notification_recipients(
            organization_id=_organization_id(current_user), roles=approval_roles
        )
        background_tasks.add_task(
            send_workflow_notifications,
            recipient_ids=recipients,
            template_code="workflow.approval_requested",
            instance_id=instance.id,
            transition="submitted",
            actor_id=UUID(current_user.sub),
            template_vars={
                "document_name": instance.title,
                "requester_name": str(current_user.sub),
                "deadline": _deadline_value(instance),
                "comment": "",
            },
        )
        return APIResponse(data=_instance_to_response(instance))
    except SubmissionValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(exc),
                "errors": exc.errors,
                "warnings": exc.warnings,
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": str(exc)}) from exc


@router.post("/cases/{receipt_no}/confirm")
async def confirm_case(
    receipt_no: str,
    background_tasks: BackgroundTasks,
    body: CaseAction | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_management(current_user)
    instance = await _get_case(db, receipt_no, current_user)
    try:
        instance = await workflow_service.transition_case(
            db, instance.id, _organization_id(current_user), UUID(current_user.sub),
            "forwarded", {"in_progress"}, body.comment if body else None,
        )
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.confirm",
            event_data={"receipt_no": receipt_no},
        )
        await db.commit()
        approval_roles = {
            approval.approver_role
            for approval in getattr(instance, "approvals", [])
            if getattr(approval, "status", "pending") == "pending"
        }
        recipients = await resolve_notification_recipients(
            organization_id=_organization_id(current_user), roles=approval_roles
        )
        background_tasks.add_task(
            send_workflow_notifications,
            recipient_ids=recipients,
            template_code="workflow.approval_requested",
            instance_id=instance.id,
            transition="forwarded",
            actor_id=UUID(current_user.sub),
            template_vars={
                "document_name": instance.title,
                "requester_name": str(instance.submitted_by),
                "deadline": _deadline_value(instance),
                "comment": body.comment if body else "",
            },
        )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "INVALID_STATUS_TRANSITION", "message": str(exc)}) from exc


@router.post("/cases/{receipt_no}/forward")
async def forward_case(
    receipt_no: str,
    background_tasks: BackgroundTasks,
    body: CaseAction | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_management(current_user)
    instance = await _get_case(db, receipt_no, current_user)
    try:
        instance = await workflow_service.transition_case(
            db, instance.id, _organization_id(current_user), UUID(current_user.sub),
            "pending_approval", {"forwarded"}, body.comment if body else None,
        )
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.forward",
            event_data={"receipt_no": receipt_no},
        )
        await db.commit()
        approval_roles = {
            approval.approver_role
            for approval in getattr(instance, "approvals", [])
            if getattr(approval, "status", "pending") == "pending"
        }
        recipients = await resolve_notification_recipients(
            organization_id=_organization_id(current_user), roles=approval_roles
        )
        background_tasks.add_task(
            send_workflow_notifications,
            recipient_ids=recipients,
            template_code="workflow.approval_requested",
            instance_id=instance.id,
            transition="forwarded",
            actor_id=UUID(current_user.sub),
            template_vars={
                "document_name": instance.title,
                "requester_name": str(instance.submitted_by),
                "deadline": _deadline_value(instance),
                "comment": body.comment if body else "",
            },
        )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "INVALID_STATUS_TRANSITION", "message": str(exc)}) from exc


@router.post("/cases/{receipt_no}/return")
async def return_case(
    receipt_no: str,
    body: CaseAction,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_management(current_user)
    if not body.comment or not body.comment.strip():
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "差戻し理由は必須です。"})
    instance = await _get_case(db, receipt_no, current_user)
    try:
        instance = await workflow_service.transition_case(
            db, instance.id, _organization_id(current_user), UUID(current_user.sub),
            "rejected", {"in_progress", "forwarded", "pending_approval"}, body.comment,
        )
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.return",
            event_data={"receipt_no": receipt_no, "comment": body.comment},
        )
        await db.commit()
        background_tasks.add_task(
            send_workflow_notification,
            recipient_id=instance.submitted_by,
            template_code="workflow.rejected",
            instance_id=instance.id,
            transition="rejected",
            actor_id=UUID(current_user.sub),
            template_vars={
                "document_name": instance.title,
                "reviewer_name": str(current_user.sub),
                "reason": body.comment,
            },
        )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "INVALID_STATUS_TRANSITION", "message": str(exc)}) from exc


@router.post("/cases/{receipt_no}/resubmit")
async def resubmit_case(
    receipt_no: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instance = await _get_case(db, receipt_no, current_user)
    try:
        instance = await workflow_service.resubmit_workflow(
            db, instance.id, UUID(current_user.sub)
        )
        workflow_service.record_audit_log(
            db,
            user_id=UUID(current_user.sub),
            event_type="case.resubmit",
            event_data={"receipt_no": instance.receipt_no},
        )
        await db.commit()
        recipients = await resolve_notification_recipients(
            organization_id=_organization_id(current_user),
            roles={"management", "admin"},
        )
        background_tasks.add_task(
            send_workflow_notifications,
            recipient_ids=recipients,
            template_code="workflow.resubmitted",
            instance_id=instance.id,
            transition="resubmitted",
            actor_id=UUID(current_user.sub),
            template_vars={
                "document_name": instance.title,
                "requester_name": str(current_user.sub),
                "deadline": _deadline_value(instance),
                "comment": "",
            },
        )
        return APIResponse(data=_instance_to_response(instance))
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "INVALID_STATUS_TRANSITION", "message": str(exc)},
        ) from exc


@router.post("/cases/{receipt_no}/approve")
async def approve_case(
    receipt_no: str,
    step_order: int | None = Query(None, gt=0),
    body: CaseAction | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instance = await _get_case(db, receipt_no, current_user)
    try:
        if step_order is None:
            pending_steps = [
                approval.step_order
                for approval in instance.approvals
                if approval.status == "pending"
            ]
            if not pending_steps:
                raise ValueError("承認待ちのステップがありません。")
            step_order = min(pending_steps)
        result = await approve_step(
            db, instance.id, step_order, UUID(current_user.sub),
            body.comment if body else None, current_user.roles,
            _organization_id(current_user),
        )
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.approve",
            event_data={"receipt_no": receipt_no, "step_order": step_order},
        )
        await db.commit()
        return APIResponse(data=_instance_to_response(result))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "INVALID_STATUS_TRANSITION", "message": str(exc)}) from exc


@router.post("/cases/{receipt_no}/judge-duplicate")
async def judge_case_duplicate(
    receipt_no: str,
    body: DuplicateJudgement,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_management(current_user)
    instance = await _get_case(db, receipt_no, current_user)
    try:
        result = await workflow_service.judge_duplicate(
            db, instance.id, _organization_id(current_user), UUID(current_user.sub),
            body.decision, body.comment,
        )
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.judge_duplicate",
            event_data={"receipt_no": receipt_no, "decision": body.decision},
        )
        await db.commit()
        return APIResponse(data=_instance_to_response(result))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(exc)}) from exc


@router.post("/cases/{receipt_no}/store")
async def store_case(
    receipt_no: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    instance = await _get_case(db, receipt_no, current_user)
    metadata = instance.metadata_ if isinstance(instance.metadata_, dict) else {}
    document_ids = metadata.get("attachment_document_ids", [])
    if not isinstance(document_ids, list) or not document_ids:
        raise HTTPException(status_code=422, detail={"code": "FILE_UPLOAD_FAILED", "message": "正本保存対象の添付ファイルがありません。"})
    stored, failed = await store_workflow_documents(
        document_ids=document_ids, organization_id=_organization_id(current_user)
    )
    if failed:
        instance.canonical_error = f"{failed}件の正本保存に失敗しました。"
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.store",
            event_data={"receipt_no": receipt_no, "failed": failed}, success=False,
        )
        await db.commit()
        raise HTTPException(status_code=502, detail={"code": "FILE_UPLOAD_FAILED", "message": instance.canonical_error})
    try:
        result = await workflow_service.transition_case(
            db, instance.id, _organization_id(current_user), UUID(current_user.sub),
            "stored", {"approved", "completed"}, "正本保存完了",
        )
        workflow_service.record_audit_log(
            db, user_id=UUID(current_user.sub), event_type="case.store",
            event_data={"receipt_no": receipt_no, "stored": stored},
        )
        await db.commit()
        return APIResponse(data={**_instance_to_response(result), "stored_document_ids": stored})
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "INVALID_STATUS_TRANSITION", "message": str(exc)}) from exc
