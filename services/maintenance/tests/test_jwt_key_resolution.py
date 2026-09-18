"""JWT 検証鍵の解決の回帰テスト。

他17サービスは JWT_PUBLIC_KEY を参照するが、これら5サービスだけが
JWT_SECRET_KEY を参照していたため、JWT_PUBLIC_KEY を一括設定しても
反映されず(公開された開発用既定値のまま)、鍵ローテーションが
無言で失敗していた。両方を受け付けることを固定する。
"""

from src.config import Settings


def test_jwt_public_key_is_honoured():
    settings = Settings(JWT_PUBLIC_KEY="rotated-key", JWT_SECRET_KEY="old-key")
    assert settings.jwt_public_key == "rotated-key"


def test_legacy_jwt_secret_key_still_works():
    settings = Settings(JWT_PUBLIC_KEY="", JWT_SECRET_KEY="legacy-key")
    assert settings.jwt_public_key == "legacy-key"


def test_falls_back_to_development_placeholder():
    settings = Settings(JWT_PUBLIC_KEY="", JWT_SECRET_KEY="")
    assert settings.jwt_public_key == "dev-only-do-not-use-in-production"


def test_middleware_uses_the_resolved_key():
    import inspect

    from src.middleware import auth as auth_module

    source = inspect.getsource(auth_module)
    assert "settings.jwt_public_key" in source
    assert "settings.JWT_SECRET_KEY" not in source
