"""レスポンスモデルが ORM の metadata_ を読めることの回帰テスト。

SQLAlchemy の宣言的 Base では `metadata` が MetaData 予約属性になるため、
レスポンスモデルが素の `metadata` を読むと MetaData オブジェクトを拾って
バリデーションエラーになり、読み取り API が HTTP 500 になる。
"""

from pydantic import ValidationError

from src.models import BIMModel, PointCloud
from src.schemas import BIMModelResponse, PointCloudResponse



def test_BIMModelResponse_reads_orm_metadata_attribute():
    instance = BIMModel()
    instance.metadata_ = {"regression": True}

    validated = None
    try:
        validated = BIMModelResponse.model_validate(instance)
    except ValidationError as exc:
        missing = {error["loc"][0] for error in exc.errors() if error.get("loc")}
        assert "metadata" not in missing, (
            "metadata が ORM の metadata_ ではなく MetaData を読んでいる"
        )

    if validated is not None:
        assert validated.metadata == {"regression": True}


def test_PointCloudResponse_reads_orm_metadata_attribute():
    instance = PointCloud()
    instance.metadata_ = {"regression": True}

    validated = None
    try:
        validated = PointCloudResponse.model_validate(instance)
    except ValidationError as exc:
        missing = {error["loc"][0] for error in exc.errors() if error.get("loc")}
        assert "metadata" not in missing, (
            "metadata が ORM の metadata_ ではなく MetaData を読んでいる"
        )

    if validated is not None:
        assert validated.metadata == {"regression": True}
