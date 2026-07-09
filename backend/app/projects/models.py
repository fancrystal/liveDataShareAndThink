from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    brand_profile: Mapped[BrandProfile] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined",
    )


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    positioning: Mapped[str] = mapped_column(Text)
    target_audience: Mapped[str] = mapped_column(Text)
    tone: Mapped[str] = mapped_column(Text)
    core_value: Mapped[str] = mapped_column(Text)
    forbidden_terms: Mapped[list[str]] = mapped_column(JSON, default=list)
    project: Mapped[Project] = relationship(back_populates="brand_profile")

