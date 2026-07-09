from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.projects.models import utc_now


class TopicIdea(Base):
    __tablename__ = "topic_ideas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    insight_id: Mapped[str] = mapped_column(ForeignKey("insights.id"))
    title: Mapped[str] = mapped_column(String(240))
    target_audience: Mapped[str] = mapped_column(Text)
    content_goal: Mapped[str] = mapped_column(String(32))
    angle: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="candidate")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Draft(Base):
    __tablename__ = "drafts"
    __table_args__ = (UniqueConstraint("topic_id", "variant"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topic_id: Mapped[str] = mapped_column(ForeignKey("topic_ideas.id"))
    variant: Mapped[str] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(24), default="pending_review")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    versions: Mapped[list[DraftVersion]] = relationship(
        back_populates="draft",
        cascade="all, delete-orphan",
        order_by="DraftVersion.version",
        lazy="joined",
    )


class DraftVersion(Base):
    __tablename__ = "draft_versions"
    __table_args__ = (UniqueConstraint("draft_id", "version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    draft_id: Mapped[str] = mapped_column(ForeignKey("drafts.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(JSON)
    cover_text: Mapped[str] = mapped_column(String(120))
    evidence_ids: Mapped[list[str]] = mapped_column(JSON)
    generator: Mapped[str] = mapped_column(String(64))
    input_context: Mapped[dict] = mapped_column(JSON)
    validation: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    draft: Mapped[Draft] = relationship(back_populates="versions")
    reviews: Mapped[list[Review]] = relationship(
        back_populates="draft_version",
        cascade="all, delete-orphan",
        order_by="Review.created_at",
    )


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    draft_version_id: Mapped[str] = mapped_column(ForeignKey("draft_versions.id"))
    decision: Mapped[str] = mapped_column(String(24))
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    draft_version: Mapped[DraftVersion] = relationship(back_populates="reviews")

