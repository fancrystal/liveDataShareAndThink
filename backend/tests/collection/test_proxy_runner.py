import pytest

from app.core.config import Settings


def test_build_proxy_app_uses_direct_browser_gateway_and_configured_token() -> None:
    from app.collection.proxy_runner import build_proxy_app

    app = build_proxy_app(Settings(collection_proxy_token="test-token"))

    assert app.title == "LiveDataShareAndThink Local Collection Proxy"


def test_build_proxy_app_requires_a_proxy_token() -> None:
    from app.collection.proxy_runner import build_proxy_app

    with pytest.raises(RuntimeError, match="COLLECTION_PROXY_TOKEN"):
        build_proxy_app(Settings(collection_proxy_token=None))
