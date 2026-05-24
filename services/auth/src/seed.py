"""初期シードデータ投入（冪等）
使い方:
    cd services/auth && python -m src.seed
"""
import asyncio
import uuid
from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy import func, select

from src.models.base import async_session
from src.models import (
    Organization,
    User,
    Role,
    Permission,
    RolePermission,
    UserRole,
    AuditLog,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── シード用 固定UUID ──────────────────────────────────────────────
ADMIN_ORG_ID      = uuid.UUID("00000000-0000-0000-0000-000000000001")
ADMIN_USER_ID     = uuid.UUID("00000000-0000-0000-0000-000000000002")

# ── 既定ロール名 ────────────────────────────────────────────────────
DEFAULT_ROLES = [
    ("admin",            "システム管理者。すべての権限を持つ", True),
    ("site_manager",     "現場所長。現場の全権限を持つ", False),
    ("site_supervisor",  "現場監督。日次管理と承認", False),
    ("site_worker",      "現場作業員。閲覧と報告中心", False),
    ("inspector",        "検査官。品質・安全管理の監査", False),
    ("accountant",       "経理担当。ERPと経営データの管理", False),
    ("readonly",         "閲覧専用。全リソースの参照のみ", False),
]

# ── 既定パーミッション ──────────────────────────────────────────────
# (resource, action, description)
DEFAULT_PERMISSIONS = [
    ("users",         "read",    "ユーザー情報の閲覧"),
    ("users",         "create",  "ユーザーの作成"),
    ("users",         "update",  "ユーザー情報の更新"),
    ("users",         "delete",  "ユーザーの削除"),
    ("roles",          "read",    "ロール情報の閲覧"),
    ("roles",          "create",  "ロールの作成"),
    ("roles",          "update",  "ロール情報の更新"),
    ("roles",          "delete",  "ロールの削除"),
    ("permissions",    "read",    "権限一覧の閲覧"),
    ("organizations",  "read",    "組織情報の閲覧"),
    ("organizations",  "create",  "組織の作成"),
    ("organizations",  "update",  "組織情報の更新"),
    ("organizations",  "delete",  "組織の削除"),
    ("documents",      "read",    "文書の閲覧"),
    ("documents",      "create",  "文書の作成"),
    ("documents",      "update",  "文書の更新"),
    ("documents",      "approve", "文書の承認"),
    ("documents",      "delete",  "文書の削除"),
    ("projects",       "read",    "工事情報の閲覧"),
    ("projects",       "create",  "工事の作成"),
    ("projects",       "update",  "工事情報の更新"),
    ("projects",       "delete",  "工事の削除"),
    ("workflow",       "read",    "ワークフローの閲覧"),
    ("workflow",       "approve", "ワークフローの承認"),
    ("iot",            "read",    "IoTデータの閲覧"),
    ("iot",            "ingest",  "IoTデータの送信"),
    ("gis",            "read",    "GISデータの閲覧"),
    ("bim",            "read",    "BIMデータの閲覧"),
    ("safety",         "read",    "安全管理データの閲覧"),
    ("safety",         "report",  "安全報告の作成"),
    ("safety",         "manage",  "安全管理の統括"),
    ("quality",        "read",    "品質管理データの閲覧"),
    ("quality",        "report",  "品質報告の作成"),
    ("quality",        "manage",  "品質管理の統括"),
    ("erp",            "read",    "経営データの閲覧"),
    ("erp",            "create",  "経営データの作成"),
    ("erp",            "update",  "経営データの更新"),
    ("partner",        "read",    "協力会社情報の閲覧"),
    ("partner",        "manage",  "協力会社の管理"),
    ("audit",          "read",    "監査ログの閲覧"),
    ("api_clients",    "read",    "APIクライアント情報の閲覧"),
    ("api_clients",    "create",  "APIクライアントの作成"),
    ("api_clients",    "revoke",  "APIクライアントの無効化"),
]

# ── ロール → パーミッション割当 ────────────────────────────────────
# key=ロール名, value=許可する (resource, action) の tuple
ROLE_PERMISSION_MAP = {
    "admin": [
        # ALL permissions
        (r, a) for r, a, _ in DEFAULT_PERMISSIONS
    ],
    "site_manager": [
        ("projects",  "read"),    ("projects",  "create"),
        ("projects",  "update"),  ("projects",  "delete"),
        ("documents", "read"),    ("documents", "create"),
        ("documents", "update"),  ("documents", "approve"),
        ("documents", "delete"),
        ("workflow",  "read"),    ("workflow",  "approve"),
        ("safety",    "read"),    ("safety",    "report"),
        ("safety",    "manage"),
        ("quality",   "read"),    ("quality",   "report"),
        ("quality",   "manage"),
        ("iot",       "read"),    ("gis",       "read"),
        ("bim",       "read"),    ("partner",   "read"),
        ("partner",   "manage"),
        ("users",     "read"),    ("roles",     "read"),
        ("permissions","read"),   ("audit",     "read"),
        ("organizations","read"),
    ],
    "site_supervisor": [
        ("projects",  "read"),    ("projects",  "update"),
        ("documents", "read"),    ("documents", "create"),
        ("documents", "update"),
        ("workflow",  "read"),    ("workflow",  "approve"),
        ("safety",    "read"),    ("safety",    "report"),
        ("quality",   "read"),    ("quality",   "report"),
        ("iot",       "read"),    ("gis",       "read"),
        ("bim",       "read"),
    ],
    "site_worker": [
        ("projects",  "read"),    ("documents", "read"),
        ("safety",    "read"),    ("safety",    "report"),
        ("quality",   "read"),    ("quality",   "report"),
        ("iot",       "read"),    ("iot",       "ingest"),
    ],
    "inspector": [
        ("projects",  "read"),    ("documents", "read"),
        ("safety",    "read"),    ("safety",    "report"),
        ("safety",    "manage"),
        ("quality",   "read"),    ("quality",   "report"),
        ("quality",   "manage"),
        ("bim",       "read"),
    ],
    "accountant": [
        ("erp",       "read"),    ("erp",       "create"),
        ("erp",       "update"),
        ("projects",  "read"),    ("documents", "read"),
        ("audit",     "read"),
    ],
    "readonly": [
        ("users",         "read"),
        ("roles",          "read"),
        ("permissions",    "read"),
        ("organizations",  "read"),
        ("documents",      "read"),
        ("projects",       "read"),
        ("workflow",       "read"),
        ("iot",            "read"),
        ("gis",            "read"),
        ("bim",            "read"),
        ("safety",         "read"),
        ("quality",        "read"),
        ("erp",            "read"),
        ("partner",        "read"),
        ("audit",          "read"),
        ("api_clients",    "read"),
    ],
}

# ── 管理ユーザ ──────────────────────────────────────────────────────
ADMIN_EMAIL = "admin@construction-enterprise-os.local"
ADMIN_PASSWORD = "AdminPass123!"
ADMIN_DISPLAY_NAME = "システム管理者"


async def run_seed() -> None:
    """シード実行（冪等）"""
    async with async_session() as db:

        # --- 1. 組織 ---
        result = await db.execute(
            select(Organization).where(Organization.id == ADMIN_ORG_ID)
        )
        org = result.scalar_one_or_none()
        if org is None:
            org = Organization(
                id=ADMIN_ORG_ID,
                name="Construction-Enterprise-OS 本社",
                name_kana="シーイーオーオーエスホンシャ",
                type="company",
                status="active",
                metadata_={"address": "東京都千代田区丸の内1-1-1", "established": "2024-04-01"},
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(org)
            await db.flush()
            print("[seed] organization created: Construction-Enterprise-OS 本社")
        else:
            print("[seed] organization already exists: Construction-Enterprise-OS 本社")

        # --- 2. ロール ---
        role_map: dict[str, Role] = {}
        for role_name, description, is_system in DEFAULT_ROLES:
            result = await db.execute(
                select(Role).where(
                    Role.name == role_name,
                    Role.organization_id == ADMIN_ORG_ID,
                )
            )
            role = result.scalar_one_or_none()
            if role is None:
                role = Role(
                    id=uuid.uuid4(),
                    organization_id=ADMIN_ORG_ID,
                    name=role_name,
                    description=description,
                    is_system=is_system,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(role)
                await db.flush()
                print(f"[seed] role created: {role_name}")
            else:
                print(f"[seed] role already exists: {role_name}")
            role_map[role_name] = role

        # --- 3. パーミッション ---
        perm_map: dict[tuple[str, str], Permission] = {}
        for resource, action, description in DEFAULT_PERMISSIONS:
            result = await db.execute(
                select(Permission).where(
                    Permission.resource == resource,
                    Permission.action == action,
                )
            )
            perm = result.scalar_one_or_none()
            if perm is None:
                perm = Permission(
                    id=uuid.uuid4(),
                    resource=resource,
                    action=action,
                    description=description,
                )
                db.add(perm)
                await db.flush()
                print(f"[seed] permission created: {resource}:{action}")
            else:
                print(f"[seed] permission already exists: {resource}:{action}")
            perm_map[(resource, action)] = perm

        # --- 4. ロール⇔パーミッション ---
        for role_name, perm_keys in ROLE_PERMISSION_MAP.items():
            role = role_map[role_name]
            for resource, action in perm_keys:
                perm = perm_map.get((resource, action))
                if perm is None:
                    print(
                        f"[seed] WARNING: permission not found: "
                        f"{resource}:{action} for role {role_name}"
                    )
                    continue

                result = await db.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm.id,
                    )
                )
                existing_rp = result.scalar_one_or_none()
                if existing_rp is None:
                    rp = RolePermission(role_id=role.id, permission_id=perm.id)
                    db.add(rp)
        await db.flush()
        print("[seed] role-permission assignments complete")

        # --- 5. 管理ユーザ ---
        result = await db.execute(
            select(User).where(User.id == ADMIN_USER_ID)
        )
        admin = result.scalar_one_or_none()
        if admin is None:
            admin = User(
                id=ADMIN_USER_ID,
                organization_id=ADMIN_ORG_ID,
                email=ADMIN_EMAIL,
                username="admin",
                hashed_password=pwd_context.hash(ADMIN_PASSWORD),
                display_name=ADMIN_DISPLAY_NAME,
                phone="03-0000-0001",
                locale="ja",
                status="active",
                mfa_enabled=False,
                login_attempts=0,
                password_changed_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(admin)
            await db.flush()
            print(f"[seed] admin user created: {ADMIN_EMAIL}")
        else:
            print(f"[seed] admin user already exists: {ADMIN_EMAIL}")

        # --- 6. 管理ユーザに admin ロールを割当 ---
        admin_role = role_map["admin"]
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == ADMIN_USER_ID,
                UserRole.role_id == admin_role.id,
            )
        )
        ur = result.scalar_one_or_none()
        if ur is None:
            ur = UserRole(
                user_id=ADMIN_USER_ID,
                role_id=admin_role.id,
                assigned_at=datetime.now(timezone.utc),
            )
            db.add(ur)
            await db.flush()
            print("[seed] admin role assigned to admin user")
        else:
            print("[seed] admin role already assigned to admin user")

        # --- 7. 監査ログ ---
        audit_count = await db.execute(
            select(func.count()).select_from(AuditLog)
        )
        count = audit_count.scalar()
        if count == 0:
            log = AuditLog(
                user_id=ADMIN_USER_ID,
                event_type="system.seed",
                event_data={
                    "action": "initial_setup",
                    "roles_created": len(DEFAULT_ROLES),
                    "permissions_created": len(DEFAULT_PERMISSIONS),
                },
                ip_address=None,
                user_agent=None,
                success=True,
                created_at=datetime.now(timezone.utc),
            )
            db.add(log)
            await db.flush()
            print("[seed] audit log created: initial setup")
        else:
            print(f"[seed] audit logs already exist ({count} entries)")

        await db.commit()
        print("[seed] ALL DONE")


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
