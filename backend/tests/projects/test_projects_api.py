def test_create_and_read_project(client, project_payload) -> None:
    created = client.post("/api/projects", json=project_payload)

    assert created.status_code == 201
    project_id = created.json()["id"]

    fetched = client.get(f"/api/projects/{project_id}")

    assert fetched.status_code == 200
    assert fetched.json()["brand_profile"]["positioning"] == "成分透明的敏感肌护肤"


def test_list_projects(client, project_payload) -> None:
    client.post("/api/projects", json=project_payload)

    response = client.get("/api/projects")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["护肤直播增长"]
