"""テスト共通設定"""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import create_app
from src.models.base import get_db

TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_ORG_ID = "22222222-2222-2222-2222-222222222222"
MOCK_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTExMTExMS0xMTExLTExMTEtMTExMS0xMTExMTExMTExMTEiLCJ0eXBlIjoidXNlciIsIm9yZyI6IjIyMjIyMjIyLTIyMjItMjIyMi0yMjIyLTIyMjIyMjIyMjIyMiIsInJvbGVzIjpbImFkbWluIl0sInNjb3BlcyI6W10sImlhdCI6OTk5OTk5OTk5OSwiZXhwIjo5OTk5OTk5OTk5LCJpc3MiOiJjZW8tb3MtYXV0aCIsImp0aSI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCJ9.1mNacRJpLN3zlgjRhP6xZ028j50u0BBoNt_j0QxfMc4"

SAMPLE_UUID = uuid.UUID("33333333-3333-3333-3333-333333333333")
NOW = datetime(2026, 5, 24, tzinfo=timezone.utc)


class MockResult:
    def __init__(self, scalar_value=None, scalars_list=None):
        self._scalar_value = scalar_value
        self._scalars_list = scalars_list

    def scalar(self):
        return self._scalar_value

    def scalar_one_or_none(self):
        return self._scalar_value

    def one_or_none(self):
        return self._scalar_value

    def scalars(self):
        mock = MagicMock()
        mock.all.return_value = self._scalars_list or []
        return mock


def make_mock_partner(**overrides):
    defaults = {
        "id": SAMPLE_UUID,
        "organization_id": uuid.UUID(TEST_ORG_ID),
        "name": "テスト建設株式会社",
        "name_kana": "テストケンセツ",
        "company_type": "subcontractor",
        "tax_id": None,
        "address": None,
        "phone": None,
        "email": "test@example.com",
        "website": None,
        "representative_name": "山田太郎",
        "employee_count": 50,
        "established_year": 2000,
        "specializations": ["civil"],
        "license_info": None,
        "insurance_info": None,
        "status": "active",
        "rating": 4.5,
        "registered_at": NOW,
        "updated_at": NOW,
        "contacts": [],
        "contracts": [],
        "evaluations": [],
        "assignments": [],
    }
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def make_mock_contract(**overrides):
    defaults = {
        "id": SAMPLE_UUID,
        "organization_id": uuid.UUID(TEST_ORG_ID),
        "partner_id": SAMPLE_UUID,
        "project_id": None,
        "contract_number": "CNT-2026-001",
        "title": "試験契約",
        "contract_type": "subcontract",
        "amount": 1000000.00,
        "currency": "JPY",
        "start_date": date(2026, 5, 1),
        "end_date": date(2027, 3, 31),
        "status": "active",
        "terms": None,
        "signed_by_our": None,
        "signed_by_partner": None,
        "signed_at": None,
        "created_at": NOW,
        "updated_at": NOW,
    }
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def make_mock_evaluation(**overrides):
    defaults = {
        "id": SAMPLE_UUID,
        "organization_id": uuid.UUID(TEST_ORG_ID),
        "partner_id": SAMPLE_UUID,
        "project_id": None,
        "evaluator_id": uuid.UUID(TEST_USER_ID),
        "overall_score": 4.5,
        "quality_score": 4.0,
        "safety_score": 5.0,
        "schedule_score": 4.0,
        "cost_score": 4.5,
        "communication_score": 4.5,
        "comment": "良い協力会社です",
        "evaluation_period_start": date(2026, 1, 1),
        "evaluation_period_end": date(2026, 3, 31),
        "created_at": NOW,
    }
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def make_mock_assignment(**overrides):
    defaults = {
        "id": SAMPLE_UUID,
        "organization_id": uuid.UUID(TEST_ORG_ID),
        "partner_id": SAMPLE_UUID,
        "project_id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
        "contract_id": None,
        "role": "元請け",
        "scope_of_work": "土木工事一式",
        "start_date": date(2026, 5, 1),
        "end_date": date(2026, 12, 31),
        "status": "active",
        "created_at": NOW,
    }
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def make_mock_contact(**overrides):
    defaults = {
        "id": SAMPLE_UUID,
        "partner_id": SAMPLE_UUID,
        "name": "佐藤花子",
        "title": "部長",
        "department": "工事部",
        "email": "sato@example.com",
        "phone": "03-1234-5678",
        "is_primary": True,
        "created_at": NOW,
    }
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


@pytest.fixture
def auth_headers():
    return {"Authorization": MOCK_TOKEN}


@pytest_asyncio.fixture
async def client():
    app_ = create_app()
    mock_session = AsyncMock()

    async def override_get_db():
        yield mock_session

    app_.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app_)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app_.dependency_overrides.clear()
