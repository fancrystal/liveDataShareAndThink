from datetime import timezone
from statistics import median

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analysis.models import Evidence, Insight
from app.analysis.patterns import ContentSample, derive_content_attraction_patterns
from app.analysis.scoring import MetricInput, score_note, weighted_engagement
from app.collection.models import MetricSnapshot, Note
from app.projects.service import ProjectService


class AnalysisService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def rank(self, project_id: str) -> dict:
        ProjectService(self.session).get(project_id)
        notes = list(self.session.scalars(select(Note).where(Note.project_id == project_id)))
        latest: list[tuple[Note, MetricSnapshot]] = [
            (note, note.metric_snapshots[-1]) for note in notes if note.metric_snapshots
        ]
        inputs: list[tuple[Note, MetricSnapshot, MetricInput]] = []
        for note, snapshot in latest:
            collected_at = snapshot.collected_at
            published_at = note.published_at
            if collected_at.tzinfo is None:
                collected_at = collected_at.replace(tzinfo=timezone.utc)
            if published_at is not None and published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            inputs.append(
                (
                    note,
                    snapshot,
                    MetricInput(
                        likes=snapshot.likes,
                        favorites=snapshot.favorites,
                        comments=snapshot.comments,
                        shares=snapshot.shares,
                        followers=snapshot.followers,
                        age_hours=(
                            max((collected_at - published_at).total_seconds() / 3600, 1)
                            if published_at is not None
                            else None
                        ),
                    ),
                )
            )
        cohort_median = median([weighted_engagement(item) for _, _, item in inputs]) if inputs else 1
        ranked = [
            {
                "note": note,
                "snapshot": snapshot,
                "score": score_note(metric_input, cohort_median, len(inputs)),
            }
            for note, snapshot, metric_input in inputs
        ]
        ranked.sort(key=lambda item: item["score"].total, reverse=True)
        confidence = "high" if len(ranked) >= 3 else "medium" if ranked else "low"
        insight = Insight(
            project_id=project_id,
            type="relative_performance",
            title="小红书样本相对表现",
            summary=f"在 {len(ranked)} 条样本中识别相对高表现内容。",
            confidence=confidence,
            result={"ranking_note_ids": [item["note"].id for item in ranked]},
        )
        self.session.add(insight)
        self.session.flush()
        evidence_rows = []
        for item in ranked:
            evidence = Evidence(
                insight_id=insight.id,
                note_id=item["note"].id,
                metric_snapshot_id=item["snapshot"].id,
                summary=f"{item['note'].title}：相对表现 {item['score'].total}",
                contribution=item["score"].total,
            )
            self.session.add(evidence)
            evidence_rows.append(evidence)

        patterns = derive_content_attraction_patterns(
            [
                ContentSample(
                    note_id=item["note"].id,
                    title=item["note"].title,
                    content=item["note"].content,
                    content_type=item["note"].content_type,
                )
                for item in ranked[:3]
            ]
        )
        attraction_insight = Insight(
            project_id=project_id,
            type="content_attraction_patterns",
            title="内容引流模式",
            summary="基于当前公开样本归纳标题钩子、内容形式与可复用选题方向。",
            confidence=confidence,
            analysis_version="content-patterns-v1",
            result={
                "hook_patterns": patterns.hook_patterns,
                "format_counts": patterns.format_counts,
                "reusable_angles": list(patterns.reusable_angles),
                "note_ids": list(patterns.note_ids),
            },
        )
        self.session.add(attraction_insight)
        self.session.flush()
        attraction_evidence = []
        for item in ranked[:3]:
            evidence = Evidence(
                insight_id=attraction_insight.id,
                note_id=item["note"].id,
                metric_snapshot_id=item["snapshot"].id,
                summary=f"内容样本：{item['note'].title}",
                contribution=item["score"].total,
            )
            self.session.add(evidence)
            attraction_evidence.append(evidence)
        self.session.commit()

        return {
            "rankings": [
                {
                    "note_id": item["note"].id,
                    "title": item["note"].title,
                    "url": item["note"].url,
                    "score": item["score"].to_dict(),
                }
                for item in ranked
            ],
            "insight": self._insight_read(insight, evidence_rows),
            "attraction_insight": self._insight_read(attraction_insight, attraction_evidence),
        }

    @staticmethod
    def _insight_read(insight: Insight, evidence_rows: list[Evidence]) -> dict:
        return {
            "id": insight.id,
            "title": insight.title,
            "summary": insight.summary,
            "confidence": insight.confidence,
            "analysis_version": insight.analysis_version,
            "result": insight.result,
            "evidence": [
                {
                    "id": row.id,
                    "note_id": row.note_id,
                    "metric_snapshot_id": row.metric_snapshot_id,
                    "summary": row.summary,
                    "contribution": row.contribution,
                }
                for row in evidence_rows
            ],
        }
