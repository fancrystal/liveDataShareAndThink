from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CollectedAuthor(BaseModel):
    platform_author_id: str
    nickname: str
    followers: int | None = None


class CollectedMetrics(BaseModel):
    likes: int | None = None
    favorites: int | None = None
    comments: int | None = None
    shares: int | None = None


class CollectedNote(BaseModel):
    platform_note_id: str
    url: str
    author: CollectedAuthor
    title: str
    content: str
    content_type: str
    published_at: datetime | None
    metrics: CollectedMetrics


class FixturePayload(BaseModel):
    source: str
    query: str
    collected_at: datetime
    notes: list[CollectedNote]


class CollectionSummary(BaseModel):
    run_id: str
    status: str
    notes_created: int
    metric_snapshots_created: int


class CollectionRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    adapter: str
    query: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    notes_created: int
    metric_snapshots_created: int


class MetricSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    collected_at: datetime
    likes: int | None
    favorites: int | None
    comments: int | None
    shares: int | None
    followers: int | None


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nickname: str
    followers: int | None


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    platform_note_id: str
    url: str
    title: str
    content: str
    content_type: str
    published_at: datetime | None
    source: dict
    author: AuthorRead
    metric_snapshots: list[MetricSnapshotRead]
