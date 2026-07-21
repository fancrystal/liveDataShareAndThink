def test_vertical_research_collects_and_returns_top_candidates(client, project, monkeypatch) -> None:
    from app.core.config import get_settings
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    get_settings.cache_clear()
    response = client.post(f"/api/projects/{project['id']}/analysis/research?topic=普拉提产后修复&source=fixture")

    assert response.status_code == 201
    payload = response.json()
    assert payload["topic"] == "普拉提产后修复"
    assert payload["run_id"]
    assert payload["collected"]["notes_created"] == 3
    assert len(payload["top_candidates"]) == 3
    assert payload["collection_date"]
    assert payload["ai_report"]["disclosure"] == "发布时间未公开"
    get_settings.cache_clear()


def test_vertical_research_returns_a_readable_cors_safe_collection_error(client, project, monkeypatch) -> None:
    from app.collection.gateway_factory import build_xiaohongshu_gateway
    from app.collection.xiaohongshu_dom_adapter import XiaohongshuCollectionError

    class FailingGateway:
        def search(self, keyword: str):
            raise XiaohongshuCollectionError("本地采集代理暂不可用，请启动后重试。")

    monkeypatch.setattr(
        "app.collection.gateway_factory.build_xiaohongshu_gateway",
        lambda _settings: FailingGateway(),
    )

    response = client.post(
        f"/api/projects/{project['id']}/analysis/research?topic=北京火锅",
        headers={"Origin": "http://127.0.0.1:17777"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "本地采集代理暂不可用，请启动后重试。"
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:17777"
