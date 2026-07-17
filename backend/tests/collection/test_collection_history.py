def test_collection_history_returns_latest_runs_first(client, imported_project) -> None:
    project_id = imported_project["id"]
    second = client.post(f"/api/projects/{project_id}/collections/fixture")
    assert second.status_code == 201

    response = client.get(f"/api/projects/{project_id}/collections")

    assert response.status_code == 200
    runs = response.json()
    assert len(runs) == 2
    assert runs[0]["adapter"] == "fixture"
    assert runs[0]["status"] == "succeeded"
    assert runs[0]["notes_created"] == 0
