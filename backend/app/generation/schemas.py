from typing import Literal

from pydantic import BaseModel, Field


ContentGoal = Literal["live_preview", "live_booking", "post_live_followup"]


class TopicCreate(BaseModel):
    title: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    content_goal: ContentGoal
    angle: str = Field(min_length=1)
    insight_id: str


class TopicRead(TopicCreate):
    id: str
    project_id: str
    status: str


class DraftVersionRead(BaseModel):
    id: str
    version: int
    title: str
    body: str
    tags: list[str]
    cover_text: str
    generator: str


class DraftRead(BaseModel):
    id: str
    variant: str
    status: str
    evidence_ids: list[str]
    current_version: DraftVersionRead


class ReviewCreate(BaseModel):
    decision: Literal["returned", "approved"]
    note: str = ""


class ReviewRead(ReviewCreate):
    id: str
    draft_version_id: str


class DraftExport(BaseModel):
    title: str
    body: str
    tags: list[str]
    cover_text: str
    evidence_ids: list[str]
    version: int
    status: str

