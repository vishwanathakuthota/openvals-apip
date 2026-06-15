from dataclasses import dataclass
from datetime import UTC, datetime

from app.db.models import MetricValue, Source

SOURCE_RELIABILITY_SCORES = {
    "sec_filing": 100,
    "annual_report": 95,
    "earnings_call": 90,
    "investor_presentation": 80,
    "analyst_estimate": 70,
    "industry_report": 65,
    "market_data": 85,
    "investor_relations": 85,
    "news_article": 50,
    "community_estimate": 30,
}


@dataclass(frozen=True)
class ConfidenceResult:
    source_reliability: int
    data_freshness: int
    cross_verification: int
    methodology_transparency: int
    confidence_score: float
    confidence_label: str
    source_count: int
    methodology_note: str


def source_reliability_score(source_type: str) -> int:
    normalized = source_type.strip().lower().replace(" ", "_").replace("-", "_")
    return SOURCE_RELIABILITY_SCORES.get(normalized, 30)


def freshness_score(published_at: datetime | None, now: datetime | None = None) -> int:
    if published_at is None:
        return 40
    now = now or datetime.now(UTC)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=UTC)
    age_days = max((now - published_at).days, 0)
    if age_days < 30:
        return 100
    if age_days < 90:
        return 90
    if age_days < 180:
        return 75
    if age_days < 365:
        return 60
    return 40


def cross_verification_score(source_count: int) -> int:
    if source_count >= 4:
        return 100
    if source_count == 3:
        return 90
    if source_count == 2:
        return 75
    if source_count == 1:
        return 50
    return 0


def methodology_transparency_score(methodology_note: str | None) -> int:
    if not methodology_note:
        return 30
    length = len(methodology_note.strip())
    if length >= 120:
        return 100
    if length >= 80:
        return 85
    if length >= 40:
        return 70
    return 50


def confidence_label(score: float) -> str:
    if score >= 90:
        return "Verified"
    if score >= 75:
        return "High Confidence"
    if score >= 60:
        return "Medium Confidence"
    if score >= 40:
        return "Low Confidence"
    return "Speculative"


def calculate_confidence(
    source_reliability: float,
    data_freshness: float,
    cross_verification: float,
    methodology_transparency: float,
) -> dict[str, float | str]:
    score = (
        source_reliability * 0.40
        + data_freshness * 0.20
        + cross_verification * 0.25
        + methodology_transparency * 0.15
    )
    return {"score": round(score, 2), "label": confidence_label(score)}


def score_metric_confidence(
    metric: MetricValue,
    sources: list[Source],
    now: datetime | None = None,
) -> ConfidenceResult:
    source_count = len(sources)
    source_reliability = average_score(
        [source_reliability_score(source.source_type) for source in sources]
    )
    data_freshness = average_score(
        [freshness_score(source.published_at, now=now) for source in sources]
    )
    cross_verification = cross_verification_score(source_count)
    methodology_transparency = methodology_transparency_score(metric.methodology)
    calculated = calculate_confidence(
        source_reliability=source_reliability,
        data_freshness=data_freshness,
        cross_verification=cross_verification,
        methodology_transparency=methodology_transparency,
    )
    return ConfidenceResult(
        source_reliability=source_reliability,
        data_freshness=data_freshness,
        cross_verification=cross_verification,
        methodology_transparency=methodology_transparency,
        confidence_score=float(calculated["score"]),
        confidence_label=str(calculated["label"]),
        source_count=source_count,
        methodology_note=metric.methodology,
    )


def average_score(scores: list[int]) -> int:
    if not scores:
        return 0
    return round(sum(scores) / len(scores))
