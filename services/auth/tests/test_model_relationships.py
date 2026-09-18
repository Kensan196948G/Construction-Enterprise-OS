"""ORM リレーションの回帰テスト。

Organization と ApiClient の間に relationship が無いと、SQLAlchemy が
同一 flush での挿入順を保証できず、ApiClient が Organization より先に
INSERT されて外部キー違反になる(実DBで再現確認済み)。
"""

from src.models import ApiClient, Organization


def test_organization_and_api_client_are_linked_by_relationship():
    assert "organization" in ApiClient.__mapper__.relationships, (
        "ApiClient.organization が無いと同一flushで挿入順が保証されない"
    )
    assert "api_clients" in Organization.__mapper__.relationships, (
        "Organization.api_clients が無いと back_populates が解決できない"
    )


def test_relationship_targets_are_correct():
    rel = ApiClient.__mapper__.relationships["organization"]
    assert rel.mapper.class_ is Organization
    assert rel.back_populates == "api_clients"
