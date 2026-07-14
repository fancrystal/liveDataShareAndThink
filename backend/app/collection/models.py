from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.projects.models import utc_now


class Author(Base):
    __tablename__ = "authors"
    __table_args__ = (UniqueConstraint("platform", "platform_author_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    platform: Mapped[str] = mapped_column(String(32), default="xiaohongshu")
    platform_author_id: Mapped[str] = mapped_column(String(120))
    nickname: Mapped[str] = mapped_column(String(120))
    followers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (UniqueConstraint("project_id", "platform", "platform_note_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.id"))
    platform: Mapped[str] = mapped_column(String(32), default="xiaohongshu")
    platform_note_id: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(240))
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(32))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[dict] = mapped_column(JSON)
    raw_data: Mapped[dict] = mapped_column(JSON)
    first_collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    author: Mapped[Author] = relationship(lazy="joined")
    metric_snapshots: Mapped[list[MetricSnapshot]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        order_by="MetricSnapshot.collected_at",
    )


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    note_id: Mapped[str] = mapped_column(ForeignKey("notes.id"))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    favorites: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    followers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[Note] = relationship(back_populates="metric_snapshots")


class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    adapter: Mapped[str] = mapped_column(String(64))
    query: Mapped[str] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(32), default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes_created: Mapped[int] = mapped_column(Integer, default=0)
    metric_snapshots_created: Mapped[int] = mapped_column(Integer, default=0)
