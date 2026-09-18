"""BIM ORM の mapper 構成が成立することの回帰テスト。

bim_elements.model_id に ForeignKey が無いと relationship の join 条件を
解決できず、mapper 構成時に NoForeignKeysError となり BIM サービスの
DB アクセスが全滅する。
"""

from sqlalchemy.orm import configure_mappers


def test_mappers_configure_without_error():
    import src.models  # noqa: F401  (mapper 登録のため import が必要)

    configure_mappers()
