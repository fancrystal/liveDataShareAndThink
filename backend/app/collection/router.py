from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.collection.fixture_adapter import FixtureAdapter
from app.collection.redbook_adapter import RedbookAdapter, RedbookAdapterError
from app.collection.schemas import CollectionSummary, NoteRead
from app.collection.service import CollectionService
from app.core.config import get_settings
from app.db.session import get_session

router = APIRouter(prefix="/api/projects/{project_id}", tags=["collection"])


def fixture_service(session: Session) -> CollectionService:
    return CollectionService(session, FixtureAdapter(get_settings().fixture_path))


def redbook_service(session: Session) -> CollectionService:
    return CollectionService(session, RedbookAdapter())


@router.post("/collections/fixture", response_model=CollectionSummary, status_code=status.HTTP_201_CREATED)
def import_fixture(project_id: str, session: Session = Depends(get_session)) -> CollectionSummary:
    return fixture_service(session).import_keyword(project_id, "敏感肌")


@router.post("/collections/redbook", response_model=CollectionSummary, status_code=status.HTTP_201_CREATED)
def import_redbook(
    project_id: str,
    keyword: str,
    session: Session = Depends(get_session),
) -> CollectionSummary:
    try:
        return redbook_service(session).import_keyword(project_id, keyword)
    except RedbookAdapterError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


@router.get("/notes", response_model=list[NoteRead])
def list_notes(project_id: str, session: Session = Depends(get_session)) -> list[NoteRead]:
    return fixture_service(session).list_notes(project_id)
