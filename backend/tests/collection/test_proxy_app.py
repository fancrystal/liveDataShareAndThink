from fastapi.testclient import TestClient

from app.collection.xiaohongshu_dom_adapter import PublicSearchCard


class FakeGateway:
    def __init__(self) -> None:
        self.keywords: list[str] = []

    def search(self, keyword: str) -> list[PublicSearchCard]:
        self.keywords.append(keyword)
        return [
            PublicSearchCard(
                note_id="note-1",
                url="https://www.xiaohongshu.com/explore/note-1",
                title="Sensitive skin routine",
                content="Keep the routine simple.",
                author_id="author-1",
                author_name="Creator",
                content_type="image",
                published_at=None,
                likes="123",
            )
        ]


def build_client() -> tuple[TestClient, FakeGateway]:
    from app.collection.proxy_app import create_proxy_app

    gateway = FakeGateway()
    return TestClient(create_proxy_app(gateway, token="test-token")), gateway


def test_proxy_rejects_missing_or_wrong_token() -> None:
    client, _ = build_client()

    response = client.post("/api/collections/xiaohongshu/search", json={"keyword": "skincare"})

    assert response.status_code == 401


def test_proxy_rejects_blank_keyword() -> None:
    client, _ = build_client()

    response = client.post(
        "/api/collections/xiaohongshu/search",
        headers={"X-Collection-Proxy-Token": "test-token"},
        json={"keyword": "   "},
    )

    assert response.status_code == 422


def test_proxy_delegates_authenticated_search_to_gateway() -> None:
    client, gateway = build_client()

    response = client.post(
        "/api/collections/xiaohongshu/search",
        headers={"X-Collection-Proxy-Token": "test-token"},
        json={"keyword": "skincare"},
    )

    assert response.status_code == 200
    assert gateway.keywords == ["skincare"]
    assert response.json()[0]["note_id"] == "note-1"
    assert response.json()[0]["likes"] == "123"
