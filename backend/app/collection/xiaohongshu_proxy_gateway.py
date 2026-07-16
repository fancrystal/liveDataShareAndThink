from typing import Any

import httpx

from app.collection.proxy_app import PublicSearchCardRead
from app.collection.xiaohongshu_dom_adapter import PublicSearchCard, XiaohongshuCollectionError


class XiaohongshuProxyGateway:
    """Read public cards through the token-protected host-local proxy."""

    def __init__(
        self,
        proxy_url: str,
        token: str | None,
        client: httpx.Client | None = None,
    ) -> None:
        self.proxy_url = proxy_url.rstrip("/")
        self.token = token or ""
        self.client = client or httpx.Client(timeout=25.0)

    def search(self, keyword: str) -> list[PublicSearchCard]:
        try:
            response = self.client.post(
                f"{self.proxy_url}/api/collections/xiaohongshu/search",
                headers={"X-Collection-Proxy-Token": self.token},
                json={"keyword": keyword},
            )
        except httpx.RequestError as error:
            raise XiaohongshuCollectionError(
                "本地采集代理未启动。请在项目目录启动代理后重试。"
            ) from error

        if response.status_code == 401:
            raise XiaohongshuCollectionError("本地采集代理令牌不匹配，请检查 .env 配置。")
        if response.status_code == 422:
            detail = self._safe_detail(response)
            raise XiaohongshuCollectionError(detail or "小红书公开搜索采集失败，请检查本机登录状态。")
        if response.is_error:
            raise XiaohongshuCollectionError("本地采集代理暂时不可用，请稍后重试。")

        try:
            return [self._to_card(item) for item in response.json()]
        except (TypeError, ValueError) as error:
            raise XiaohongshuCollectionError("本地采集代理返回的数据无效，请重启代理后重试。") from error

    @staticmethod
    def _to_card(item: dict[str, Any]) -> PublicSearchCard:
        card = PublicSearchCardRead.model_validate(item)
        return PublicSearchCard(
            note_id=card.note_id,
            url=card.url,
            title=card.title,
            content=card.content,
            author_id=card.author_id,
            author_name=card.author_name,
            content_type=card.content_type,
            published_at=card.published_at,
            likes=card.likes,
            favorites=card.favorites,
            comments=card.comments,
            shares=card.shares,
        )

    @staticmethod
    def _safe_detail(response: httpx.Response) -> str:
        try:
            detail = response.json().get("detail")
        except (TypeError, ValueError):
            return ""
        return detail if isinstance(detail, str) else ""
