import uvicorn

from app.collection.proxy_app import create_proxy_app
from app.collection.xiaohongshu_browser_gateway import XiaohongshuBrowserGateway
from app.core.config import Settings, get_settings


def build_proxy_app(settings: Settings) -> object:
    if not settings.collection_proxy_token:
        raise RuntimeError("COLLECTION_PROXY_TOKEN must be set before starting the local collection proxy")
    return create_proxy_app(XiaohongshuBrowserGateway(), settings.collection_proxy_token)


def main() -> None:
    uvicorn.run(build_proxy_app(get_settings()), host="0.0.0.0", port=17779)


if __name__ == "__main__":
    main()
