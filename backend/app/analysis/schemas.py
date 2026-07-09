from pydantic import BaseModel


class ScoreRead(BaseModel):
    total: float
    engagement: float
    velocity: float
    cohort_relative: float
    author_efficiency: float | None
    confidence: str
    explanation: dict


class RankingRead(BaseModel):
    note_id: str
    title: str
    url: str
    score: ScoreRead


class EvidenceRead(BaseModel):
    id: str
    note_id: str
    metric_snapshot_id: str
    summary: str
    contribution: float


class InsightRead(BaseModel):
    id: str
    title: str
    summary: str
    confidence: str
    analysis_version: str
    evidence: list[EvidenceRead]


class RankingReport(BaseModel):
    rankings: list[RankingRead]
    insight: InsightRead

