"""API リクエスト/レスポンス スキーマ"""

from datetime import datetime
from uuid import UUID

from typing import Generic, TypeVar

from pydantic import BaseModel, EmailStr, Field

T = TypeVar("T")


# ============================================
# 共通
# ============================================
class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    error: "ErrorDetail | None" = None
    meta: "MetaInfo | None" = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict] | None = None


class MetaInfo(BaseModel):
    page: int | None = None
    per_page: int | None = None
    total: int | None = None
    total_pages: int | None = None


# ============================================
# 認証
# ============================================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_name: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    requires_mfa: bool = False
    mfa_session_token: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    sub: str  # user_id or client_id
    type: str  # "user" or "client"
    org: str | None = None
    roles: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    device_id: str | None = None


class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    session_token: str
    code: str


class MFADisableRequest(BaseModel):
    password: str
    code: str


# ============================================
# ユーザー
# ============================================
class UserCreateRequest(BaseModel):
    organization_id: UUID
    email: EmailStr
    username: str | None = None
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=255)
    phone: str | None = None
    role_ids: list[UUID] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    display_name: str | None = None
    phone: str | None = None
    locale: str | None = None
    status: str | None = None  # "active", "suspended", "deactivated"


class UserResponse(BaseModel):
    id: UUID
    organization_id: UUID
    email: str
    username: str | None
    display_name: str
    phone: str | None
    locale: str
    status: str
    mfa_enabled: bool
    last_login_at: datetime | None
    created_at: datetime
    roles: list["RoleSummary"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)


# ============================================
# ロール
# ============================================
class RoleCreateRequest(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    permission_ids: list[UUID] = Field(default_factory=list)


class RoleUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleSummary(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    is_system: bool
    created_at: datetime
    permissions: list["PermissionSummary"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class RoleAssignRequest(BaseModel):
    user_id: UUID
    role_id: UUID
    expires_at: datetime | None = None


# ============================================
# 権限
# ============================================
class PermissionSummary(BaseModel):
    id: UUID
    resource: str
    action: str

    model_config = {"from_attributes": True}


class PermissionResponse(BaseModel):
    id: UUID
    resource: str
    action: str
    description: str | None

    model_config = {"from_attributes": True}


# ============================================
# APIクライアント
# ============================================
class ApiClientCreateRequest(BaseModel):
    name: str
    scopes: list[str]


class ApiClientCreateResponse(BaseModel):
    id: UUID
    name: str
    client_id: str
    client_secret: str  # 作成時のみ返却
    scopes: list[str]


class ApiClientResponse(BaseModel):
    id: UUID
    name: str
    client_id: str
    scopes: list[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
