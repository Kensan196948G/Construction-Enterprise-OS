"""Initial auth schema

Revision ID: 001
Revises: None
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INET, ENUM

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create auth schema
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")

    # Create enum types
    op.execute(
        "CREATE TYPE auth.org_type AS ENUM "
        "('company', 'department', 'site', 'partner')"
    )
    op.execute(
        "CREATE TYPE auth.org_status AS ENUM ('active', 'inactive')"
    )
    op.execute(
        "CREATE TYPE auth.user_status AS ENUM "
        "('pending', 'active', 'suspended', 'deactivated')"
    )
    op.execute(
        "CREATE TYPE auth.api_client_status AS ENUM ('active', 'revoked')"
    )

    # organizations
    op.create_table(
        'organizations',
        sa.Column(
            'id', UUID(as_uuid=True), primary_key=True,
            server_default=sa.text('gen_random_uuid()')
        ),
        sa.Column(
            'parent_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.organizations.id')
        ),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('name_kana', sa.String(255)),
        sa.Column(
            'type',
            ENUM(
                'company', 'department', 'site', 'partner',
                name='org_type', schema='auth', create_type=False
            ),
            nullable=False,
        ),
        sa.Column(
            'status',
            ENUM(
                'active', 'inactive',
                name='org_status', schema='auth', create_type=False
            ),
            server_default='active',
        ),
        sa.Column('metadata', JSONB, server_default='{}'),
        sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        schema='auth'
    )
    op.create_index(
        'ix_organizations_parent_id', 'organizations',
        ['parent_id'], schema='auth'
    )
    op.create_index(
        'ix_organizations_type', 'organizations',
        ['type'], schema='auth'
    )

    # users
    op.create_table(
        'users',
        sa.Column(
            'id', UUID(as_uuid=True), primary_key=True,
            server_default=sa.text('gen_random_uuid()')
        ),
        sa.Column(
            'organization_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.organizations.id'), nullable=False
        ),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('locale', sa.String(10), server_default='ja'),
        sa.Column(
            'status',
            ENUM(
                'pending', 'active', 'suspended', 'deactivated',
                name='user_status', schema='auth', create_type=False
            ),
            server_default='pending',
        ),
        sa.Column('mfa_enabled', sa.Boolean, server_default='false'),
        sa.Column('mfa_secret', sa.String(255)),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column(
            'password_changed_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column('login_attempts', sa.Integer, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True)),
        sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        schema='auth'
    )
    op.create_index('ix_users_email', 'users', ['email'], schema='auth')
    op.create_index(
        'ix_users_username', 'users', ['username'], schema='auth'
    )
    op.create_index(
        'ix_users_organization_id', 'users',
        ['organization_id'], schema='auth'
    )

    # roles
    op.create_table(
        'roles',
        sa.Column(
            'id', UUID(as_uuid=True), primary_key=True,
            server_default=sa.text('gen_random_uuid()')
        ),
        sa.Column(
            'organization_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.organizations.id')
        ),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_system', sa.Boolean, server_default='false'),
        sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        schema='auth'
    )
    op.create_index(
        'ix_roles_organization_id', 'roles',
        ['organization_id'], schema='auth'
    )

    # permissions
    op.create_table(
        'permissions',
        sa.Column(
            'id', UUID(as_uuid=True), primary_key=True,
            server_default=sa.text('gen_random_uuid()')
        ),
        sa.Column('resource', sa.String(255), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        schema='auth'
    )
    op.create_unique_constraint(
        'uq_permissions_resource_action', 'permissions',
        ['resource', 'action'], schema='auth'
    )

    # role_permissions
    op.create_table(
        'role_permissions',
        sa.Column(
            'role_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.roles.id'), primary_key=True
        ),
        sa.Column(
            'permission_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.permissions.id'), primary_key=True
        ),
        schema='auth'
    )

    # user_roles
    op.create_table(
        'user_roles',
        sa.Column(
            'user_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.users.id'), primary_key=True
        ),
        sa.Column(
            'role_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.roles.id'), primary_key=True
        ),
        sa.Column(
            'assigned_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column(
            'assigned_by', UUID(as_uuid=True),
            sa.ForeignKey('auth.users.id')
        ),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        schema='auth'
    )

    # refresh_tokens
    op.create_table(
        'refresh_tokens',
        sa.Column(
            'id', UUID(as_uuid=True), primary_key=True,
            server_default=sa.text('gen_random_uuid()')
        ),
        sa.Column(
            'user_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.users.id'), nullable=False
        ),
        sa.Column(
            'token_hash', sa.String(255), unique=True, nullable=False
        ),
        sa.Column('device_info', JSONB),
        sa.Column('ip_address', INET),
        sa.Column(
            'expires_at', sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        schema='auth'
    )
    op.create_index(
        'ix_refresh_tokens_token_hash', 'refresh_tokens',
        ['token_hash'], schema='auth'
    )
    op.create_index(
        'ix_refresh_tokens_user_id', 'refresh_tokens',
        ['user_id'], schema='auth'
    )

    # api_clients
    op.create_table(
        'api_clients',
        sa.Column(
            'id', UUID(as_uuid=True), primary_key=True,
            server_default=sa.text('gen_random_uuid()')
        ),
        sa.Column(
            'organization_id', UUID(as_uuid=True),
            sa.ForeignKey('auth.organizations.id'), nullable=False
        ),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column(
            'client_id', sa.String(100), unique=True, nullable=False
        ),
        sa.Column(
            'client_secret_hash', sa.String(255), nullable=False
        ),
        sa.Column('scopes', ARRAY(sa.String), nullable=False),
        sa.Column(
            'status',
            ENUM(
                'active', 'revoked',
                name='api_client_status', schema='auth', create_type=False
            ),
            server_default='active',
        ),
        sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        schema='auth'
    )
    op.create_index(
        'ix_api_clients_client_id', 'api_clients',
        ['client_id'], schema='auth'
    )

    # audit_logs
    op.create_table(
        'audit_logs',
        sa.Column(
            'id', sa.Integer, primary_key=True, autoincrement=True
        ),
        sa.Column('user_id', UUID(as_uuid=True)),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_data', JSONB),
        sa.Column('ip_address', INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('success', sa.Boolean, nullable=False),
        sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        schema='auth'
    )
    op.create_index(
        'ix_audit_logs_user_id', 'audit_logs',
        ['user_id'], schema='auth'
    )
    op.create_index(
        'ix_audit_logs_event_type', 'audit_logs',
        ['event_type'], schema='auth'
    )
    op.create_index(
        'ix_audit_logs_created_at', 'audit_logs',
        ['created_at'], schema='auth'
    )


def downgrade() -> None:
    op.execute('DROP TABLE IF EXISTS auth.audit_logs CASCADE')
    op.execute('DROP TABLE IF EXISTS auth.api_clients CASCADE')
    op.execute('DROP TABLE IF EXISTS auth.refresh_tokens CASCADE')
    op.execute('DROP TABLE IF EXISTS auth.user_roles CASCADE')
    op.execute('DROP TABLE IF EXISTS auth.role_permissions CASCADE')
    op.execute('DROP TABLE IF EXISTS auth.permissions CASCADE')
    op.execute('DROP TABLE IF EXISTS auth.roles CASCADE')
    op.execute('DROP TABLE IF EXISTS auth.users CASCADE')
    op.execute('DROP TABLE IF EXISTS auth.organizations CASCADE')

    op.execute('DROP TYPE IF EXISTS auth.api_client_status CASCADE')
    op.execute('DROP TYPE IF EXISTS auth.user_status CASCADE')
    op.execute('DROP TYPE IF EXISTS auth.org_status CASCADE')
    op.execute('DROP TYPE IF EXISTS auth.org_type CASCADE')

    op.execute('DROP SCHEMA IF EXISTS auth CASCADE')
