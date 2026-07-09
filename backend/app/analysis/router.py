from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.analysis.schemas import RankingReport
from app.analysis.service import AnalysisService
from app.db.session import get_session

router = APIRouter(prefix="/api/projects/{project_id}/analysis", tags=["analysis"])


@router.post("/rank", response_model=RankingReport, status_code=status.HTTP_201_CREATED)
def rank_notes(project_id: str, session: Session = Depends(get_session)) -> RankingReport:
    return AnalysisService(session).rank(project_id)

