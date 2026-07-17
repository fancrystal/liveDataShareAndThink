from fastapi.testclient import TestClient

from app.main import create_app
from app.core.config import get_settings


def test_health_returns_service_status() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "live-data-share-and-think",
        "phase": "content-growth",
    }


def test_local_web_origin_is_allowed() -> None:
    client = TestClient(create_app())

    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_docker_web_origin_is_allowed() -> None:
    client = TestClient(create_app())

    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:17777",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:17777"


def test_collection_proxy_status_never_returns_the_proxy_token(monkeypatch) -> None:
    monkeypatch.setenv("COLLECTION_PROXY_URL", "http://host.docker.internal:17779")
    monkeypatch.setenv("COLLECTION_PROXY_TOKEN", "private-token")
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/api/collection-proxy/status")

    assert response.status_code == 200
    assert response.json() == {"configured": True, "message": "Local collection proxy configured"}
    assert "private-token" not in response.text
    get_settings.cache_clear()
