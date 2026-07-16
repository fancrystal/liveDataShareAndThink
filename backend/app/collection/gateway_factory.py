from app.collection.xiaohongshu_browser_gateway import XiaohongshuBrowserGateway
from app.collection.xiaohongshu_proxy_gateway import XiaohongshuProxyGateway
from app.core.config import Settings


def build_xiaohongshu_gateway(settings: Settings) -> XiaohongshuBrowserGateway | XiaohongshuProxyGateway:
    if settings.collection_proxy_url:
        return XiaohongshuProxyGateway(settings.collection_proxy_url, settings.collection_proxy_token)
    return XiaohongshuBrowserGateway()
