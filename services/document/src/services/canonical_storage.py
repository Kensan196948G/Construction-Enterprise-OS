"""正本・作業領域への実体ファイル転送。

Workflow サービスは案件の提出時に「作業領域保存」、承認後の正本保存時に
「正本保存」を Document Service の内部APIへ要求する。本モジュールはその要求を
受けて、MinIO 上の実体ファイルを実際の保存先へ転送する。

保存先は次の2方式。設定が無い場合は **fail-closed**（保存したことにしない）。

* ``ONEDRIVE_ENABLED=true`` かつ4項目が揃っている場合は OneDrive
  （Microsoft Graph）へアップロードする。
* それ以外で ``CANONICAL_STORAGE_ROOT`` が設定されている場合は
  ローカルファイルシステム（docker volume）へ原子的に書き込む。
* どちらも設定されていない場合は ``StorageTransferError``
  （``STORAGE_NOT_CONFIGURED``）を送出する。従来のように時刻だけを記録して
  成功を返すことはしない。
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import re
import tempfile
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from uuid import UUID

import httpx

from ..config import get_settings
from ..models import Document
from . import storage_service

logger = logging.getLogger(__name__)

# 1ファイルあたりの読み書きチャンク（メモリ枯渇を避けるため逐次転送する）
_CHUNK_SIZE = 1024 * 1024

# ファイル名1コンポーネントの最大バイト数（多くのファイルシステムの上限255byte）
_MAX_COMPONENT_BYTES = 200

# Microsoft Graph の simple upload 上限（250MB）。超える場合は upload session が必要。
_GRAPH_SIMPLE_UPLOAD_LIMIT_BYTES = 250 * 1024 * 1024

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
_UNDESIRABLE_CHARS = re.compile(r'[<>:"|?*\\/]')
# 区切り文字を除去した後も ".." が部分文字列として残らないようにする
# (下流のツールが独自に区切り解釈する場合の多層防御)
_DOT_RUNS = re.compile(r"\.{2,}")

BACKEND_FILESYSTEM = "filesystem"
BACKEND_ONEDRIVE = "onedrive"


class StorageTransferError(Exception):
    """実体ファイル転送の失敗。HTTPステータスへ写像して呼び出し元へ返す。"""

    def __init__(self, code: str, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

    def as_detail(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class StorageResult:
    """転送結果。DBへ記録するための情報のみを持つ。"""

    backend: str
    relative_path: str
    size_bytes: int


def sanitize_path_component(value: object, *, fallback: str) -> str:
    """パス1コンポーネントを安全化する（パストラバーサル防止）。

    区切り文字・制御文字・Windows/OneDrive で禁止される文字を除去し、
    ``.`` / ``..`` だけになる場合は ``fallback`` に置換する。
    戻り値は必ず区切り文字を含まない単一コンポーネントになる。
    """
    if value is None:
        return fallback
    candidate = unicodedata.normalize("NFC", str(value))
    candidate = _UNDESIRABLE_CHARS.sub("_", candidate)
    candidate = _CONTROL_CHARS.sub("", candidate)
    candidate = _DOT_RUNS.sub("_", candidate)
    candidate = candidate.strip().strip(".")
    candidate = candidate.strip()
    if not candidate or candidate in {".", ".."}:
        return fallback
    return _truncate_component(candidate)


def _truncate_component(name: str) -> str:
    """拡張子を保ったままバイト長で切り詰める。"""
    encoded = name.encode("utf-8")
    if len(encoded) <= _MAX_COMPONENT_BYTES:
        return name

    stem, dot, extension = name.rpartition(".")
    extension_bytes = len(extension.encode("utf-8")) + 1 if dot else 0
    if extension_bytes >= _MAX_COMPONENT_BYTES // 2:
        stem, dot, extension, extension_bytes = name, "", "", 0

    budget = _MAX_COMPONENT_BYTES - extension_bytes
    truncated = stem.encode("utf-8")[:budget].decode("utf-8", errors="ignore")
    truncated = truncated or "file"
    return f"{truncated}.{extension}" if dot else truncated


def canonical_relative_path(document: Document) -> str:
    """正本の保存先相対パス。ドキュメントIDと版で一意になる。"""
    organization_id = _safe_uuid(document.organization_id)
    document_id = _safe_uuid(document.id)
    file_name = sanitize_path_component(document.file_name, fallback="document.bin")
    version = document.current_version or 1
    return f"canonical/{organization_id}/{document_id}/v{version}/{file_name}"


def work_area_relative_path(document: Document, receipt_no: str) -> str:
    """受付番号単位の作業領域の保存先相対パス。"""
    organization_id = _safe_uuid(document.organization_id)
    document_id = _safe_uuid(document.id)
    safe_receipt = sanitize_path_component(receipt_no, fallback="no-receipt")
    file_name = sanitize_path_component(document.file_name, fallback="document.bin")
    return f"work-areas/{safe_receipt}/{organization_id}/{document_id}/{file_name}"


def _safe_uuid(value: object) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError):
        return "unknown-organization"


def _resolve_backend() -> str:
    settings = get_settings()

    if settings.ONEDRIVE_ENABLED:
        missing = [
            name
            for name, value in (
                ("ONEDRIVE_TENANT_ID", settings.ONEDRIVE_TENANT_ID),
                ("ONEDRIVE_CLIENT_ID", settings.ONEDRIVE_CLIENT_ID),
                ("ONEDRIVE_CLIENT_SECRET", settings.ONEDRIVE_CLIENT_SECRET),
                ("ONEDRIVE_DRIVE_ID", settings.ONEDRIVE_DRIVE_ID),
            )
            if not value
        ]
        if missing:
            raise StorageTransferError(
                "STORAGE_NOT_CONFIGURED",
                "OneDrive連携が有効ですが設定が不足しています: " + ", ".join(missing),
                status_code=503,
            )
        return BACKEND_ONEDRIVE

    if settings.CANONICAL_STORAGE_ROOT:
        return BACKEND_FILESYSTEM

    raise StorageTransferError(
        "STORAGE_NOT_CONFIGURED",
        "正本の保存先が設定されていません（CANONICAL_STORAGE_ROOT または ONEDRIVE_ENABLED）。",
        status_code=503,
    )


def _iter_source_chunks(document: Document) -> Iterator[bytes]:
    """MinIO 上の実体を逐次読み出す。存在しなければ 502 相当のエラー。"""
    if not document.storage_key:
        raise StorageTransferError(
            "SOURCE_FILE_NOT_FOUND", "対象文書のストレージキーが未設定です。"
        )

    try:
        stream = storage_service.get_file_stream(document.storage_key)
    except Exception as exc:
        logger.exception("Object storage unavailable: %s", document.storage_key)
        raise StorageTransferError(
            "SOURCE_STORAGE_UNAVAILABLE",
            "オブジェクトストレージに接続できませんでした。",
            status_code=503,
        ) from exc

    if stream is None:
        raise StorageTransferError(
            "SOURCE_FILE_NOT_FOUND", "ストレージに実体ファイルが見つかりません。"
        )

    try:
        while True:
            chunk = stream.read(_CHUNK_SIZE)
            if not chunk:
                break
            yield chunk
    except Exception as exc:
        logger.exception("Failed while reading object: %s", document.storage_key)
        raise StorageTransferError(
            "SOURCE_STORAGE_UNAVAILABLE",
            "オブジェクトストレージからの読み出しに失敗しました。",
            status_code=503,
        ) from exc
    finally:
        closer = getattr(stream, "close", None)
        if callable(closer):
            with contextlib.suppress(Exception):
                closer()


def _storage_root() -> Path:
    settings = get_settings()
    if not settings.CANONICAL_STORAGE_ROOT:
        raise StorageTransferError(
            "STORAGE_NOT_CONFIGURED",
            "正本の保存先（CANONICAL_STORAGE_ROOT）が設定されていません。",
            status_code=503,
        )
    return Path(settings.CANONICAL_STORAGE_ROOT).expanduser().resolve()


def _contained_target(root: Path, relative_path: str) -> Path:
    """root 配下に収まることを検証した絶対パスを返す。"""
    target = (root / relative_path).resolve()
    if target != root and root not in target.parents:
        raise StorageTransferError(
            "INVALID_STORAGE_PATH", "保存先パスが保存ルートの外を指しています。"
        )
    return target


def _limited_chunks(
    document: Document, max_bytes: int, code: str, message: str
) -> Iterator[bytes]:
    """転送量の上限を超えたら中断する。保存領域の枯渇を防ぐ。"""
    total = 0
    for chunk in _iter_source_chunks(document):
        total += len(chunk)
        if total > max_bytes:
            raise StorageTransferError(code, message, status_code=413)
        yield chunk


def _write_stream_atomically(target: Path, chunks: Iterator[bytes]) -> int:
    """一時ファイルへ書いてから os.replace で原子的に差し替える。"""
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    written = 0
    file_descriptor, temp_name = tempfile.mkstemp(
        dir=str(target.parent), prefix=".transfer-", suffix=".part"
    )
    try:
        with os.fdopen(file_descriptor, "wb") as handle:
            for chunk in chunks:
                handle.write(chunk)
                written += len(chunk)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o640)
        os.replace(temp_name, target)
        _fsync_directory(target.parent)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temp_name)
        raise
    return written


def _fsync_directory(directory: Path) -> None:
    """ディレクトリエントリを永続化する。

    ``os.replace`` の後にディレクトリを fsync しないと、電源断で
    エントリが失われ「成功を返したのにファイルが無い」状態になり得る。
    ディレクトリを開けない環境では致命的ではないため握りつぶす。
    """
    try:
        directory_fd = os.open(directory, os.O_RDONLY)
    except OSError:
        logger.debug("Could not open directory for fsync: %s", directory)
        return
    try:
        os.fsync(directory_fd)
    except OSError:
        logger.debug("Could not fsync directory: %s", directory)
    finally:
        os.close(directory_fd)


def _filesystem_size_limit_bytes() -> int:
    settings = get_settings()
    return max(1, settings.CANONICAL_STORAGE_MAX_FILE_MB) * 1024 * 1024


def _store_to_filesystem(document: Document, relative_path: str) -> StorageResult:
    root = _storage_root()
    target = _contained_target(root, relative_path)
    chunks = _limited_chunks(
        document,
        _filesystem_size_limit_bytes(),
        "FILE_TOO_LARGE",
        "ファイルサイズが上限を超えています。",
    )
    try:
        size = _write_stream_atomically(target, chunks)
    except StorageTransferError:
        raise
    except OSError as exc:
        logger.exception("Failed to write canonical file: %s", target)
        raise StorageTransferError(
            "TRANSFER_FAILED", "正本ファイルの書き込みに失敗しました。"
        ) from exc
    return StorageResult(
        backend=BACKEND_FILESYSTEM, relative_path=relative_path, size_bytes=size
    )



def _onedrive_token(client: httpx.Client) -> str:
    settings = get_settings()
    url = (
        f"https://login.microsoftonline.com/{settings.ONEDRIVE_TENANT_ID}"
        "/oauth2/v2.0/token"
    )
    try:
        response = client.post(
            url,
            data={
                "client_id": settings.ONEDRIVE_CLIENT_ID,
                "client_secret": settings.ONEDRIVE_CLIENT_SECRET,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        token = response.json().get("access_token")
    except (httpx.HTTPError, ValueError) as exc:
        # client_secret を含むため、例外内容をそのまま外へ出さない
        logger.exception("OneDrive token acquisition failed")
        raise StorageTransferError(
            "ONEDRIVE_AUTH_FAILED",
            "OneDrive の認証に失敗しました。",
            status_code=503,
        ) from exc

    if not token:
        raise StorageTransferError(
            "ONEDRIVE_AUTH_FAILED", "OneDrive のアクセストークンを取得できませんでした。", 503
        )
    return token


def _store_to_onedrive(document: Document, relative_path: str) -> StorageResult:
    settings = get_settings()
    root_path = sanitize_path_component(
        settings.ONEDRIVE_ROOT_PATH, fallback="Mirai-Site-Admin-Workflow"
    )
    item_path = f"{root_path}/{relative_path}"
    max_bytes = min(
        max(1, settings.CANONICAL_STORAGE_MAX_FILE_MB) * 1024 * 1024,
        _GRAPH_SIMPLE_UPLOAD_LIMIT_BYTES,
    )

    # ファイル全体をメモリに載せない。一度一時ファイルへ落としてから
    # ストリームとして送る(並行転送時のメモリ枯渇を防ぐ)。
    file_descriptor, temp_name = tempfile.mkstemp(prefix=".onedrive-", suffix=".part")
    size = 0
    try:
        chunks = _limited_chunks(
            document,
            max_bytes,
            "FILE_TOO_LARGE_FOR_ONEDRIVE",
            "OneDriveの単純アップロード上限を超えています。分割アップロードは未対応です。",
        )
        with os.fdopen(file_descriptor, "wb") as handle:
            for chunk in chunks:
                handle.write(chunk)
                size += len(chunk)
            handle.flush()
            os.fsync(handle.fileno())

        with httpx.Client(timeout=settings.ONEDRIVE_GRAPH_TIMEOUT_SECONDS) as client:
            token = _onedrive_token(client)
            url = (
                "https://graph.microsoft.com/v1.0/drives/"
                f"{quote(settings.ONEDRIVE_DRIVE_ID, safe='')}"
                f"/root:/{quote(item_path, safe='/')}:/content"
            )
            with open(temp_name, "rb") as payload:
                response = client.put(
                    url,
                    content=payload,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": document.mime_type
                        or "application/octet-stream",
                    },
                )
            response.raise_for_status()
    except StorageTransferError:
        raise
    except httpx.HTTPError as exc:
        logger.exception("OneDrive upload failed: %s", item_path)
        raise StorageTransferError(
            "TRANSFER_FAILED", "OneDriveへのアップロードに失敗しました。"
        ) from exc
    except OSError as exc:
        logger.exception("OneDrive staging failed: %s", item_path)
        raise StorageTransferError(
            "TRANSFER_FAILED", "OneDriveアップロード用の一時ファイル作成に失敗しました。"
        ) from exc
    finally:
        with contextlib.suppress(OSError):
            os.unlink(temp_name)

    return StorageResult(
        backend=BACKEND_ONEDRIVE, relative_path=item_path, size_bytes=size
    )



def _transfer(document: Document, relative_path: str) -> StorageResult:
    backend = _resolve_backend()
    if backend == BACKEND_ONEDRIVE:
        return _store_to_onedrive(document, relative_path)
    return _store_to_filesystem(document, relative_path)


async def store_canonical(document: Document) -> StorageResult:
    """正本を実体ファイルとして保存する。"""
    return await asyncio.to_thread(_transfer, document, canonical_relative_path(document))


async def store_work_area(document: Document, receipt_no: str) -> StorageResult:
    """提出済み添付を受付番号単位の作業領域へ実体ファイルとして保存する。"""
    return await asyncio.to_thread(
        _transfer, document, work_area_relative_path(document, receipt_no)
    )
