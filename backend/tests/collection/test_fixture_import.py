from datetime import UTC, datetime

import app.collection.router as collection_router
from app.collection.schemas import CollectedAuthor, CollectedMetrics, CollectedNote, FixturePayload


class FakeRedbookAdapter:
    @property
    def name(self) -> str:
        return "redbook"

    def search_notes(self, keyword: str) -> FixturePayload:
        return FixturePayload(
            source="redbook",
            query=keyword,
            collected_at=datetime.now(UTC),
            notes=[
                CollectedNote(
                    platform_note_id="redbook-note-1",
                    url="https://www.xiaohongshu.com/explore/redbook-note-1",
                    author=CollectedAuthor(platform_author_id="redbook-author-1", nickname="测试作者"),
                    title="真实采集测试笔记",
                    content="用于验证 API。",
                    content_type="image",
                    published_at=datetime(2026, 7, 10, tzinfo=UTC),
                    metrics=CollectedMetrics(likes=12, favorites=4, comments=2),
                )
            ],
        )


def test_redbook_import_uses_collection_service(client, project, monkeypatch) -> None:
    monkeypatch.setattr(collection_router, "RedbookAdapter", FakeRedbookAdapter)

    response = client.post(f"/api/projects/{project['id']}/collections/redbook?keyword=敏感肌")

    assert response.status_code == 201
    assert response.json()["notes_created"] == 1

    notes = client.get(f"/api/projects/{project['id']}/notes")
    assert notes.status_code == 200
    assert notes.json()[0]["source"]["adapter"] == "redbook"


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
