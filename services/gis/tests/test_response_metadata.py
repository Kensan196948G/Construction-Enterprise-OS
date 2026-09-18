"""レスポンスモデルが ORM の metadata_ を読めることの回帰テスト。

SQLAlchemy の宣言的 Base では `metadata` が MetaData 予約属性になるため、
レスポンスモデルが素の `metadata` を読むと MetaData オブジェクトを拾って
バリデーションエラーになり、読み取り API が HTTP 500 になる。
"""

from pydantic import ValidationError

from src.models import ConstructionSite, HazardZone, Infrastructure
from src.schemas import HazardZoneResponse, InfrastructureResponse, SiteResponse



def test_SiteResponse_reads_orm_metadata_attribute():
    instance = ConstructionSite()
    instance.metadata_ = {"regression": True}

    validated = None
    try:
        validated = SiteResponse.model_validate(instance)
    except ValidationError as exc:
        missing = {error["loc"][0] for error in exc.errors() if error.get("loc")}
        assert "metadata" not in missing, (
            "metadata が ORM の metadata_ ではなく MetaData を読んでいる"
        )

    if validated is not None:
        assert validated.metadata == {"regression": True}


def test_InfrastructureResponse_reads_orm_metadata_attribute():
    instance = Infrastructure()
    instance.metadata_ = {"regression": True}

    validated = None
    try:
        validated = InfrastructureResponse.model_validate(instance)
    except ValidationError as exc:
        missing = {error["loc"][0] for error in exc.errors() if error.get("loc")}
        assert "metadata" not in missing, (
            "metadata が ORM の metadata_ ではなく MetaData を読んでいる"
        )

    if validated is not None:
        assert validated.metadata == {"regression": True}


def test_HazardZoneResponse_reads_orm_metadata_attribute():
    instance = HazardZone()
    instance.metadata_ = {"regression": True}

    validated = None
    try:
        validated = HazardZoneResponse.model_validate(instance)
    except ValidationError as exc:
        missing = {error["loc"][0] for error in exc.errors() if error.get("loc")}
        assert "metadata" not in missing, (
            "metadata が ORM の metadata_ ではなく MetaData を読んでいる"
        )

    if validated is not None:
        assert validated.metadata == {"regression": True}
