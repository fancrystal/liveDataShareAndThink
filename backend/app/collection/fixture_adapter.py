import json
from pathlib import Path

from app.collection.schemas import FixturePayload


class FixtureAdapter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    @property
    def name(self) -> str:
        return "fixture"

    def search_notes(self, keyword: str) -> FixturePayload:
        payload = FixturePayload.model_validate_json(self.path.read_text(encoding="utf-8"))
        if payload.query != keyword:
            return payload.model_copy(update={"query": keyword})
        return payload

