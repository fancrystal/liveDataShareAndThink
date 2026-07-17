def test_analysis_returns_ranked_notes_with_evidence(client, imported_project) -> None:
    response = client.post(f"/api/projects/{imported_project['id']}/analysis/rank")

    assert response.status_code == 201
    payload = response.json()
    assert len(payload["rankings"]) == 3
    assert payload["rankings"][0]["score"]["total"] >= payload["rankings"][1]["score"]["total"]
    assert payload["insight"]["confidence"] in {"medium", "high"}
    assert len(payload["insight"]["evidence"]) == 3
    assert payload["attraction_insight"]["result"]["format_counts"]
    assert len(payload["attraction_insight"]["evidence"]) == 3
