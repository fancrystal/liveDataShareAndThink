from dataclasses import asdict, dataclass
from math import log1p
from typing import Literal


@dataclass(frozen=True)
class MetricInput:
    likes: int | None
    favorites: int | None
    comments: int | None
    shares: int | None
    followers: int | None
    age_hours: float | None


@dataclass(frozen=True)
class NoteScore:
    total: float
    engagement: float
    velocity: float | None
    cohort_relative: float
    author_efficiency: float | None
    confidence: Literal["low", "medium", "high"]
    explanation: dict[str, int | float | None]

    def to_dict(self) -> dict:
        return asdict(self)


def weighted_engagement(metrics: MetricInput) -> float:
    values = (
        (metrics.likes, 1.0),
        (metrics.favorites, 1.5),
        (metrics.comments, 2.0),
        (metrics.shares, 2.0),
    )
    return sum(value * weight for value, weight in values if value is not None)


def _bounded_ratio(value: float, reference: float) -> float:
    safe_reference = max(reference, 1.0)
    ratio = value / safe_reference
    return round(min(100.0, 100.0 * ratio / (ratio + 0.5)), 2)


def score_note(
    metrics: MetricInput,
    cohort_median_engagement: float,
    cohort_size: int,
) -> NoteScore:
    weighted = weighted_engagement(metrics)
    engagement = _bounded_ratio(log1p(weighted), log1p(cohort_median_engagement))
    velocity = None
    if metrics.age_hours is not None:
        hourly = weighted / max(metrics.age_hours, 1.0)
        velocity = _bounded_ratio(log1p(hourly), log1p(max(cohort_median_engagement / 24, 1)))
    cohort_relative = _bounded_ratio(weighted, cohort_median_engagement)
    author_efficiency = None
    if metrics.followers is not None:
        author_efficiency = _bounded_ratio(weighted, max(metrics.followers * 0.2, 1))

    available = sum(
        value is not None
        for value in (metrics.likes, metrics.favorites, metrics.comments, metrics.shares, metrics.followers)
    )
    if metrics.age_hours is None:
        confidence: Literal["low", "medium", "high"] = "low"
    elif available == 5 and cohort_size >= 3:
        confidence: Literal["low", "medium", "high"] = "high"
    elif available >= 3 and cohort_size >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    components: list[tuple[float, float]] = [(engagement, 0.35), (cohort_relative, 0.25)]
    if velocity is not None:
        components.append((velocity, 0.25))
    if author_efficiency is not None:
        components.append((author_efficiency, 0.15))
    weight_total = sum(weight for _, weight in components)
    total = round(sum(value * weight for value, weight in components) / weight_total, 2)

    return NoteScore(
        total=total,
        engagement=engagement,
        velocity=velocity,
        cohort_relative=cohort_relative,
        author_efficiency=author_efficiency,
        confidence=confidence,
        explanation={
            "weighted_engagement": round(weighted, 2),
            "cohort_median_engagement": round(cohort_median_engagement, 2),
            "age_hours": round(metrics.age_hours, 2) if metrics.age_hours is not None else None,
            "followers": metrics.followers,
            "cohort_size": cohort_size,
        },
    )
