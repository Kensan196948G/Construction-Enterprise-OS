"""通知テンプレート管理サービス"""

import math
from typing import Any
from uuid import UUID

from jinja2 import BaseLoader, Environment
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import NotificationTemplate
from ..schemas import NotificationTemplateCreate, PaginationMeta

env = Environment(loader=BaseLoader())


def render_template(template_str: str, variables: dict) -> str:
    template = env.from_string(template_str)
    return template.render(**variables)


async def get_templates(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    category: str | None = None,
) -> tuple[list[NotificationTemplate], PaginationMeta]:
    stmt = select(NotificationTemplate)
    count_stmt = select(func.count(NotificationTemplate.id))

    if category:
        stmt = stmt.where(NotificationTemplate.category == category)
        count_stmt = count_stmt.where(NotificationTemplate.category == category)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    offset = (page - 1) * per_page
    stmt = stmt.order_by(NotificationTemplate.category, NotificationTemplate.code)
    stmt = stmt.offset(offset).limit(per_page)

    result = await db.execute(stmt)
    templates = result.scalars().all()

    total_pages = math.ceil(total / per_page) if per_page > 0 else 0
    meta = PaginationMeta(
        page=page, per_page=per_page, total=total, total_pages=total_pages
    )

    return list(templates), meta


async def get_template_by_code(
    db: AsyncSession, code: str
) -> NotificationTemplate | None:
    stmt = select(NotificationTemplate).where(NotificationTemplate.code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_template_by_id(
    db: AsyncSession, template_id: UUID
) -> NotificationTemplate | None:
    stmt = select(NotificationTemplate).where(NotificationTemplate.id == template_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_template(
    db: AsyncSession, data: NotificationTemplateCreate
) -> NotificationTemplate:
    template = NotificationTemplate(
        code=data.code,
        name=data.name,
        channels=data.channels,
        title_template=data.title_template,
        body_template=data.body_template,
        priority=data.priority,
        category=data.category,
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)
    return template


async def update_template(
    db: AsyncSession, template: NotificationTemplate, data: dict
) -> NotificationTemplate:
    for field, value in data.items():
        if value is not None:
            setattr(template, field, value)
    await db.flush()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, template: NotificationTemplate) -> None:
    await db.delete(template)
    await db.flush()


async def ensure_default_templates(db: AsyncSession) -> None:
    defaults: list[dict[str, Any]] = [
        {
            "code": "workflow.approval_requested",
            "name": "承認依頼通知",
            "channels": ["in_app", "email"],
            "title_template": "【要承認】{{ document_name }}の承認依頼",
            "body_template": "{{ document_name }}の承認依頼が{{ requester_name }}さんから届いています。\n期日: {{ deadline }}\nコメント: {{ comment }}",
            "priority": "high",
            "category": "workflow",
        },
        {
            "code": "workflow.approved",
            "name": "承認完了通知",
            "channels": ["in_app", "email"],
            "title_template": "【承認完了】{{ document_name }}が承認されました",
            "body_template": "{{ document_name }}が{{ approver_name }}さんにより承認されました。",
            "priority": "normal",
            "category": "workflow",
        },
        {
            "code": "workflow.rejected",
            "name": "差戻通知",
            "channels": ["in_app", "email"],
            "title_template": "【差戻】{{ document_name }}が差し戻されました",
            "body_template": "{{ document_name }}が{{ reviewer_name }}さんにより差し戻されました。\n理由: {{ reason }}",
            "priority": "high",
            "category": "workflow",
        },
        {
            "code": "safety.alert",
            "name": "安全警告",
            "channels": ["in_app", "email"],
            "title_template": "【安全警告】{{ message }}",
            "body_template": "安全警告が発生しました。\n現場: {{ site_name }}\n種別: {{ alert_type }}\n内容: {{ message }}\n発生日時: {{ occurred_at }}",
            "priority": "urgent",
            "category": "safety",
        },
        {
            "code": "iot.alert",
            "name": "IoT 警告",
            "channels": ["in_app", "email"],
            "title_template": "【IoT警告】{{ device_name }}で{{ metric }}が閾値を超過",
            "body_template": "{{ device_name }}の{{ metric }}が閾値を超過しました。\n現在値: {{ value }}\n閾値: {{ threshold }}\n現場: {{ site_name }}",
            "priority": "high",
            "category": "iot",
        },
        {
            "code": "system.maintenance",
            "name": "システムメンテナンス通知",
            "channels": ["in_app", "email"],
            "title_template": "【システム】{{ message }}",
            "body_template": "{{ message }}\n\n予定日時: {{ scheduled_at }}\n影響範囲: {{ affected_services }}",
            "priority": "normal",
            "category": "system",
        },
    ]

    for tpl_data in defaults:
        existing = await get_template_by_code(db, tpl_data["code"])
        if not existing:
            template = NotificationTemplate(**tpl_data)
            db.add(template)

    await db.flush()
