from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.projects.models import utc_now


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(240))
    summary: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(16))
    analysis_version: Mapped[str] = mapped_column(String(32), default="relative-v1")
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    evidence: Mapped[list[Evidence]] = relationship(
        back_populates="insight",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    insight_id: Mapped[str] = mapped_column(ForeignKey("insights.id"))
    note_id: Mapped[str] = mapped_column(ForeignKey("notes.id"))
    metric_snapshot_id: Mapped[str] = mapped_column(ForeignKey("metric_snapshots.id"))
    summary: Mapped[str] = mapped_column(Text)
    contribution: Mapped[float] = mapped_column(Float)
    insight: Mapped[Insight] = relationship(back_populates="evidence")

