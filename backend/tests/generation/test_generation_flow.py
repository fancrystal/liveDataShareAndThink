def test_topic_generates_three_reviewable_versions(client, analyzed_project) -> None:
    topic_response = client.post(
        f"/api/projects/{analyzed_project['id']}/topics",
        json={
            "title": "敏感肌直播前先做减法",
            "target_audience": "反复泛红且频繁换产品的人",
            "content_goal": "live_preview",
            "angle": "用两步自查降低试错",
            "insight_id": analyzed_project["insight_id"],
        },
    )
    assert topic_response.status_code == 201
    topic = topic_response.json()

    generated = client.post(f"/api/topics/{topic['id']}/drafts/generate")

    assert generated.status_code == 201
    drafts = generated.json()
    assert len(drafts) == 3
    assert {draft["variant"] for draft in drafts} == {"practical", "story", "contrarian"}
    assert all(draft["evidence_ids"] for draft in drafts)

    version_id = drafts[0]["current_version"]["id"]
    blocked = client.get(f"/api/draft-versions/{version_id}/export")
    assert blocked.status_code == 409

    approved = client.post(
        f"/api/draft-versions/{version_id}/reviews",
        json={"decision": "approved", "note": "可用"},
    )
    assert approved.status_code == 201

    exported = client.get(f"/api/draft-versions/{version_id}/export")
    assert exported.status_code == 200
    assert exported.json()["status"] == "approved"
    assert exported.json()["evidence_ids"]


def test_topic_requires_insight_from_same_project(client, project) -> None:
    response = client.post(
        f"/api/projects/{project['id']}/topics",
        json={
            "title": "没有证据的选题",
            "target_audience": "测试人群",
            "content_goal": "live_preview",
            "angle": "测试",
            "insight_id": "missing",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Insight not found"}
