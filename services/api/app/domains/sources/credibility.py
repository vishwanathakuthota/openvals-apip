from dataclasses import dataclass
from datetime import datetime

from app.db.models import Source
from app.domains.confidence.service import freshness_score, source_reliability_score

SOURCE_TYPE_TIERS = {
    "sec_filing": 1,
    "annual_report": 1,
    "earnings_call": 1,
    "investor_presentation": 2,
    "public_company_statement": 2,
    "industry_report": 3,
    "institutional_dataset": 3,
    "news_article": 4,
    "community_estimate": 4,
}

TIER_COVERAGE_WEIGHTS = {
    1: 45,
    2: 25,
    3: 20,
    4: 10,
}

TIER_LABELS = {
    1: "Tier 1",
    2: "Tier 2",
    3: "Tier 3",
    4: "Tier 4",
}


@dataclass(frozen=True)
class EvidenceCoverage:
    score: int
    label: str
    source_count: int
    tier_counts: dict[str, int]
    methodology_note: str


def source_tier(source_type: str) -> int:
    normalized = normalize_source_type(source_type)
    return SOURCE_TYPE_TIERS.get(normalized, 4)


def source_credibility_score(source_type: str, published_at: datetime | None = None) -> int:
    reliability = source_reliability_score(source_type)
    freshness = freshness_score(published_at)
    tier = source_tier(source_type)
    tier_bonus = {1: 10, 2: 5, 3: 0, 4: -10}[tier]
    return max(0, min(100, round((reliability * 0.75) + (freshness * 0.25) + tier_bonus)))


def evidence_coverage_score(sources: list[Source]) -> EvidenceCoverage:
    tier_counts: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
    for source in sources:
        tier_counts[source_tier(source.source_type)] += 1

    score = 0
    for tier, count in tier_counts.items():
        if count:
            score += TIER_COVERAGE_WEIGHTS[tier]
            score += min(count - 1, 2) * 5
    score = min(score, 100)

    label = coverage_label(score)
    readable_counts = {TIER_LABELS[tier]: count for tier, count in tier_counts.items() if count}
    methodology_note = (
        "Coverage score weights evidence tiers: Tier 1 filings and reports, Tier 2 company "
        "statements, Tier 3 institutional datasets, and Tier 4 trusted financial journalism."
    )
    return EvidenceCoverage(
        score=score,
        label=label,
        source_count=len(sources),
        tier_counts=readable_counts,
        methodology_note=methodology_note,
    )


def coverage_label(score: int) -> str:
    if score >= 90:
        return "Full Coverage"
    if score >= 70:
        return "Strong Coverage"
    if score >= 50:
        return "Partial Coverage"
    if score >= 30:
        return "Thin Coverage"
    return "Unverified Coverage"


def normalize_source_type(source_type: str) -> str:
    return source_type.strip().lower().replace(" ", "_").replace("-", "_")
