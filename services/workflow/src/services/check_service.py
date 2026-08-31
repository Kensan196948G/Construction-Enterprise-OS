"""提出時に実行するマスタ駆動チェック。"""

from typing import Any


class SubmissionValidationError(ValueError):
    """提出を妨げるチェックエラー。警告は提出を妨げない。"""

    def __init__(self, errors: list[dict[str, str]], warnings: list[dict[str, str]]):
        self.errors = errors
        self.warnings = warnings
        super().__init__("提出時チェックに失敗しました。")


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _metadata_value(metadata: dict[str, Any], field: str) -> Any:
    value: Any = metadata
    for part in field.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def validate_submission(
    metadata: dict[str, Any] | None, check_rules: dict[str, Any] | None
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """定義のルールに従い、提出を止めるエラーと通知用警告を返す。"""
    metadata = metadata or {}
    rules = check_rules or {}
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    required_fields = rules.get("required_fields", [])
    if isinstance(required_fields, list):
        for field in required_fields:
            if not isinstance(field, str) or not field:
                continue
            if _is_blank(_metadata_value(metadata, field)):
                errors.append({"field": field, "message": f"{field}は必須です"})

    required_attachments = rules.get("required_attachments", [])
    attachments = metadata.get("attachments", [])
    if not isinstance(attachments, list):
        attachments = []
    attachment_names = {
        item.get("name")
        for item in attachments
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    attachment_names.update(item for item in attachments if isinstance(item, str))
    if isinstance(required_attachments, list):
        for attachment in required_attachments:
            if isinstance(attachment, str) and attachment not in attachment_names:
                errors.append(
                    {
                        "field": "attachments",
                        "message": f"必要資料「{attachment}」が不足しています",
                    }
                )

    construction_code = _metadata_value(metadata, "construction_code")
    construction_master = rules.get("construction_master", {})
    master = (
        construction_master.get(construction_code)
        if isinstance(construction_master, dict)
        else None
    )
    if construction_code and isinstance(master, dict):
        for field in ("construction_name", "branch_code", "site_code", "manager_id"):
            submitted = _metadata_value(metadata, field)
            expected = master.get(field)
            if expected is not None and submitted != expected:
                warnings.append(
                    {
                        "field": field,
                        "message": "工事コードと工事マスタの情報が一致していません",
                    }
                )

    return errors, warnings
