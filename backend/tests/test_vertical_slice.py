def test_fixed_sample_vertical_slice(client, project) -> None:
    imported = client.post(f"/api/projects/{project['id']}/collections/fixture")
    assert imported.status_code == 201

    report = client.post(f"/api/projects/{project['id']}/analysis/rank")
    assert report.status_code == 201

    topic = client.post(
        f"/api/projects/{project['id']}/topics",
        json={
            "title": "敏感肌直播前先做减法",
            "target_audience": "反复泛红且频繁换产品的人",
            "content_goal": "live_preview",
            "angle": "用两步自查降低试错",
            "insight_id": report.json()["insight"]["id"],
        },
    )
    assert topic.status_code == 201

    drafts = client.post(f"/api/topics/{topic.json()['id']}/drafts/generate")
    assert drafts.status_code == 201
    version_id = drafts.json()[0]["current_version"]["id"]

    assert client.get(f"/api/draft-versions/{version_id}/export").status_code == 409
    assert client.post(
        f"/api/draft-versions/{version_id}/reviews",
        json={"decision": "approved", "note": "final"},
    ).status_code == 201
    assert client.get(f"/api/draft-versions/{version_id}/export").status_code == 200
