from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analysis.models import Insight
from app.generation.models import Draft, DraftVersion, Review, TopicIdea
from app.generation.ports import ContentGenerator, GenerationBrief
from app.generation.schemas import ReviewCreate, TopicCreate
from app.projects.service import ProjectService


class GenerationService:
    def __init__(self, session: Session, generator: ContentGenerator) -> None:
        self.session = session
        self.generator = generator

    def create_topic(self, project_id: str, payload: TopicCreate) -> TopicIdea:
        ProjectService(self.session).get(project_id)
        insight = self.session.get(Insight, payload.insight_id)
        if insight is None or insight.project_id != project_id:
            raise HTTPException(status_code=404, detail="Insight not found")
        topic = TopicIdea(project_id=project_id, **payload.model_dump())
        self.session.add(topic)
        self.session.commit()
        self.session.refresh(topic)
        return topic

    def generate(self, topic_id: str) -> list[dict]:
        topic = self.session.get(TopicIdea, topic_id)
        if topic is None:
            raise HTTPException(status_code=404, detail="Topic not found")
        project = ProjectService(self.session).get(topic.project_id)
        insight = self.session.get(Insight, topic.insight_id)
        evidence = insight.evidence if insight else []
        brief = GenerationBrief(
            topic=topic.title,
            audience=topic.target_audience,
            goal=topic.content_goal,
            angle=topic.angle,
            brand_tone=project.brand_profile.tone,
            forbidden_terms=tuple(project.brand_profile.forbidden_terms),
            evidence_summaries=tuple(row.summary for row in evidence),
        )
        generated = self.generator.generate(brief)
        if len(generated) != 3 or len({item.title for item in generated}) != 3:
            raise HTTPException(status_code=422, detail="Generator must return three unique variants")
        results = []
        for item in generated:
            if not item.title or not item.body or len(item.title) > 20:
                raise HTTPException(status_code=422, detail="Generated content failed validation")
            combined = f"{item.title}\n{item.body}"
            if any(term in combined for term in brief.forbidden_terms):
                raise HTTPException(status_code=422, detail="Generated content contains forbidden terms")
            draft = Draft(topic_id=topic.id, variant=item.variant)
            self.session.add(draft)
            self.session.flush()
            version = DraftVersion(
                draft_id=draft.id,
                version=1,
                title=item.title,
                body=item.body,
                tags=list(item.tags),
                cover_text=item.cover_text,
                evidence_ids=[row.id for row in evidence],
                generator=self.generator.name,
                input_context={
                    "topic": brief.topic,
                    "audience": brief.audience,
                    "goal": brief.goal,
                    "angle": brief.angle,
                },
                validation={"valid": True, "forbidden_terms_checked": True},
            )
            self.session.add(version)
            self.session.flush()
            results.append(self._draft_read(draft, version))
        topic.status = "generated"
        self.session.commit()
        return results

    def review(self, version_id: str, payload: ReviewCreate) -> Review:
        version = self.session.get(DraftVersion, version_id)
        if version is None:
            raise HTTPException(status_code=404, detail="Draft version not found")
        review = Review(draft_version_id=version_id, **payload.model_dump())
        version.draft.status = "approved" if payload.decision == "approved" else "returned"
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return review

    def export(self, version_id: str) -> dict:
        version = self.session.get(DraftVersion, version_id)
        if version is None:
            raise HTTPException(status_code=404, detail="Draft version not found")
        if not any(review.decision == "approved" for review in version.reviews):
            raise HTTPException(status_code=409, detail="Draft version is not approved")
        return {
            "title": version.title,
            "body": version.body,
            "tags": version.tags,
            "cover_text": version.cover_text,
            "evidence_ids": version.evidence_ids,
            "version": version.version,
            "status": "approved",
        }

    @staticmethod
    def _draft_read(draft: Draft, version: DraftVersion) -> dict:
        return {
            "id": draft.id,
            "variant": draft.variant,
            "status": draft.status,
            "evidence_ids": version.evidence_ids,
            "current_version": {
                "id": version.id,
                "version": version.version,
                "title": version.title,
                "body": version.body,
                "tags": version.tags,
                "cover_text": version.cover_text,
                "generator": version.generator,
            },
        }

