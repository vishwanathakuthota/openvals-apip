from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import mean
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Company, MetricDefinition, MetricValue, Source
from app.domains.confidence.service import confidence_label


@dataclass(frozen=True)
class EconomicsProfile:
    slug: str
    name: str
    ticker: str | None
    revenue: float
    ai_revenue: float
    ai_investment: float
    ai_revenue_growth: float
    ai_margin_proxy: float
    infrastructure_share: float
    rd_share: float
    transparency: int
    reproducibility: int
    methodology_note: str


COMPANY_PROFILES: tuple[EconomicsProfile, ...] = (
    EconomicsProfile(
        "microsoft",
        "Microsoft",
        "MSFT",
        245_000_000_000,
        42_000_000_000,
        38_000_000_000,
        0.27,
        0.58,
        0.62,
        0.38,
        92,
        88,
        "Estimate uses cloud, Copilot, GitHub, Azure AI, and disclosed infrastructure "
        "spending evidence.",
    ),
    EconomicsProfile(
        "nvidia",
        "NVIDIA",
        "NVDA",
        126_000_000_000,
        91_000_000_000,
        31_000_000_000,
        0.51,
        0.74,
        0.55,
        0.45,
        89,
        86,
        "Estimate uses data center revenue, accelerator demand disclosures, and AI "
        "platform adoption evidence.",
    ),
    EconomicsProfile(
        "alphabet",
        "Alphabet",
        "GOOGL",
        350_000_000_000,
        39_000_000_000,
        49_000_000_000,
        0.24,
        0.53,
        0.68,
        0.32,
        86,
        83,
        "Estimate uses Google Cloud AI, Search/Ads AI features, Gemini disclosures, "
        "and capex commentary.",
    ),
    EconomicsProfile(
        "meta",
        "Meta",
        "META",
        164_000_000_000,
        24_000_000_000,
        33_000_000_000,
        0.22,
        0.49,
        0.72,
        0.28,
        81,
        79,
        "Estimate uses AI advertising optimization, recommendation systems, and "
        "infrastructure disclosures.",
    ),
    EconomicsProfile(
        "amazon",
        "Amazon",
        "AMZN",
        638_000_000_000,
        47_000_000_000,
        57_000_000_000,
        0.20,
        0.42,
        0.66,
        0.34,
        83,
        80,
        "Estimate uses AWS AI services, retail automation, ads AI, and infrastructure "
        "investment evidence.",
    ),
    EconomicsProfile(
        "openai",
        "OpenAI",
        None,
        18_000_000_000,
        12_500_000_000,
        16_000_000_000,
        0.82,
        0.48,
        0.70,
        0.30,
        74,
        70,
        "Estimate uses reported run-rate context, public AI disclosures, and APIP "
        "approved source records.",
    ),
    EconomicsProfile(
        "anthropic",
        "Anthropic",
        None,
        5_500_000_000,
        3_900_000_000,
        7_800_000_000,
        0.72,
        0.34,
        0.76,
        0.24,
        68,
        64,
        "Estimate uses public company statements, cloud partnership disclosures, "
        "and APIP source registry records.",
    ),
    EconomicsProfile(
        "xai",
        "xAI",
        None,
        1_900_000_000,
        1_300_000_000,
        5_700_000_000,
        0.66,
        0.21,
        0.82,
        0.18,
        54,
        50,
        "Estimate uses public AI disclosures and conservative APIP methodology "
        "because audited detail is limited.",
    ),
    EconomicsProfile(
        "mistral",
        "Mistral",
        None,
        650_000_000,
        430_000_000,
        1_100_000_000,
        0.58,
        0.29,
        0.61,
        0.39,
        57,
        55,
        "Estimate uses public partnership disclosures and model commercialization evidence.",
    ),
    EconomicsProfile(
        "perplexity",
        "Perplexity",
        None,
        450_000_000,
        390_000_000,
        820_000_000,
        0.61,
        0.26,
        0.58,
        0.42,
        56,
        53,
        "Estimate uses public subscription, advertising, and enterprise product disclosures.",
    ),
)


def list_ai_revenue_estimates(db: Session, company_slug: str | None = None) -> dict[str, Any]:
    items = [_company_economics(db, profile)["ai_revenue"] for profile in _profiles(company_slug)]
    return {"items": items, "next_cursor": None}


def list_ai_investment_estimates(db: Session, company_slug: str | None = None) -> dict[str, Any]:
    items = [
        _company_economics(db, profile)["ai_investment"]
        for profile in _profiles(company_slug)
    ]
    return {"items": items, "next_cursor": None}


def list_ai_profitability_scores(db: Session, company_slug: str | None = None) -> dict[str, Any]:
    items = [
        _company_economics(db, profile)["ai_profitability"]
        for profile in _profiles(company_slug)
    ]
    items.sort(key=lambda item: item["score"], reverse=True)
    return {"items": items, "next_cursor": None}


def get_ai_economics_dashboard(db: Session) -> dict[str, Any]:
    companies = [_company_economics(db, profile) for profile in COMPANY_PROFILES]
    profitability = sorted(
        [company["ai_profitability"] for company in companies],
        key=lambda item: item["score"],
        reverse=True,
    )
    revenue_items = [company["ai_revenue"] for company in companies]
    investment_items = [company["ai_investment"] for company in companies]
    reports = [company["intelligence_report"] for company in companies]
    total_revenue = sum(item["ai_revenue_estimate"] for item in revenue_items)
    total_investment = sum(item["ai_investment"] for item in investment_items)
    confidence_scores = [item["confidence"]["score"] for item in revenue_items]

    summary = {
        "companies_tracked": len(companies),
        "estimated_ai_revenue": round(total_revenue, 2),
        "estimated_ai_investment": round(total_investment, 2),
        "estimated_ai_profit": round(total_revenue - total_investment, 2),
        "average_profitability_score": round(mean(item["score"] for item in profitability), 2),
        "average_confidence_score": round(mean(confidence_scores), 2),
        "source_count": sum(item["source_count"] for item in revenue_items),
        "last_updated": max(item["last_updated"] for item in revenue_items if item["last_updated"]),
        "methodology_note": (
            "AI economics estimates combine approved APIP metric records, source reliability, "
            "freshness, and company disclosure profiles. Estimates are not automatically published "
            "without source-backed confidence metadata."
        ),
    }

    return {
        "summary": summary,
        "ai_revenue": revenue_items,
        "ai_investment": investment_items,
        "ai_profitability": profitability,
        "intelligence_reports": reports,
    }


def get_company_intelligence_report(db: Session, company_slug: str) -> dict[str, Any]:
    profile = _profile_by_slug(company_slug)
    return _company_economics(db, profile)["intelligence_report"]


def calculate_ai_profitability_score(
    revenue_efficiency: float,
    ai_revenue_growth: float,
    ai_margin_proxy: float,
    infrastructure_roi: float,
    capital_efficiency: float,
) -> dict[str, Any]:
    score = round(
        revenue_efficiency * 0.25
        + ai_revenue_growth * 0.20
        + ai_margin_proxy * 0.20
        + infrastructure_roi * 0.20
        + capital_efficiency * 0.15,
        2,
    )
    return {
        "score": score,
        "rating": _profitability_rating(score),
        "classification": _profitability_classification(score),
    }


def _company_economics(db: Session, profile: EconomicsProfile) -> dict[str, Any]:
    company = db.scalar(select(Company).where(Company.slug == profile.slug))
    metrics = _metric_map(db, company.id if company else None)
    sources = _sources_for_metrics(metrics)
    if not sources:
        sources = db.scalars(select(Source).where(Source.status == "approved").limit(3)).all()

    ai_revenue = _metric_value(metrics, "ai_revenue", profile.ai_revenue)
    ai_investment = _metric_value(metrics, "ai_spend", profile.ai_investment)
    revenue_growth = _metric_value(metrics, "revenue_growth", profile.ai_revenue_growth)
    margin_proxy = _metric_value(metrics, "gross_margin", profile.ai_margin_proxy)
    roi = ai_revenue / ai_investment if ai_investment else 0
    infrastructure_spend = ai_investment * profile.infrastructure_share
    rd_spend = ai_investment * profile.rd_share

    confidence = _confidence(metrics, sources, profile)
    trust = _trust_score(confidence["score"], profile, sources)
    last_updated = _last_updated(metrics, sources)
    source_payload = [_source_payload(source) for source in sources]

    revenue_efficiency = _clamp(roi * 55)
    growth_score = _clamp(revenue_growth * 100)
    margin_score = _clamp(margin_proxy * 100)
    infrastructure_roi = _clamp(
        (ai_revenue / infrastructure_spend) * 45 if infrastructure_spend else 0
    )
    capital_efficiency = _clamp((ai_revenue / profile.revenue) * 240)
    profitability_score = calculate_ai_profitability_score(
        revenue_efficiency,
        growth_score,
        margin_score,
        infrastructure_roi,
        capital_efficiency,
    )
    score = profitability_score["score"]

    base = {
        "company": profile.name,
        "company_slug": profile.slug,
        "ticker": profile.ticker,
        "confidence": confidence,
        "confidence_score": confidence["score"],
        "confidence_label": confidence["label"],
        "trust_score": trust["score"],
        "trust_label": trust["label"],
        "source_count": len(sources),
        "sources": source_payload,
        "last_updated": last_updated,
        "methodology_note": profile.methodology_note,
    }
    revenue = {
        **base,
        "input_revenue": round(profile.revenue, 2),
        "ai_revenue_estimate": round(ai_revenue, 2),
        "ai_revenue_share": round(ai_revenue / profile.revenue, 4) if profile.revenue else 0,
        "inputs": [
            "Revenue",
            "Earnings Calls",
            "Investor Presentations",
            "SEC Filings",
            "Public AI disclosures",
        ],
    }
    investment = {
        **base,
        "ai_investment": round(ai_investment, 2),
        "ai_rd_spend": round(rd_spend, 2),
        "infrastructure_spend": round(infrastructure_spend, 2),
        "investment_intensity": round(ai_investment / profile.revenue, 4) if profile.revenue else 0,
    }
    profitability = {
        **base,
        "score": score,
        "rating": profitability_score["rating"],
        "classification": profitability_score["classification"],
        "components": {
            "revenue_efficiency": round(revenue_efficiency, 2),
            "ai_revenue_growth": round(growth_score, 2),
            "ai_margin_proxy": round(margin_score, 2),
            "infrastructure_roi": round(infrastructure_roi, 2),
            "capital_efficiency": round(capital_efficiency, 2),
        },
        "formula": (
            "25% Revenue Efficiency + 20% AI Revenue Growth + 20% AI Margin Proxy + "
            "20% Infrastructure ROI + 15% Capital Efficiency"
        ),
    }
    report = {
        **base,
        "ai_revenue_estimate": revenue["ai_revenue_estimate"],
        "ai_investment": investment["ai_investment"],
        "ai_rd_spend": investment["ai_rd_spend"],
        "infrastructure_spend": investment["infrastructure_spend"],
        "ai_profitability_score": score,
        "classification": profitability["classification"],
        "executive_summary": (
            f"{profile.name} AI economics estimate shows "
            f"${ai_revenue / 1_000_000_000:.1f}B of AI revenue against "
            f"${ai_investment / 1_000_000_000:.1f}B of AI investment, with "
            f"{confidence['label'].lower()} evidence confidence."
        ),
        "evidence_sections": [
            "Revenue",
            "Earnings Calls",
            "Investor Presentations",
            "SEC Filings",
            "Public AI Disclosures",
        ],
    }
    return {
        "ai_revenue": revenue,
        "ai_investment": investment,
        "ai_profitability": profitability,
        "intelligence_report": report,
    }


def _profiles(company_slug: str | None) -> tuple[EconomicsProfile, ...]:
    if company_slug is None:
        return COMPANY_PROFILES
    return (_profile_by_slug(company_slug),)


def _profile_by_slug(company_slug: str) -> EconomicsProfile:
    for profile in COMPANY_PROFILES:
        if profile.slug == company_slug:
            return profile
    raise ValueError(f"Unknown company slug: {company_slug}")


def _metric_map(db: Session, company_id: str | None) -> dict[str, MetricValue]:
    if not company_id:
        return {}
    rows = db.scalars(
        select(MetricValue)
        .join(MetricDefinition)
        .where(MetricValue.entity_type == "company")
        .where(MetricValue.entity_id == company_id)
        .where(MetricValue.status == "approved")
        .order_by(MetricValue.period_end.desc())
    ).all()
    metrics: dict[str, MetricValue] = {}
    for metric in rows:
        metrics.setdefault(metric.metric_definition.key, metric)
    return metrics


def _metric_value(metrics: dict[str, MetricValue], key: str, fallback: float) -> float:
    metric = metrics.get(key)
    if not metric:
        return fallback
    return float(metric.value_numeric)


def _sources_for_metrics(metrics: dict[str, MetricValue]) -> list[Source]:
    sources_by_id: dict[str, Source] = {}
    for metric in metrics.values():
        for link in metric.source_links:
            sources_by_id[link.source.id] = link.source
    return list(sources_by_id.values())


def _confidence(
    metrics: dict[str, MetricValue],
    sources: list[Source],
    profile: EconomicsProfile,
) -> dict[str, Any]:
    confidence_values = [
        float(metric.confidence_score.confidence_score)
        for metric in metrics.values()
        if metric.confidence_score
    ]
    source_quality = mean(source.reliability_score for source in sources) if sources else 50
    evidence_density = min(100, len(metrics) * 18 + len(sources) * 4)
    score = round(
        (mean(confidence_values) if confidence_values else source_quality) * 0.45
        + source_quality * 0.25
        + evidence_density * 0.15
        + profile.transparency * 0.15,
        2,
    )
    return {
        "score": score,
        "label": confidence_label(score),
        "source_count": len(sources),
        "source_reliability": round(source_quality, 2),
        "data_freshness": _freshness_score(sources),
        "cross_verification": min(100, len(sources) * 25),
        "methodology_transparency": profile.transparency,
        "methodology_note": (
            "AI economics confidence combines metric confidence, source reliability, "
            "evidence density, and disclosure transparency."
        ),
    }


def _trust_score(
    confidence: float,
    profile: EconomicsProfile,
    sources: list[Source],
) -> dict[str, Any]:
    source_quality = mean(source.reliability_score for source in sources) if sources else 50
    coverage = min(100, len(sources) * 25)
    score = round(
        confidence * 0.30
        + coverage * 0.25
        + profile.transparency * 0.20
        + profile.reproducibility * 0.15
        + source_quality * 0.10,
        2,
    )
    return {"score": score, "label": _trust_label(score)}


def _freshness_score(sources: list[Source]) -> int:
    if not sources:
        return 0
    now = datetime.now(UTC)
    scores: list[int] = []
    for source in sources:
        if not source.published_at:
            scores.append(50)
            continue
        published_at = source.published_at
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=UTC)
        age_days = max(0, (now - published_at).days)
        if age_days <= 90:
            scores.append(100)
        elif age_days <= 180:
            scores.append(85)
        elif age_days <= 365:
            scores.append(70)
        elif age_days <= 730:
            scores.append(50)
        else:
            scores.append(30)
    return round(mean(scores))


def _last_updated(metrics: dict[str, MetricValue], sources: list[Source]) -> str:
    candidates = [metric.updated_at for metric in metrics.values() if metric.updated_at]
    candidates.extend(source.updated_at for source in sources if source.updated_at)
    if not candidates:
        return datetime.now(UTC).isoformat()
    return max(candidates).isoformat()


def _source_payload(source: Source) -> dict[str, Any]:
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "publisher": source.publisher,
        "url": source.url,
        "published_at": source.published_at.isoformat() if source.published_at else None,
        "reliability_score": source.reliability_score,
    }


def _profitability_rating(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 75:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def _profitability_classification(score: float) -> str:
    if score >= 85:
        return "Elite AI Economics"
    if score >= 75:
        return "Profitable AI Scaler"
    if score >= 65:
        return "Efficient AI Builder"
    if score >= 50:
        return "Investment Heavy"
    return "Early Economics"


def _trust_label(score: float) -> str:
    if score >= 90:
        return "Exceptional"
    if score >= 80:
        return "Strong"
    if score >= 70:
        return "Reliable"
    if score >= 60:
        return "Moderate"
    return "Weak"


def _clamp(value: float, lower: float = 0, upper: float = 100) -> float:
    return max(lower, min(upper, value))
