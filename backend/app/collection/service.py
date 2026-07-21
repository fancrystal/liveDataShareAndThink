from datetime import UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collection.models import Author, CollectionRun, MetricSnapshot, Note
from app.collection.ports import PlatformAdapter
from app.collection.schemas import CollectionSummary
from app.projects.service import ProjectService


class CollectionService:
    def __init__(self, session: Session, adapter: PlatformAdapter) -> None:
        self.session = session
        self.adapter = adapter

    def import_keyword(self, project_id: str, keyword: str) -> CollectionSummary:
        ProjectService(self.session).get(project_id)
        payload = self.adapter.search_notes(keyword)
        collected_at = payload.collected_at.astimezone(UTC)
        run = CollectionRun(project_id=project_id, adapter=self.adapter.name, query=keyword)
        self.session.add(run)
        notes_created = 0
        snapshots_created = 0

        for item in payload.notes:
            author = self.session.scalar(
                select(Author).where(
                    Author.platform == "xiaohongshu",
                    Author.platform_author_id == item.author.platform_author_id,
                )
            )
            if author is None:
                author = Author(
                    platform_author_id=item.author.platform_author_id,
                    nickname=item.author.nickname,
                    followers=item.author.followers,
                    raw_data=item.author.model_dump(),
                )
                self.session.add(author)
                self.session.flush()
            else:
                author.nickname = item.author.nickname
                author.followers = item.author.followers

            note = self.session.scalar(
                select(Note).where(
                    Note.project_id == project_id,
                    Note.platform == "xiaohongshu",
                    Note.platform_note_id == item.platform_note_id,
                )
            )
            source = {
                "adapter": self.adapter.name,
                "query": payload.query,
                "collected_at": collected_at.isoformat(),
            }
            if note is None:
                note = Note(
                    project_id=project_id,
                    author_id=author.id,
                    platform_note_id=item.platform_note_id,
                    url=item.url,
                    title=item.title,
                    content=item.content,
                    content_type=item.content_type,
                    published_at=item.published_at,
                    source=source,
                    raw_data=item.model_dump(mode="json"),
                    first_collected_at=collected_at,
                    last_collected_at=collected_at,
                )
                self.session.add(note)
                self.session.flush()
                notes_created += 1
            else:
                note.last_collected_at = collected_at
                note.source = source

            self.session.add(
                MetricSnapshot(
                    note_id=note.id,
                    collected_at=collected_at,
                    followers=item.author.followers,
                    **item.metrics.model_dump(),
                )
            )
            snapshots_created += 1

        run.status = "succeeded"
        run.finished_at = collected_at
        run.notes_created = notes_created
        run.metric_snapshots_created = snapshots_created
        self.session.commit()
        return CollectionSummary(
            run_id=run.id,
            status=run.status,
            notes_created=notes_created,
            metric_snapshots_created=snapshots_created,
        )

    def list_notes(self, project_id: str) -> list[Note]:
        ProjectService(self.session).get(project_id)
        return list(self.session.scalars(select(Note).where(Note.project_id == project_id).order_by(Note.published_at)))

    def list_runs(self, project_id: str) -> list[CollectionRun]:
        ProjectService(self.session).get(project_id)
        return list(
            self.session.scalars(
                select(CollectionRun)
                .where(CollectionRun.project_id == project_id)
                .order_by(CollectionRun.started_at.desc())
            )
        )
