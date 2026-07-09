def test_fixture_import_is_idempotent(client, project) -> None:
    first = client.post(f"/api/projects/{project['id']}/collections/fixture")
    second = client.post(f"/api/projects/{project['id']}/collections/fixture")

    assert first.status_code == 201
    assert first.json()["notes_created"] == 3
    assert first.json()["metric_snapshots_created"] == 3
    assert second.status_code == 201
    assert second.json()["notes_created"] == 0
    assert second.json()["metric_snapshots_created"] == 3

    notes = client.get(f"/api/projects/{project['id']}/notes")
    assert notes.status_code == 200
    assert len(notes.json()) == 3
    assert all(note["source"]["adapter"] == "fixture" for note in notes.json())


def test_collection_rejects_unknown_project(client) -> None:
    response = client.post("/api/projects/missing/collections/fixture")

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}
