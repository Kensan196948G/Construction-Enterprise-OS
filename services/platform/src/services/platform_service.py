"""Platformサービス ユーティリティ"""


def validate_widget_type(widget_type: str) -> bool:
    """Validate that a dashboard widget type is supported."""
    return widget_type in {"gauge", "chart", "map", "table", "value", "status"}


def normalize_interval_seconds(seconds: int) -> int:
    """Clamp refresh interval to valid range."""
    return max(1, min(seconds, 3600))
