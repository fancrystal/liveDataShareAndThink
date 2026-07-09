from typing import Protocol

from app.collection.schemas import FixturePayload


class PlatformAdapter(Protocol):
    @property
    def name(self) -> str: ...

    def search_notes(self, keyword: str) -> FixturePayload: ...

