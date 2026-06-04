from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.passwords import hash_password
from app.db.models import (
    AIModel,
    Company,
    ConfidenceScore,
    Country,
    Industry,
    MetricDefinition,
    MetricSource,
    MetricValue,
    Source,
    User,
)
from app.db.session import SessionLocal
from app.domains.confidence.service import score_metric_confidence, source_reliability_score


def seed_database(db: Session) -> None:
    admin = get_or_create(
        db,
        User,
        "email",
        "admin@openvalidations.com",
        full_name="APIP Admin",
        role="admin",
        status="active",
        password_hash=hash_password("apip-admin-change-me"),
    )

    countries = {
        "US": get_or_create(
            db,
            Country,
            "iso_code",
            "US",
            name="United States",
            slug="united-states",
            region="North America",
        ),
        "CN": get_or_create(
            db, Country, "iso_code", "CN", name="China", slug="china", region="Asia"
        ),
        "IN": get_or_create(
            db, Country, "iso_code", "IN", name="India", slug="india", region="Asia"
        ),
        "GB": get_or_create(
            db,
            Country,
            "iso_code",
            "GB",
            name="United Kingdom",
            slug="united-kingdom",
            region="Europe",
        ),
        "CA": get_or_create(
            db, Country, "iso_code", "CA", name="Canada", slug="canada", region="North America"
        ),
        "DE": get_or_create(
            db, Country, "iso_code", "DE", name="Germany", slug="germany", region="Europe"
        ),
        "FR": get_or_create(
            db, Country, "iso_code", "FR", name="France", slug="france", region="Europe"
        ),
        "JP": get_or_create(
            db, Country, "iso_code", "JP", name="Japan", slug="japan", region="Asia"
        ),
        "SG": get_or_create(
            db, Country, "iso_code", "SG", name="Singapore", slug="singapore", region="Asia"
        ),
        "KR": get_or_create(
            db, Country, "iso_code", "KR", name="South Korea", slug="south-korea", region="Asia"
        ),
    }

    companies = {
        "openai": get_or_create(
            db,
            Company,
            "slug",
            "openai",
            name="OpenAI",
            ticker=None,
            headquarters_country_id=countries["US"].id,
            website_url="https://openai.com",
            status="active",
        ),
        "anthropic": get_or_create(
            db,
            Company,
            "slug",
            "anthropic",
            name="Anthropic",
            ticker=None,
            headquarters_country_id=countries["US"].id,
            website_url="https://anthropic.com",
            status="active",
        ),
        "google": get_or_create(
            db,
            Company,
            "slug",
            "google",
            name="Google",
            ticker="GOOGL",
            headquarters_country_id=countries["US"].id,
            website_url="https://google.com",
            status="active",
        ),
        "microsoft": get_or_create(
            db,
            Company,
            "slug",
            "microsoft",
            name="Microsoft",
            ticker="MSFT",
            headquarters_country_id=countries["US"].id,
            website_url="https://microsoft.com",
            status="active",
        ),
        "meta": get_or_create(
            db,
            Company,
            "slug",
            "meta",
            name="Meta",
            ticker="META",
            headquarters_country_id=countries["US"].id,
            website_url="https://meta.com",
            status="active",
        ),
        "amazon": get_or_create(
            db,
            Company,
            "slug",
            "amazon",
            name="Amazon",
            ticker="AMZN",
            headquarters_country_id=countries["US"].id,
            website_url="https://amazon.com",
            status="active",
        ),
        "nvidia": get_or_create(
            db,
            Company,
            "slug",
            "nvidia",
            name="NVIDIA",
            ticker="NVDA",
            headquarters_country_id=countries["US"].id,
            website_url="https://nvidia.com",
            status="active",
        ),
    }

    industries = [
        "Healthcare AI",
        "Education AI",
        "Manufacturing AI",
        "Retail AI",
        "Cybersecurity AI",
        "Finance AI",
        "Legal AI",
        "Marketing AI",
        "Government AI",
        "Media AI",
    ]
    for industry in industries:
        get_or_create(db, Industry, "slug", slugify(industry), name=industry, status="active")

    models = [
        ("gpt", "GPT", "GPT", companies["openai"].id),
        ("claude", "Claude", "Claude", companies["anthropic"].id),
        ("gemini", "Gemini", "Gemini", companies["google"].id),
        ("llama", "Llama", "Llama", companies["meta"].id),
    ]
    for slug, name, family, provider_id in models:
        get_or_create(
            db,
            AIModel,
            "slug",
            slug,
            name=name,
            model_family=family,
            provider_company_id=provider_id,
            status="active",
        )

    definitions = {
        "ai_spend": get_or_create(
            db,
            MetricDefinition,
            "key",
            "ai_spend",
            name="AI Spend",
            description="Estimated AI investment spending.",
            unit="usd",
            higher_is_better=0,
            aggregation_method="sum",
        ),
        "ai_revenue": get_or_create(
            db,
            MetricDefinition,
            "key",
            "ai_revenue",
            name="AI Revenue",
            description="Estimated AI-generated revenue.",
            unit="usd",
            higher_is_better=1,
            aggregation_method="sum",
        ),
        "roi": get_or_create(
            db,
            MetricDefinition,
            "key",
            "roi",
            name="ROI",
            description="Revenue divided by spend.",
            unit="ratio",
            higher_is_better=1,
            aggregation_method="weighted_average",
        ),
        "gross_margin": get_or_create(
            db,
            MetricDefinition,
            "key",
            "gross_margin",
            name="Gross Margin",
            description="Estimated model gross margin.",
            unit="ratio",
            higher_is_better=1,
            aggregation_method="latest",
        ),
    }

    sources = [
        get_or_create(
            db,
            Source,
            "title",
            "Synthetic APIP Annual Report Baseline",
            source_type="annual_report",
            url="https://example.com/apip-annual-report",
            publisher="OpenVals",
            published_at=datetime(2026, 5, 20, tzinfo=UTC),
            reliability_score=source_reliability_score("annual_report"),
            status="approved",
        ),
        get_or_create(
            db,
            Source,
            "title",
            "Synthetic APIP Investor Presentation",
            source_type="investor_presentation",
            url="https://example.com/apip-investor-presentation",
            publisher="OpenVals",
            published_at=datetime(2026, 4, 15, tzinfo=UTC),
            reliability_score=source_reliability_score("investor_presentation"),
            status="approved",
        ),
        get_or_create(
            db,
            Source,
            "title",
            "Synthetic APIP Industry Report",
            source_type="industry_report",
            url="https://example.com/apip-industry-report",
            publisher="OpenVals",
            published_at=datetime(2026, 2, 15, tzinfo=UTC),
            reliability_score=source_reliability_score("industry_report"),
            status="approved",
        ),
    ]

    seed_metric(
        db,
        definitions["ai_revenue"],
        "company",
        companies["openai"].id,
        12_500_000_000,
        "usd",
        sources,
    )
    seed_metric(
        db,
        definitions["ai_spend"],
        "company",
        companies["openai"].id,
        16_000_000_000,
        "usd",
        sources,
    )
    seed_metric(
        db,
        definitions["ai_revenue"],
        "country",
        countries["US"].id,
        165_000_000_000,
        "usd",
        sources,
    )
    seed_metric(
        db,
        definitions["roi"],
        "industry",
        db.scalar(select(Industry.id).where(Industry.slug == "healthcare-ai")),
        1.18,
        None,
        sources,
    )
    seed_metric(
        db,
        definitions["gross_margin"],
        "model",
        db.scalar(select(AIModel.id).where(AIModel.slug == "gpt")),
        0.61,
        None,
        sources,
    )

    db.add(admin)
    db.commit()


def get_or_create(db: Session, model: type, key: str, value: object, **kwargs):
    instance = db.scalar(select(model).where(getattr(model, key) == value))
    if instance:
        return instance
    instance = model(**{key: value}, **kwargs)
    db.add(instance)
    db.flush()
    return instance


def seed_metric(
    db: Session,
    definition: MetricDefinition,
    entity_type: str,
    entity_id: str | None,
    value: float,
    currency: str | None,
    sources: list[Source],
) -> None:
    metric = db.scalar(
        select(MetricValue).where(
            MetricValue.metric_definition_id == definition.id,
            MetricValue.entity_type == entity_type,
            MetricValue.entity_id == entity_id,
            MetricValue.period_start == date(2026, 1, 1),
            MetricValue.period_end == date(2026, 12, 31),
        )
    )
    if not metric:
        metric = MetricValue(
            metric_definition_id=definition.id,
            entity_type=entity_type,
            entity_id=entity_id,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 12, 31),
            value_numeric=value,
            currency=currency,
            methodology=(
                "Synthetic APIP baseline calculated from approved source records, "
                "normalized to 2026 reporting periods, and cross-checked across annual report, "
                "investor presentation, and industry report evidence."
            ),
            status="approved",
        )
        db.add(metric)
        db.flush()
    for source in sources:
        existing_link = db.scalar(
            select(MetricSource).where(
                MetricSource.metric_value_id == metric.id,
                MetricSource.source_id == source.id,
            )
        )
        if not existing_link:
            db.add(
                MetricSource(
                    metric_value_id=metric.id,
                    source_id=source.id,
                    evidence_note="Linked during APIP seed confidence calculation.",
                )
            )
    if not metric.confidence_score:
        confidence = score_metric_confidence(metric, sources)
        db.add(
            ConfidenceScore(
                metric_value_id=metric.id,
                source_reliability=confidence.source_reliability,
                data_freshness=confidence.data_freshness,
                cross_verification=confidence.cross_verification,
                methodology_transparency=confidence.methodology_transparency,
                confidence_score=confidence.confidence_score,
                confidence_label=confidence.confidence_label,
                source_count=confidence.source_count,
                methodology_note=confidence.methodology_note,
            )
        )


def slugify(value: str) -> str:
    return value.lower().replace(" ", "-")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_database(session)
