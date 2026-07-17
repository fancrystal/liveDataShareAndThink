from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class ContentSample:
    note_id: str
    title: str
    content: str
    content_type: str


@dataclass(frozen=True)
class ContentAttractionPatterns:
    hook_patterns: dict[str, int]
    format_counts: dict[str, int]
    reusable_angles: tuple[str, ...]
    note_ids: tuple[str, ...]


def derive_content_attraction_patterns(samples: list[ContentSample]) -> ContentAttractionPatterns:
    hooks = Counter(_hook_type(sample.title) for sample in samples)
    formats = Counter(sample.content_type for sample in samples)
    angles = tuple(_angle(sample) for sample in samples[:3])
    while len(angles) < 3:
        angles += ("基于更多公开样本补充选题方向",)
    return ContentAttractionPatterns(
        hook_patterns=dict(hooks),
        format_counts=dict(formats),
        reusable_angles=angles,
        note_ids=tuple(sample.note_id for sample in samples),
    )


def _hook_type(title: str) -> str:
    normalized = title.strip()
    if "?" in normalized or "？" in normalized or normalized.startswith(("为什么", "如何", "怎么")):
        return "question"
    if any(marker in normalized for marker in ("先", "别", "不要", "停止")):
        return "directive"
    return "statement"


def _angle(sample: ContentSample) -> str:
    title = sample.title.strip()[:24]
    return f"围绕“{title}”延展同类可执行内容"
