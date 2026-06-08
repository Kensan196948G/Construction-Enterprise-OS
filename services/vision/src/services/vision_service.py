"""Backward-compatible re-export shim.

API modules import `vision_service.*` — this module delegates to the
domain-specific service files so existing call sites need no changes.
"""

from .ocr_service import (
    create_ocr_result,
    get_ocr_result_by_id,
    get_ocr_results,
)
from .image_analysis_service import (
    create_image_analysis,
    get_image_analyses,
    get_image_analysis_by_id,
)
from .vector_service import (
    build_search_results,
    create_vector_index,
    delete_vector_index,
    get_vector_index_by_id,
    get_vector_indices,
    increment_vector_counts,
    update_vector_index,
)

__all__ = [
    # OCR
    "create_ocr_result",
    "get_ocr_results",
    "get_ocr_result_by_id",
    # Image analysis
    "create_image_analysis",
    "get_image_analyses",
    "get_image_analysis_by_id",
    # Vector
    "create_vector_index",
    "get_vector_indices",
    "get_vector_index_by_id",
    "update_vector_index",
    "delete_vector_index",
    "increment_vector_counts",
    "build_search_results",
]
