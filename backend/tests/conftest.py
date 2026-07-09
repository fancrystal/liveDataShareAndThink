from collections.abc import Iterator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    with TestClient(create_app(database_url=database_url)) as test_client:
        yield test_client


@pytest.fixture
def project_payload() -> dict:
    return {
        "name": "护肤直播增长",
        "description": "研究敏感肌直播引流",
        "brand_profile": {
            "name": "小鹿护肤",
            "positioning": "成分透明的敏感肌护肤",
            "target_audience": "25-35岁敏感肌女性",
            "tone": "专业、克制、友好",
            "core_value": "降低试错成本",
            "forbidden_terms": ["根治", "百分百有效"],
        },
    }


@pytest.fixture
def project(client: TestClient, project_payload: dict) -> dict:
    response = client.post("/api/projects", json=project_payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def imported_project(client: TestClient, project: dict) -> dict:
    response = client.post(f"/api/projects/{project['id']}/collections/fixture")
    assert response.status_code == 201
    return project


@pytest.fixture
def analyzed_project(client: TestClient, imported_project: dict) -> dict:
    response = client.post(f"/api/projects/{imported_project['id']}/analysis/rank")
    assert response.status_code == 201
    return {**imported_project, "insight_id": response.json()["insight"]["id"]}

