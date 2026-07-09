from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.collection.fixture_adapter import FixtureAdapter
from app.collection.schemas import CollectionSummary, NoteRead
from app.collection.service import CollectionService
from app.core.config import get_settings
from app.db.session import get_session

router = APIRouter(prefix="/api/projects/{project_id}", tags=["collection"])


def fixture_service(session: Session) -> CollectionService:
    return CollectionService(session, FixtureAdapter(get_settings().fixture_path))


@router.post("/collections/fixture", response_model=CollectionSummary, status_code=status.HTTP_201_CREATED)
def import_fixture(project_id: str, session: Session = Depends(get_session)) -> CollectionSummary:
    return fixture_service(session).import_keyword(project_id, "敏感肌")


@router.get("/notes", response_model=list[NoteRead])
def list_notes(project_id: str, session: Session = Depends(get_session)) -> list[NoteRead]:
    return fixture_service(session).list_notes(project_id)

