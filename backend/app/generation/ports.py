from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class GenerationBrief:
    topic: str
    audience: str
    goal: Literal["live_preview", "live_booking", "post_live_followup"]
    angle: str
    brand_tone: str
    forbidden_terms: tuple[str, ...]
    evidence_summaries: tuple[str, ...]


@dataclass(frozen=True)
class GeneratedContent:
    variant: Literal["practical", "story", "contrarian"]
    title: str
    body: str
    tags: tuple[str, ...]
    cover_text: str


class ContentGenerator(Protocol):
    @property
    def name(self) -> str: ...

    def generate(self, brief: GenerationBrief) -> list[GeneratedContent]: ...

