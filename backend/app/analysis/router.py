from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.analysis.schemas import RankingReport
from app.analysis.service import AnalysisService
from app.collection.fixture_adapter import FixtureAdapter
from app.collection.service import CollectionService
from app.core.config import get_settings
from app.db.session import get_session

router = APIRouter(prefix="/api/projects/{project_id}/analysis", tags=["analysis"])


@router.post("/rank", response_model=RankingReport, status_code=status.HTTP_201_CREATED)
def rank_notes(project_id: str, session: Session = Depends(get_session)) -> RankingReport:
    return AnalysisService(session).rank(project_id)


@router.post("/research", status_code=status.HTTP_201_CREATED)
def run_vertical_research(
    project_id: str,
    topic: str,
    source: str = "xiaohongshu",
    session: Session = Depends(get_session),
) -> dict:
    if source != "fixture":
        from app.collection.gateway_factory import build_xiaohongshu_gateway
        from app.collection.xiaohongshu_dom_adapter import XiaohongshuDomAdapter

        adapter = XiaohongshuDomAdapter(build_xiaohongshu_gateway(get_settings()))
    else:
        adapter = FixtureAdapter(get_settings().fixture_path)
    collected = CollectionService(session, adapter).import_keyword(project_id, topic)
    report = AnalysisService(session).rank(project_id)
    candidates = [{"title": item["title"], "url": item["url"], "score": item["score"]["total"]} for item in report["rankings"][:20]]
    settings = get_settings()
    if settings.deepseek_api_key:
        from app.analysis.deepseek_reporter import DeepSeekHotReporter

        ai_report = DeepSeekHotReporter(settings.deepseek_api_key, settings.deepseek_model, settings.deepseek_base_url).analyze(topic, candidates)
    else:
        ai_report = {"today_summary": "未配置 DeepSeek，以下为公开样本排名。", "hot_reasons": [], "replication_checklist": [], "disclosure": "发布时间未公开"}
    return {
        "topic": topic,
        "collection_date": report["insight"]["created_at"] if "created_at" in report["insight"] else "collected-now",
        "collected": collected.model_dump(),
        "top_candidates": candidates,
        "analysis": report,
        "ai_report": ai_report,
    }
