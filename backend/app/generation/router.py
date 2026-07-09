from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.generation.schemas import (
    DraftExport,
    DraftRead,
    ReviewCreate,
    ReviewRead,
    TopicCreate,
    TopicRead,
)
from app.generation.service import GenerationService
from app.generation.template_adapter import TemplateGenerator

router = APIRouter(tags=["generation"])


def service(session: Session) -> GenerationService:
    return GenerationService(session, TemplateGenerator())


@router.post("/api/projects/{project_id}/topics", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
def create_topic(project_id: str, payload: TopicCreate, session: Session = Depends(get_session)) -> TopicRead:
    return service(session).create_topic(project_id, payload)


@router.post("/api/topics/{topic_id}/drafts/generate", response_model=list[DraftRead], status_code=status.HTTP_201_CREATED)
def generate_drafts(topic_id: str, session: Session = Depends(get_session)) -> list[DraftRead]:
    return service(session).generate(topic_id)


@router.post(
    "/api/draft-versions/{version_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def review_draft(
    version_id: str,
    payload: ReviewCreate,
    session: Session = Depends(get_session),
) -> ReviewRead:
    return service(session).review(version_id, payload)


@router.get("/api/draft-versions/{version_id}/export", response_model=DraftExport)
def export_draft(version_id: str, session: Session = Depends(get_session)) -> DraftExport:
    return service(session).export(version_id)

