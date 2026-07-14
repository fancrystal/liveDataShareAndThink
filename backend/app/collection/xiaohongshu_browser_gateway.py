from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Protocol
from urllib.parse import quote

from app.collection.xiaohongshu_dom_adapter import (
    PublicSearchCard,
    XiaohongshuCollectionError,
)


class Page(Protocol):
    def evaluate(self, script: str) -> list[dict[str, str | None]]: ...


class XiaohongshuBrowserGateway:
    """Read public search cards using the user's existing local xhs-cli session."""

    SEARCH_URL = "https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_explore_feed"
    CARD_SCRIPT = """() => Array.from(document.querySelectorAll('a[href*="/explore/"]'))
      .map((link) => {
        const url = link.href || '';
        const noteId = (url.match(/\\/explore\\/([^?/#]+)/) || [])[1] || '';
        const card = link.closest('section, article, div[class*="note"]') || link.parentElement;
        const text = (card?.innerText || link.innerText || '').split('\\n').map((part) => part.trim()).filter(Boolean);
        const authorLink = card?.querySelector('a[href*="/user/profile/"]');
        const authorUrl = authorLink?.href || '';
        const authorId = (authorUrl.match(/\\/user\\/profile\\/([^?/#]+)/) || [])[1] || '';
        const time = card?.querySelector('time')?.dateTime || card?.querySelector('time')?.getAttribute('datetime') || '';
        return {
          note_id: noteId,
          url,
          title: text[0] || '',
          content: text.slice(1, -1).join(' '),
          author_id: authorId,
          author_name: (authorLink?.innerText || text.at(-1) || '').trim(),
          content_type: card?.querySelector('video') ? 'video' : 'image',
          published_at: time,
          likes: '',
          favorites: '',
          comments: '',
          shares: '',
        };
      })
      .filter((card) => card.note_id && card.url && card.title && card.author_id && card.author_name && card.published_at)
      .slice(0, 20)"""

    def search(self, keyword: str) -> list[PublicSearchCard]:
        try:
            with self._open_signed_in_page() as page:
                page.goto(
                    self.SEARCH_URL.format(keyword=quote(keyword)),
                    wait_until="domcontentloaded",
                    timeout=20_000,
                )
                page.wait_for_selector('a[href*="/explore/"]', timeout=12_000)
                return self.extract_cards(page)
        except XiaohongshuCollectionError:
            raise
        except Exception as error:
            raise XiaohongshuCollectionError(self._safe_message(error)) from error

    @classmethod
    def extract_cards(cls, page: Page) -> list[PublicSearchCard]:
        raw_cards = page.evaluate(cls.CARD_SCRIPT)
        cards: list[PublicSearchCard] = []
        for item in raw_cards[:20]:
            try:
                cards.append(
                    PublicSearchCard(
                        note_id=cls._required(item, "note_id"),
                        url=cls._required(item, "url"),
                        title=cls._required(item, "title"),
                        content=str(item.get("content") or ""),
                        author_id=cls._required(item, "author_id"),
                        author_name=cls._required(item, "author_name"),
                        content_type=str(item.get("content_type") or "image"),
                        published_at=cls._required(item, "published_at"),
                        likes=cls._optional(item, "likes"),
                        favorites=cls._optional(item, "favorites"),
                        comments=cls._optional(item, "comments"),
                        shares=cls._optional(item, "shares"),
                    )
                )
            except ValueError:
                continue
        return cards

    @staticmethod
    def _required(item: dict[str, str | None], key: str) -> str:
        value = str(item.get(key) or "").strip()
        if not value:
            raise ValueError(f"Missing public card field: {key}")
        return value

    @staticmethod
    def _optional(item: dict[str, str | None], key: str) -> str | None:
        value = str(item.get(key) or "").strip()
        return value or None

    @contextmanager
    def _open_signed_in_page(self) -> Iterator[Any]:
        from xhs_cli.auth import cookie_str_to_dict, get_saved_cookie_string
        from xhs_cli.client import XhsClient

        cookie_string = get_saved_cookie_string()
        if not cookie_string:
            raise XiaohongshuCollectionError("请先使用 xhs login 在本机完成小红书登录后再采集。")

        with XhsClient(cookie_str_to_dict(cookie_string)) as client:
            yield client._page

    @staticmethod
    def _safe_message(error: Exception) -> str:
        if isinstance(error, TimeoutError):
            return "小红书搜索页面加载超时，请检查本机网络和登录状态后重试。"
        return "无法读取小红书公开搜索结果。请确认本机已登录，并处理可能的验证提示后重试。"
