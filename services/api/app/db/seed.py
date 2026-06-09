from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.passwords import hash_password
from app.db.models import (
    AIModel,
    ApiKey,
    Company,
    CompanyValidation,
    ConfidenceScore,
    Country,
    Industry,
    MetricDefinition,
    MetricSource,
    MetricValue,
    ResearchQueueItem,
    Source,
    User,
)
from app.db.session import SessionLocal
from app.domains.autonomous_research.service import (
    run_ai_economy_validation,
    run_approval_agent,
    run_research_agent,
    run_validation_agent,
)
from app.domains.confidence.service import score_metric_confidence, source_reliability_score
from app.domains.identity.api_keys import hash_api_key
from app.domains.microsoft_validation.service import (
    ensure_alphabet_validation_workspace,
    ensure_microsoft_validation_workspace,
    ensure_nvidia_validation_workspace,
    write_workspace_audit_log,
)
from app.domains.research.service import (
    collect_research_evidence,
    ensure_research_queue_item,
    review_research_evidence,
    update_research_status,
    write_research_audit,
)
from app.domains.sources.registry import BETA_COMPANIES, SOURCE_REGISTRY
from app.domains.trust_index.service import ensure_trust_index_snapshots
from app.domains.validation.service import (
    attach_source_evidence,
    ensure_company_validation,
    ensure_source_review,
    recalculate_company_validation,
)

LOCAL_DEV_API_KEY = "apip_live_local_dev_key"


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
    get_or_create(
        db,
        ApiKey,
        "key_hash",
        hash_api_key(LOCAL_DEV_API_KEY),
        name="Local Development API Key",
        key_prefix=LOCAL_DEV_API_KEY[:16],
        plan="enterprise",
        daily_limit=None,
        status="active",
        created_by_user_id=admin.id,
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
        slug: get_or_create(
            db,
            Company,
            "slug",
            slug,
            name=name,
            ticker=ticker,
            headquarters_country_id=countries["US"].id,
            website_url=website_url,
            status="active",
        )
        for slug, name, ticker, website_url in BETA_COMPANIES
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
        ("grok", "Grok", "Grok", companies["xai"].id),
        ("mistral", "Mistral", "Mistral", companies["mistral"].id),
        ("perplexity", "Perplexity Assistant", "Perplexity", companies["perplexity"].id),
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
        "revenue_growth": get_or_create(
            db,
            MetricDefinition,
            "key",
            "revenue_growth",
            name="Revenue Growth",
            description="Year-over-year AI revenue growth score.",
            unit="ratio",
            higher_is_better=1,
            aggregation_method="latest",
        ),
        "adoption": get_or_create(
            db,
            MetricDefinition,
            "key",
            "adoption",
            name="Adoption",
            description="AI adoption score across tracked customers, users, or deployments.",
            unit="score",
            higher_is_better=1,
            aggregation_method="latest",
        ),
        "ai_reality_index": get_or_create(
            db,
            MetricDefinition,
            "key",
            "ai_reality_index",
            name="AI Reality Index",
            description="Composite score from ROI, revenue growth, margin, and adoption.",
            unit="score",
            higher_is_better=1,
            aggregation_method="weighted_average",
        ),
    }

    source_map: dict[str, Source] = {}
    company_source_map: dict[str, list[Source]] = {slug: [] for slug in companies}
    shared_sources: list[Source] = []
    for registry_source in SOURCE_REGISTRY:
        source = upsert_source(
            db,
            title=registry_source.title,
            source_type=registry_source.source_type,
            url=registry_source.url,
            publisher=registry_source.publisher,
            published_at=registry_source.published_at,
        )
        source_map[registry_source.key] = source
        if registry_source.company_slug:
            company_source_map[registry_source.company_slug].append(source)
        else:
            shared_sources.append(source)

    def beta_sources(company_slug: str) -> list[Source]:
        return company_source_map.get(company_slug, []) + shared_sources[:2]

    beta_company_metrics = {
        "microsoft": {
            "ai_revenue": (75_000_000_000, "usd"),
            "ai_spend": (80_000_000_000, "usd"),
            "roi": (0.94, None),
            "revenue_growth": (0.34, None),
            "gross_margin": (0.69, None),
            "adoption": (92, None),
        },
        "google": {
            "ai_revenue": (43_000_000_000, "usd"),
            "ai_spend": (52_500_000_000, "usd"),
            "roi": (0.82, None),
            "revenue_growth": (0.31, None),
            "gross_margin": (0.56, None),
            "adoption": (89, None),
        },
        "meta": {
            "ai_revenue": (28_000_000_000, "usd"),
            "ai_spend": (69_000_000_000, "usd"),
            "roi": (0.41, None),
            "revenue_growth": (0.21, None),
            "gross_margin": (0.82, None),
            "adoption": (86, None),
        },
        "amazon": {
            "ai_revenue": (107_600_000_000, "usd"),
            "ai_spend": (83_000_000_000, "usd"),
            "roi": (1.30, None),
            "revenue_growth": (0.19, None),
            "gross_margin": (0.38, None),
            "adoption": (88, None),
        },
        "nvidia": {
            "ai_revenue": (115_200_000_000, "usd"),
            "ai_spend": (39_300_000_000, "usd"),
            "roi": (2.93, None),
            "revenue_growth": (1.42, None),
            "gross_margin": (0.75, None),
            "adoption": (95, None),
        },
        "openai": {
            "ai_revenue": (12_500_000_000, "usd"),
            "ai_spend": (16_000_000_000, "usd"),
            "roi": (0.78, None),
            "revenue_growth": (0.82, None),
            "gross_margin": (0.48, None),
            "adoption": (76, None),
        },
        "anthropic": {
            "ai_revenue": (5_000_000_000, "usd"),
            "ai_spend": (8_000_000_000, "usd"),
            "roi": (0.62, None),
            "revenue_growth": (0.74, None),
            "gross_margin": (0.44, None),
            "adoption": (68, None),
        },
        "xai": {
            "ai_revenue": (1_800_000_000, "usd"),
            "ai_spend": (6_000_000_000, "usd"),
            "roi": (0.30, None),
            "revenue_growth": (0.66, None),
            "gross_margin": (0.38, None),
            "adoption": (54, None),
        },
        "mistral": {
            "ai_revenue": (900_000_000, "usd"),
            "ai_spend": (1_700_000_000, "usd"),
            "roi": (0.53, None),
            "revenue_growth": (0.58, None),
            "gross_margin": (0.42, None),
            "adoption": (57, None),
        },
        "perplexity": {
            "ai_revenue": (750_000_000, "usd"),
            "ai_spend": (1_200_000_000, "usd"),
            "roi": (0.62, None),
            "revenue_growth": (0.61, None),
            "gross_margin": (0.40, None),
            "adoption": (63, None),
        },
    }
    for company_slug, metrics in beta_company_metrics.items():
        for metric_key, (value, currency) in metrics.items():
            seed_metric(
                db,
                definitions[metric_key],
                "company",
                companies[company_slug].id,
                value,
                currency,
                beta_sources(company_slug),
                beta_methodology(company_slug, metric_key),
            )
        validation = seed_company_validation(
            db, companies[company_slug], beta_sources(company_slug), admin.id
        )
        seed_research_queue_item(
            db,
            companies[company_slug],
            validation,
            beta_sources(company_slug),
            admin.id,
        )

    microsoft_workspace = ensure_microsoft_validation_workspace(db, admin.id)
    nvidia_workspace = ensure_nvidia_validation_workspace(db, admin.id)
    alphabet_workspace = ensure_alphabet_validation_workspace(db, admin.id)
    write_workspace_audit_log(
        db,
        actor_user_id=admin.id,
        action="microsoft_validation.workspace_seeded",
        workspace=microsoft_workspace,
        metadata={
            "company": "Microsoft",
            "report_path": microsoft_workspace.report_path,
            "methodology_version": microsoft_workspace.methodology_version,
        },
    )
    write_workspace_audit_log(
        db,
        actor_user_id=admin.id,
        action="nvidia_validation.workspace_seeded",
        workspace=nvidia_workspace,
        metadata={
            "company": "NVIDIA",
            "report_path": nvidia_workspace.report_path,
            "methodology_version": nvidia_workspace.methodology_version,
        },
    )
    write_workspace_audit_log(
        db,
        actor_user_id=admin.id,
        action="alphabet_validation.workspace_seeded",
        workspace=alphabet_workspace,
        metadata={
            "company": "Alphabet",
            "report_path": alphabet_workspace.report_path,
            "methodology_version": alphabet_workspace.methodology_version,
        },
    )

    us_sources = [
        source_map["stanford-ai-index"],
        source_map["oecd-ai-observatory"],
        source_map["imf-ai-topic"],
        source_map["world-bank-digital"],
    ]
    seed_metric(
        db,
        definitions["ai_revenue"],
        "country",
        countries["US"].id,
        165_000_000_000,
        "usd",
        us_sources,
        "United States beta AI revenue aggregates company-level AI infrastructure "
        "and AI application evidence from institutional source registries.",
    )
    seed_metric(db, definitions["roi"], "country", countries["US"].id, 0.74, None, us_sources)
    seed_metric(
        db,
        definitions["revenue_growth"],
        "country",
        countries["US"].id,
        0.68,
        None,
        us_sources,
    )
    seed_metric(
        db,
        definitions["gross_margin"],
        "country",
        countries["US"].id,
        0.45,
        None,
        us_sources,
    )
    seed_metric(
        db,
        definitions["adoption"],
        "country",
        countries["US"].id,
        61,
        None,
        us_sources,
    )
    healthcare_id = db.scalar(select(Industry.id).where(Industry.slug == "healthcare-ai"))
    seed_metric(
        db,
        definitions["roi"],
        "industry",
        healthcare_id,
        1.18,
        None,
        us_sources,
    )
    seed_metric(
        db,
        definitions["revenue_growth"],
        "industry",
        healthcare_id,
        0.59,
        None,
        us_sources,
    )
    seed_metric(
        db,
        definitions["gross_margin"],
        "industry",
        healthcare_id,
        0.62,
        None,
        us_sources,
    )
    seed_metric(
        db,
        definitions["adoption"],
        "industry",
        healthcare_id,
        67,
        None,
        us_sources,
    )
    seed_metric(
        db,
        definitions["gross_margin"],
        "model",
        db.scalar(select(AIModel.id).where(AIModel.slug == "gpt")),
        0.61,
        None,
        beta_sources("openai"),
    )
    run_research_agent(db)
    run_validation_agent(db)
    run_approval_agent(db)
    run_ai_economy_validation(db, admin.id)
    ensure_trust_index_snapshots(db)

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


def upsert_source(
    db: Session,
    title: str,
    source_type: str,
    url: str,
    publisher: str,
    published_at: datetime,
) -> Source:
    source = db.scalar(select(Source).where(Source.url == url))
    if not source:
        source = Source(
            title=title,
            source_type=source_type,
            url=url,
            publisher=publisher,
            published_at=published_at,
            reliability_score=source_reliability_score(source_type),
            status="approved",
        )
        db.add(source)
        db.flush()
        return source
    source.title = title
    source.source_type = source_type
    source.publisher = publisher
    source.published_at = published_at
    source.reliability_score = source_reliability_score(source_type)
    source.status = "approved"
    return source


def beta_methodology(company_slug: str, metric_key: str) -> str:
    return (
        f"APIP beta {company_slug} {metric_key} is normalized from approved source registry "
        "evidence. Direct AI economics disclosure varies by company, so APIP stores "
        "the source-backed proxy with confidence and evidence coverage rather than "
        "treating it as a final audited AI segment."
    )


def seed_company_validation(
    db: Session,
    company: Company,
    sources: list[Source],
    reviewer_user_id: str,
) -> CompanyValidation:
    validation = ensure_company_validation(db, company)
    validation.status = "in_review"
    validation.reviewed_by_user_id = reviewer_user_id
    validation.reviewer_notes = (
        "Initial OpenVals beta validation created from approved source registry evidence."
    )
    for source in sources:
        evidence = attach_source_evidence(
            db,
            validation,
            source,
            evidence_type=source.source_type,
            review_status="approved",
        )
        evidence.reviewer_notes = "Seeded from beta source registry."
        evidence.reviewed_by_user_id = reviewer_user_id
        evidence.reviewed_at = datetime.now(UTC)
        review = ensure_source_review(db, validation, source, review_status="approved")
        review.reviewer_notes = "Source approved for beta company validation."
        review.reviewed_by_user_id = reviewer_user_id
        review.reviewed_at = datetime.now(UTC)
    recalculate_company_validation(validation)
    return validation


def seed_research_queue_item(
    db: Session,
    company: Company,
    validation: CompanyValidation,
    sources: list[Source],
    actor_user_id: str,
) -> ResearchQueueItem:
    item = ensure_research_queue_item(db, company, validation)
    item.assigned_to_user_id = actor_user_id
    item.reviewer_user_id = actor_user_id
    item.priority = (
        "high" if company.slug in {"microsoft", "google", "meta", "amazon", "nvidia"} else "normal"
    )
    item.notes = "Seeded APIP beta research queue item using approved source registry evidence."
    previous_status = item.status
    update_research_status(item, "under_review", notes=item.notes)
    for source in sources:
        evidence = collect_research_evidence(
            db,
            item,
            source,
            collected_by_user_id=actor_user_id,
            evidence_type=source.source_type,
        )
        review_research_evidence(
            evidence,
            approval_status="approved",
            reviewer_user_id=actor_user_id,
            reviewer_notes="Approved from APIP beta source registry during seed import.",
        )
    write_research_audit(
        db,
        queue_item_id=item.id,
        actor_user_id=actor_user_id,
        action="research_queue.seeded",
        from_status=previous_status,
        to_status=item.status,
        notes=item.notes,
        metadata={"company_id": company.id, "company": company.name},
    )
    return item


def seed_metric(
    db: Session,
    definition: MetricDefinition,
    entity_type: str,
    entity_id: str | None,
    value: float,
    currency: str | None,
    sources: list[Source],
    methodology: str | None = None,
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
            methodology=methodology
            or "APIP beta metric normalized from approved source registry evidence.",
            status="approved",
        )
        db.add(metric)
        db.flush()
    else:
        metric.value_numeric = value
        metric.currency = currency
        metric.methodology = methodology or metric.methodology
        metric.status = "approved"
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
                    evidence_note="Linked during APIP beta source registry ingestion.",
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
