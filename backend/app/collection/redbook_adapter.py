from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from subprocess import CompletedProcess
from typing import Any

from app.collection.schemas import CollectedAuthor, CollectedMetrics, CollectedNote, FixturePayload

CommandRunner = Callable[[list[str]], CompletedProcess[str]]


class RedbookAdapterError(Exception):
    """Safe error returned when the local redbook CLI cannot provide data."""


class RedbookAdapter:
    def __init__(self, runner: CommandRunner | None = None) -> None:
        self.runner = runner or self._run_command

    @property
    def name(self) -> str:
        return "redbook"

    def search_notes(self, keyword: str) -> FixturePayload:
        query = keyword.strip()
        if not query:
            raise RedbookAdapterError("请输入非空关键词后再采集。")

        try:
            result = self.runner(["redbook", "search", query, "--sort", "popular", "--json"])
        except FileNotFoundError as error:
            raise RedbookAdapterError("未安装 redbook，请先安装 @lucasygu/redbook。") from error
        except subprocess.TimeoutExpired as error:
            raise RedbookAdapterError("redbook 查询超时，请检查本机网络和登录状态后重试。") from error

        if result.returncode != 0:
            raise RedbookAdapterError("redbook 无法完成查询。请确认 Chrome 已登录小红书，并处理可能的验证码或风控提示。")

        try:
            decoded = json.loads(result.stdout)
            notes = [self._normalize_note(item) for item in self._find_note_items(decoded)]
        except (json.JSONDecodeError, TypeError, ValueError, KeyError) as error:
            raise RedbookAdapterError("redbook 返回的数据格式不兼容，请升级 redbook 后重试。") from error

        return FixturePayload(source=self.name, query=query, collected_at=datetime.now(UTC), notes=notes)

    @staticmethod
    def _run_command(args: list[str]) -> CompletedProcess[str]:
        return subprocess.run(args, capture_output=True, check=False, text=True, timeout=30)

    @staticmethod
    def _find_note_items(decoded: Any) -> list[Mapping[str, Any]]:
        payload = decoded.get("data", decoded) if isinstance(decoded, Mapping) else decoded
        if not isinstance(payload, Mapping):
            raise ValueError("The CLI response must be an object")

        items = payload.get("notes") or payload.get("items")
        if not isinstance(items, list):
            raise ValueError("The CLI response has no notes list")
        if not all(isinstance(item, Mapping) for item in items):
            raise ValueError("The notes list contains an invalid item")
        return items

    @classmethod
    def _normalize_note(cls, item: Mapping[str, Any]) -> CollectedNote:
        author_data = item.get("user") or item.get("author") or {}
        if not isinstance(author_data, Mapping):
            raise ValueError("The author is invalid")

        note_id = cls._required_text(item, "id", "note_id", "noteId")
        author_id = cls._required_text(author_data, "id", "user_id", "userId")
        title = cls._required_text(item, "title", "display_title")
        published_at = cls._required_text(item, "published_at", "publish_time", "create_time", "time")
        url = cls._first_text(item, "url", "note_url") or f"https://www.xiaohongshu.com/explore/{note_id}"

        return CollectedNote(
            platform_note_id=note_id,
            url=url,
            author=CollectedAuthor(
                platform_author_id=author_id,
                nickname=cls._first_text(author_data, "nickname", "name") or "小红书用户",
                followers=cls._first_count(author_data, "followers", "fans", "follower_count"),
            ),
            title=title,
            content=cls._first_text(item, "content", "desc", "description") or "",
            content_type=cls._first_text(item, "content_type", "type", "note_type") or "unknown",
            published_at=published_at,
            metrics=CollectedMetrics(
                likes=cls._first_count(item, "likes", "like_count", "liked_count"),
                favorites=cls._first_count(item, "favorites", "collects", "collect_count", "collected_count"),
                comments=cls._first_count(item, "comments", "comment_count"),
                shares=cls._first_count(item, "shares", "share_count"),
            ),
        )

    @staticmethod
    def _required_text(data: Mapping[str, Any], *names: str) -> str:
        value = RedbookAdapter._first_text(data, *names)
        if value is None:
            raise ValueError(f"Missing required field: {names[0]}")
        return value

    @staticmethod
    def _first_text(data: Mapping[str, Any], *names: str) -> str | None:
        for name in names:
            value = data.get(name)
            if value is not None and str(value).strip():
                return str(value).strip()
        return None

    @staticmethod
    def _first_count(data: Mapping[str, Any], *names: str) -> int | None:
        for name in names:
            value = data.get(name)
            if value is not None:
                return RedbookAdapter._to_count(value)
        return None

    @staticmethod
    def _to_count(value: Any) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if not isinstance(value, str):
            return None

        text = value.replace(",", "").strip().lower()
        multiplier = 10_000 if text.endswith("w") or text.endswith("万") else 1
        if multiplier > 1:
            text = text[:-1]
        try:
            return int(float(text) * multiplier)
        except ValueError:
            return None
