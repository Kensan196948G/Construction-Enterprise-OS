"""レスポンスモデルが ORM の metadata_ を読めることの回帰テスト。

SQLAlchemy の宣言的 Base では `metadata` が MetaData 予約属性になるため、
レスポンスモデルが素の `metadata` を読むと MetaData オブジェクトを拾って
バリデーションエラーになり、読み取り API が HTTP 500 になる。
"""

from pydantic import ValidationError

from src.models import Device
from src.schemas import DeviceResponse


def test_DeviceResponse_reads_orm_metadata_attribute():
    # alias が外れると MetaData を読んで 500 になる。ここで設定自体を固定する。
    field = DeviceResponse.model_fields["metadata"]
    assert str(field.validation_alias) == "metadata_"

    instance = Device()
    instance.metadata_ = {"regression": True}

    validated = None
    try:
        validated = DeviceResponse.model_validate(instance)
    except ValidationError as exc:
        missing = {error["loc"][0] for error in exc.errors() if error.get("loc")}
        assert "metadata" not in missing, (
            "metadata が ORM の metadata_ ではなく MetaData を読んでいる"
        )

    if validated is not None:
        assert validated.metadata == {"regression": True}
