"""認証・認可 データモデル"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (
        Index("ix_organizations_parent_id", "parent_id"),
        Index("ix_organizations_type", "type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.organizations.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_kana: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(
        Enum("company", "department", "site", "partner", name="org_type"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", name="org_status"), default="active"
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # リレーション
    parent = relationship("Organization", remote_side=[id], backref="children")
    users: Mapped[list["User"]] = relationship("User", back_populates="organization")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_username", "username"),
        Index("ix_users_organization_id", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.organizations.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    locale: Mapped[str] = mapped_column(String(10), default="ja")
    status: Mapped[str] = mapped_column(
        Enum("pending", "active", "suspended", "deactivated", name="user_status"),
        default="pending",
    )
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")
    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", foreign_keys="UserRole.user_id")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        Index("ix_roles_organization_id", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.organizations.id")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    permissions: Mapped[list["RolePermission"]] = relationship("RolePermission", back_populates="role")
    users: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("resource", "action"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    roles: Mapped[list["RolePermission"]] = relationship("RolePermission", back_populates="permission")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.roles.id"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.permissions.id"), primary_key=True
    )

    role: Mapped["Role"] = relationship("Role", back_populates="permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="roles")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.users.id"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.roles.id"), primary_key=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.users.id")
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates="roles", foreign_keys=[user_id])
    role: Mapped["Role"] = relationship("Role", back_populates="users")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_tokens_token_hash", "token_hash"),
        Index("ix_refresh_tokens_user_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_info: Mapped[dict | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(INET)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class ApiClient(Base):
    __tablename__ = "api_clients"
    __table_args__ = (
        Index("ix_api_clients_client_id", "client_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    client_secret_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("active", "revoked", name="api_client_status"), default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_event_type", "event_type"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[dict | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
