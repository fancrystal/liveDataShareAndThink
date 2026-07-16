from collections.abc import Callable
from hmac import compare_digest
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.collection.xiaohongshu_dom_adapter import (
    PublicSearchCard,
    SearchGateway,
    XiaohongshuCollectionError,
)


class SearchRequest(BaseModel):
    keyword: str = Field(min_length=1)


class PublicSearchCardRead(BaseModel):
    note_id: str
    url: str
    title: str
    content: str
    author_id: str
    author_name: str
    content_type: str
    published_at: str | None
    likes: str | None
    favorites: str | None
    comments: str | None
    shares: str | None

    @classmethod
    def from_card(cls, card: PublicSearchCard) -> "PublicSearchCardRead":
        return cls(
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


def create_proxy_app(gateway: SearchGateway, token: str) -> FastAPI:
    app = FastAPI(title="LiveDataShareAndThink Local Collection Proxy")

    @app.post(
        "/api/collections/xiaohongshu/search",
        response_model=list[PublicSearchCardRead],
    )
    def search(
        request: SearchRequest,
        proxy_token: Annotated[str | None, Header(alias="X-Collection-Proxy-Token")] = None,
    ) -> list[PublicSearchCardRead]:
        if not token or not proxy_token or not compare_digest(proxy_token, token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized collection proxy request")
        keyword = request.keyword.strip()
        if not keyword:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Keyword is required")
        try:
            return [PublicSearchCardRead.from_card(card) for card in gateway.search(keyword)]
        except XiaohongshuCollectionError as error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error

    return app
