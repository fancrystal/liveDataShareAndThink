from datetime import UTC, datetime

import pytest

from app.collection.xiaohongshu_dom_adapter import (
    PublicSearchCard,
    XiaohongshuCollectionError,
    XiaohongshuDomAdapter,
    parse_visible_count,
)


class FakeGateway:
    def search(self, keyword: str) -> list[PublicSearchCard]:
        assert keyword == "sensitive skin"
        return [
            PublicSearchCard(
                note_id="note-1",
                url="https://www.xiaohongshu.com/explore/note-1",
                title="Sensitive skin routine",
                content="Start with fewer products.",
                author_id="author-1",
                author_name="Creator",
                content_type="image",
                published_at="2026-07-10T08:00:00Z",
                likes="1.2w",
                favorites="300",
                comments="8",
            )
        ]


def test_search_notes_normalizes_visible_public_card() -> None:
    adapter = XiaohongshuDomAdapter(
        FakeGateway(),
        clock=lambda: datetime(2026, 7, 13, tzinfo=UTC),
    )

    result = adapter.search_notes(" sensitive skin ")

    assert result.source == "xiaohongshu-dom"
    assert result.query == "sensitive skin"
    assert result.collected_at == datetime(2026, 7, 13, tzinfo=UTC)
    assert result.notes[0].platform_note_id == "note-1"
    assert result.notes[0].metrics.likes == 12_000
    assert result.notes[0].metrics.favorites == 300
    assert result.notes[0].metrics.shares is None


def test_search_notes_rejects_blank_keyword() -> None:
    adapter = XiaohongshuDomAdapter(FakeGateway())

    with pytest.raises(XiaohongshuCollectionError, match="非空关键词"):
        adapter.search_notes("   ")


def test_parse_visible_count_returns_none_for_unknown_text() -> None:
    assert parse_visible_count("high engagement") is None
