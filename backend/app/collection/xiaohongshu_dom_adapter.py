from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from app.collection.schemas import CollectedAuthor, CollectedMetrics, CollectedNote, FixturePayload


class XiaohongshuCollectionError(Exception):
    """A credential-safe error raised when public Xiaohongshu cards cannot be imported."""


@dataclass(frozen=True)
class PublicSearchCard:
    note_id: str
    url: str
    title: str
    content: str
    author_id: str
    author_name: str
    content_type: str
    published_at: str
    likes: str | None = None
    favorites: str | None = None
    comments: str | None = None
    shares: str | None = None


class SearchGateway(Protocol):
    def search(self, keyword: str) -> list[PublicSearchCard]: ...


def parse_visible_count(value: str | None) -> int | None:
    if value is None:
        return None

    text = value.replace(",", "").strip().lower()
    if not text:
        return None

    multiplier = 10_000 if text.endswith(("w", "万")) else 1
    if multiplier > 1:
        text = text[:-1].strip()

    try:
        return int(float(text) * multiplier)
    except ValueError:
        return None


class XiaohongshuDomAdapter:
    name = "xiaohongshu-dom"

    def __init__(
        self,
        gateway: SearchGateway,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.gateway = gateway
        self.clock = clock

    def search_notes(self, keyword: str) -> FixturePayload:
        query = keyword.strip()
        if not query:
            raise XiaohongshuCollectionError("请输入非空关键词后再采集。")

        cards = self.gateway.search(query)
        return FixturePayload(
            source=self.name,
            query=query,
            collected_at=self.clock(),
            notes=[self._to_note(card) for card in cards],
        )

    @staticmethod
    def _to_note(card: PublicSearchCard) -> CollectedNote:
        return CollectedNote(
            platform_note_id=card.note_id,
            url=card.url,
            author=CollectedAuthor(
                platform_author_id=card.author_id,
                nickname=card.author_name,
            ),
            title=card.title,
            content=card.content,
            content_type=card.content_type,
            published_at=card.published_at,
            metrics=CollectedMetrics(
                likes=parse_visible_count(card.likes),
                favorites=parse_visible_count(card.favorites),
                comments=parse_visible_count(card.comments),
                shares=parse_visible_count(card.shares),
            ),
        )
