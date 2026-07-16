import json

import httpx
import pytest

from app.collection.xiaohongshu_dom_adapter import XiaohongshuCollectionError


def make_gateway(handler):
    from app.collection.xiaohongshu_proxy_gateway import XiaohongshuProxyGateway

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://proxy.test")
    return XiaohongshuProxyGateway("http://proxy.test", "shared-token", client=client)


def test_proxy_gateway_posts_keyword_with_token_and_normalizes_cards() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/collections/xiaohongshu/search"
        assert request.headers["X-Collection-Proxy-Token"] == "shared-token"
        assert json.loads(request.content) == {"keyword": "skincare"}
        return httpx.Response(
            200,
            json=[
                {
                    "note_id": "note-1",
                    "url": "https://www.xiaohongshu.com/explore/note-1",
                    "title": "Routine",
                    "content": "Simple routine",
                    "author_id": "author-1",
                    "author_name": "Creator",
                    "content_type": "image",
                    "published_at": None,
                    "likes": "1.2w",
                    "favorites": None,
                    "comments": None,
                    "shares": None,
                }
            ],
        )

    cards = make_gateway(handler).search("skincare")

    assert cards[0].note_id == "note-1"
    assert cards[0].likes == "1.2w"


@pytest.mark.parametrize(
    ("response", "message"),
    [
        (httpx.ConnectError("offline"), "本地采集代理未启动"),
        (httpx.Response(401, json={"detail": "Unauthorized"}), "代理令牌"),
        (httpx.Response(422, json={"detail": "session expired"}), "session expired"),
    ],
)
def test_proxy_gateway_returns_safe_collection_errors(response, message: str) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        if isinstance(response, Exception):
            raise response
        return response

    with pytest.raises(XiaohongshuCollectionError, match=message):
        make_gateway(handler).search("skincare")
