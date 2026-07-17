def test_vertical_research_collects_and_returns_top_candidates(client, project, monkeypatch) -> None:
    from app.core.config import get_settings
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    get_settings.cache_clear()
    response = client.post(f"/api/projects/{project['id']}/analysis/research?topic=普拉提产后修复&source=fixture")

    assert response.status_code == 201
    payload = response.json()
    assert payload["topic"] == "普拉提产后修复"
    assert payload["collected"]["notes_created"] == 3
    assert len(payload["top_candidates"]) == 3
    assert payload["collection_date"]
    assert payload["ai_report"]["disclosure"] == "发布时间未公开"
    get_settings.cache_clear()
