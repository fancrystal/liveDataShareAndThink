from __future__ import annotations

from subprocess import CompletedProcess

import pytest

from app.collection.redbook_adapter import RedbookAdapter, RedbookAdapterError


def test_search_notes_normalizes_redbook_json() -> None:
    payload = {
        "data": {
            "notes": [
                {
                    "id": "note-1",
                    "url": "https://www.xiaohongshu.com/explore/note-1",
                    "title": "敏感肌护肤步骤",
                    "desc": "先做减法，再做选择。",
                    "type": "normal",
                    "time": "2026-07-10T08:00:00Z",
                    "user": {"id": "author-1", "nickname": "小鹿", "fans": 1200},
                    "likes": 100,
                    "collects": 50,
                    "comments": 10,
                    "shares": 2,
                }
            ]
        }
    }

    adapter = RedbookAdapter(runner=lambda _args: CompletedProcess([], 0, __import__("json").dumps(payload), ""))

    result = adapter.search_notes("敏感肌")

    assert result.source == "redbook"
    assert result.query == "敏感肌"
    assert len(result.notes) == 1
    assert result.notes[0].platform_note_id == "note-1"
    assert result.notes[0].author.followers == 1200
    assert result.notes[0].metrics.favorites == 50


def test_search_notes_explains_missing_cli() -> None:
    def missing_command(_args: list[str]) -> CompletedProcess[str]:
        raise FileNotFoundError

    adapter = RedbookAdapter(runner=missing_command)

    with pytest.raises(RedbookAdapterError, match="安装"):
        adapter.search_notes("敏感肌")
