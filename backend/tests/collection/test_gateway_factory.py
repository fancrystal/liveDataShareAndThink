from app.collection.xiaohongshu_browser_gateway import XiaohongshuBrowserGateway
from app.core.config import Settings


def test_factory_uses_direct_browser_gateway_without_proxy_url() -> None:
    from app.collection.gateway_factory import build_xiaohongshu_gateway

    gateway = build_xiaohongshu_gateway(Settings(collection_proxy_url=None, collection_proxy_token=None))

    assert isinstance(gateway, XiaohongshuBrowserGateway)


def test_factory_uses_proxy_gateway_when_proxy_url_is_configured() -> None:
    from app.collection.gateway_factory import build_xiaohongshu_gateway
    from app.collection.xiaohongshu_proxy_gateway import XiaohongshuProxyGateway

    gateway = build_xiaohongshu_gateway(
        Settings(collection_proxy_url="http://host.docker.internal:17779", collection_proxy_token="token")
    )

    assert isinstance(gateway, XiaohongshuProxyGateway)
