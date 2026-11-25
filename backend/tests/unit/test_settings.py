import importlib
import sys
from types import ModuleType

import pytest
from django.core.exceptions import ImproperlyConfigured

PROD = "config.settings.prod"
REQUIRED = ("SECRET_KEY", "ALLOWED_HOSTS", "CORS_ALLOWED_ORIGINS")


def _load_prod() -> ModuleType:
    sys.modules.pop(PROD, None)
    return importlib.import_module(PROD)


@pytest.fixture
def prod_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    monkeypatch.setenv("SECRET_KEY", "x" * 50)
    monkeypatch.setenv("ALLOWED_HOSTS", "galeway-api.onrender.com")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://galeway.pages.dev")
    return monkeypatch


@pytest.mark.usefixtures("prod_env")
def test_prod_settings_are_hardened() -> None:
    prod = _load_prod()

    assert prod.DEBUG is False
    assert prod.SECURE_SSL_REDIRECT is True
    assert prod.SECURE_HSTS_SECONDS == 31536000
    assert prod.X_FRAME_OPTIONS == "DENY"
    assert prod.CORS_ALLOWED_ORIGINS == ["https://galeway.pages.dev"]
    assert "galeway-api.onrender.com" in prod.ALLOWED_HOSTS


@pytest.mark.parametrize("missing", REQUIRED)
def test_prod_fails_fast_when_a_required_variable_is_missing(
    prod_env: pytest.MonkeyPatch, missing: str
) -> None:
    prod_env.delenv(missing)

    with pytest.raises(ImproperlyConfigured):
        _load_prod()
