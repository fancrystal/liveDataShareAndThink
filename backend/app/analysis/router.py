from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.analysis.schemas import RankingReport
from app.analysis.service import AnalysisService
from app.collection.fixture_adapter import FixtureAdapter
from app.collection.models import CollectionRun
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
    from app.collection.xiaohongshu_dom_adapter import XiaohongshuCollectionError

    try:
        if source != "fixture":
            from app.collection.gateway_factory import build_xiaohongshu_gateway
            from app.collection.xiaohongshu_dom_adapter import XiaohongshuDomAdapter

            adapter = XiaohongshuDomAdapter(build_xiaohongshu_gateway(get_settings()))
        else:
            adapter = FixtureAdapter(get_settings().fixture_path)
        collected = CollectionService(session, adapter).import_keyword(project_id, topic)
    except XiaohongshuCollectionError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error

    run = session.get(CollectionRun, collected.run_id)
    if run is None or run.finished_at is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="本次采集记录不完整，请重新研究。")
    report = AnalysisService(session).rank(project_id, source_query=topic, collected_at=run.finished_at)
    candidates = [
        {
            "title": item["title"],
            "content": item["content"],
            "url": item["url"],
            "score": item["score"]["total"],
            "metrics": item["metrics"],
            "collected_at": item["collected_at"],
        }
        for item in report["rankings"][:20]
    ]
    settings = get_settings()
    if settings.deepseek_api_key:
        from app.analysis.deepseek_reporter import DeepSeekHotReporter

        try:
            ai_report = DeepSeekHotReporter(settings.deepseek_api_key, settings.deepseek_model, settings.deepseek_base_url).analyze(topic, candidates)
        except RuntimeError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="DeepSeek 爆款分析失败，请检查 API Key、模型配置和网络后重试。",
            ) from error
    else:
        ai_report = {"today_summary": "未配置 DeepSeek，以下为公开样本排名。", "hot_reasons": [], "replication_checklist": [], "disclosure": "发布时间未公开"}
    return {
        "topic": topic,
        "run_id": collected.run_id,
        "collection_date": report["insight"]["created_at"] if "created_at" in report["insight"] else "collected-now",
        "collected": collected.model_dump(),
        "top_candidates": candidates,
        "analysis": report,
        "ai_report": ai_report,
    }


@router.post("/post-package")
def create_post_package(
    project_id: str,
    topic: str,
    angle: str,
    run_id: str | None = None,
    session: Session = Depends(get_session),
) -> dict:
    run = session.get(CollectionRun, run_id) if run_id else None
    if run_id and (run is None or run.project_id != project_id or run.finished_at is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到本次研究的采集记录。")
    report = AnalysisService(session).rank(
        project_id,
        source_query=run.query if run else None,
        collected_at=run.finished_at if run else None,
    )
    evidence = [
        {
            "title": item["title"],
            "content": item["content"],
            "metrics": item["metrics"],
            "score": item["score"]["total"],
            "url": item["url"],
        }
        for item in report["rankings"][:20]
    ]
    settings = get_settings()
    if not settings.deepseek_api_key:
        return {"title": angle or topic, "caption": "请配置 DeepSeek 后生成完整图文内容。", "tags": [topic], "pages": [{"heading": f"第 {index} 页", "body": angle or topic} for index in range(1, 6)]}
    from app.generation.post_packager import DeepSeekPostPackager
    try:
        return DeepSeekPostPackager(settings.deepseek_api_key, settings.deepseek_model, settings.deepseek_base_url).create(topic, angle, evidence)
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="DeepSeek 图文生成失败，请检查 API Key、模型配置和网络后重试。",
        ) from error
