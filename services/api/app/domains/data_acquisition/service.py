import json
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AuditLog,
    Company,
    ConfidenceScore,
    DataAcquisitionRun,
    MetricDefinition,
    MetricSource,
    MetricValue,
    Source,
    SourceMetric,
    User,
)
from app.domains.confidence.service import (
    freshness_score,
    score_metric_confidence,
    source_reliability_score,
)
from app.domains.data_acquisition.connectors import (
    AcquiredMetric,
    ConnectorResult,
    InvestorRelationsConnector,
    SecEdgarConnector,
    YahooFinanceConnector,
)
from app.domains.data_acquisition.registry import (
    ACQUISITION_TARGETS,
    METRIC_REGISTRY,
    SOURCE_REGISTRY,
)

REFRESH_INTERVAL_SECONDS = 30 * 60


def refresh_realtime_company_metrics(db: Session) -> dict[str, object]:
    connectors = [YahooFinanceConnector(), SecEdgarConnector(), InvestorRelationsConnector()]
    return run_acquisition(db, connectors=connectors)


def run_acquisition(db: Session, connectors: list[object]) -> dict[str, object]:
    ensure_realtime_metric_definitions(db)
    companies_by_slug = ensure_target_companies(db)
    totals = {"targets": len(ACQUISITION_TARGETS), "runs": 0, "metrics": 0, "failed_runs": 0}
    for target in ACQUISITION_TARGETS:
        company = companies_by_slug[target.slug]
        for connector in connectors:
            totals["runs"] += 1
            run = start_run(db, company, connector_name(connector), source_name(connector))
            try:
                result = connector.collect(target)
                metrics_saved = persist_connector_result(db, company, result)
                complete_run(db, run, result, metrics_saved)
                totals["metrics"] += metrics_saved
            except Exception as exc:  # pragma: no cover - defensive scheduler boundary
                fail_run(db, run, str(exc))
                totals["failed_runs"] += 1
    write_audit_log(
        db,
        action="data_acquisition.refresh_completed",
        metadata={**totals, "refresh_interval_seconds": REFRESH_INTERVAL_SECONDS},
    )
    db.commit()
    return {**totals, "status": "completed"}


def persist_connector_result(db: Session, company: Company, result: ConnectorResult) -> int:
    if not result.metrics:
        source = upsert_source(
            db,
            source_name=f"{result.source_name} for {company.name}",
            source_type="investor_relations",
            source_url=result.source_url,
            publisher=result.source_name,
            published_at=None,
            retrieved_at=result.retrieved_at,
        )
        source.status = "approved"
        return 0
    saved = 0
    for metric in result.metrics:
        persist_metric(db, company, metric)
        saved += 1
    return saved


def persist_metric(db: Session, company: Company, metric: AcquiredMetric) -> MetricValue:
    source = upsert_source(
        db,
        source_name=metric.source_name,
        source_type=metric.source_type,
        source_url=metric.source_url,
        publisher=metric.publisher,
        published_at=metric.published_at,
        retrieved_at=metric.retrieved_at,
    )
    definition = ensure_metric_definition(db, metric.metric_key)
    metric_value = upsert_metric_value(db, company, definition, metric)
    link_source(db, metric_value, source, metric)
    confidence = score_metric_confidence(metric_value, [source], now=metric.retrieved_at)
    upsert_confidence(db, metric_value, confidence)
    upsert_source_metric(db, company, source, metric, confidence.confidence_score)
    return metric_value


def upsert_source(
    db: Session,
    source_name: str,
    source_type: str,
    source_url: str,
    publisher: str,
    published_at: datetime | None,
    retrieved_at: datetime,
) -> Source:
    source = db.scalar(select(Source).where(Source.url == source_url, Source.title == source_name))
    freshness = freshness_score(published_at or retrieved_at, now=retrieved_at)
    if not source:
        source = Source(
            title=source_name,
            source_type=source_type,
            url=source_url,
            publisher=publisher,
            published_at=published_at,
            retrieved_at=retrieved_at,
            freshness_score=freshness,
            reliability_score=source_reliability_score(source_type),
            status="approved",
        )
        db.add(source)
        db.flush()
        return source
    source.publisher = publisher
    source.published_at = published_at
    source.retrieved_at = retrieved_at
    source.freshness_score = freshness
    source.reliability_score = source_reliability_score(source_type)
    source.status = "approved"
    return source


def upsert_metric_value(
    db: Session,
    company: Company,
    definition: MetricDefinition,
    metric: AcquiredMetric,
) -> MetricValue:
    metric_value = db.scalar(
        select(MetricValue).where(
            MetricValue.metric_definition_id == definition.id,
            MetricValue.entity_type == "company",
            MetricValue.entity_id == company.id,
            MetricValue.period_start == metric.period_start,
            MetricValue.period_end == metric.period_end,
        )
    )
    if not metric_value:
        metric_value = MetricValue(
            metric_definition_id=definition.id,
            entity_type="company",
            entity_id=company.id,
            period_start=metric.period_start,
            period_end=metric.period_end,
            value_numeric=metric.value,
            currency=metric.currency,
            methodology=metric.methodology_note,
            status="approved",
        )
        db.add(metric_value)
        db.flush()
        return metric_value
    metric_value.value_numeric = metric.value
    metric_value.currency = metric.currency
    metric_value.methodology = metric.methodology_note
    metric_value.status = "approved"
    return metric_value


def link_source(
    db: Session,
    metric_value: MetricValue,
    source: Source,
    metric: AcquiredMetric,
) -> None:
    existing = db.scalar(
        select(MetricSource).where(
            MetricSource.metric_value_id == metric_value.id,
            MetricSource.source_id == source.id,
        )
    )
    if existing:
        existing.evidence_note = metric.methodology_note
        return
    db.add(
        MetricSource(
            metric_value_id=metric_value.id,
            source_id=source.id,
            evidence_note=metric.methodology_note,
        )
    )


def upsert_confidence(db: Session, metric_value: MetricValue, confidence) -> None:
    existing = db.scalar(
        select(ConfidenceScore).where(ConfidenceScore.metric_value_id == metric_value.id)
    )
    payload = {
        "source_reliability": confidence.source_reliability,
        "data_freshness": confidence.data_freshness,
        "cross_verification": confidence.cross_verification,
        "methodology_transparency": confidence.methodology_transparency,
        "confidence_score": confidence.confidence_score,
        "confidence_label": confidence.confidence_label,
        "source_count": confidence.source_count,
        "methodology_note": confidence.methodology_note,
    }
    if not existing:
        db.add(ConfidenceScore(metric_value_id=metric_value.id, **payload))
        return
    for key, value in payload.items():
        setattr(existing, key, value)


def upsert_source_metric(
    db: Session,
    company: Company,
    source: Source,
    metric: AcquiredMetric,
    confidence_score_value: float,
) -> None:
    actor = system_user(db)
    existing = db.scalar(
        select(SourceMetric).where(
            SourceMetric.company_id == company.id,
            SourceMetric.source_id == source.id,
            SourceMetric.metric_type == metric.metric_key,
            SourceMetric.year == metric.period_end.year,
        )
    )
    payload = {
        "value_numeric": metric.value,
        "source_url": metric.source_url,
        "source_type": metric.source_type,
        "confidence_score": Decimal(str(confidence_score_value)),
        "retrieved_at": metric.retrieved_at,
        "freshness_score": freshness_score(
            metric.published_at or metric.retrieved_at, metric.retrieved_at
        ),
        "methodology_note": metric.methodology_note,
        "approved_status": "approved",
    }
    if not existing:
        db.add(
            SourceMetric(
                company_id=company.id,
                year=metric.period_end.year,
                metric_type=metric.metric_key,
                source_id=source.id,
                created_by_user_id=actor.id,
                **payload,
            )
        )
        return
    for key, value in payload.items():
        setattr(existing, key, value)


def ensure_realtime_metric_definitions(db: Session) -> None:
    for key in METRIC_REGISTRY:
        ensure_metric_definition(db, key)


def ensure_metric_definition(db: Session, key: str) -> MetricDefinition:
    config = METRIC_REGISTRY[key]
    definition = db.scalar(select(MetricDefinition).where(MetricDefinition.key == key))
    if definition:
        return definition
    definition = MetricDefinition(
        key=key,
        name=config["name"],
        description=f"Real-time refreshed {config['name']} from approved external sources.",
        unit=config["unit"],
        higher_is_better=config["higher_is_better"],
        aggregation_method="latest",
    )
    db.add(definition)
    db.flush()
    return definition


def ensure_target_companies(db: Session) -> dict[str, Company]:
    companies: dict[str, Company] = {}
    for target in ACQUISITION_TARGETS:
        company = db.scalar(select(Company).where(Company.slug == target.slug))
        if not company:
            company = Company(
                name=target.name,
                slug=target.slug,
                ticker=target.ticker,
                website_url=target.investor_relations_url,
                status="active",
            )
            db.add(company)
            db.flush()
        company.ticker = target.ticker
        company.website_url = company.website_url or target.investor_relations_url
        company.status = "active"
        companies[target.slug] = company
    return companies


def start_run(
    db: Session, company: Company, connector: str, source_name: str
) -> DataAcquisitionRun:
    run = DataAcquisitionRun(
        company_id=company.id,
        connector=connector,
        source_name=source_name,
        status="running",
        metadata_json="{}",
    )
    db.add(run)
    db.flush()
    return run


def complete_run(
    db: Session, run: DataAcquisitionRun, result: ConnectorResult, records_found: int
) -> None:
    run.status = "completed"
    run.completed_at = datetime.now(UTC)
    run.retrieved_at = result.retrieved_at
    run.records_found = records_found
    run.metadata_json = json.dumps(result.raw_payload, sort_keys=True)


def fail_run(db: Session, run: DataAcquisitionRun, message: str) -> None:
    run.status = "failed"
    run.completed_at = datetime.now(UTC)
    run.error_message = message


def data_acquisition_status(db: Session) -> dict[str, object]:
    runs = db.scalars(
        select(DataAcquisitionRun).order_by(DataAcquisitionRun.started_at.desc()).limit(50)
    ).all()
    return {
        "refresh_interval_seconds": REFRESH_INTERVAL_SECONDS,
        "sources": SOURCE_REGISTRY,
        "targets": [target.__dict__ for target in ACQUISITION_TARGETS],
        "runs": [run_payload(run) for run in runs],
    }


def run_payload(run: DataAcquisitionRun) -> dict[str, object]:
    return {
        "id": run.id,
        "company_id": run.company_id,
        "connector": run.connector,
        "source_name": run.source_name,
        "status": run.status,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "retrieved_at": run.retrieved_at.isoformat() if run.retrieved_at else None,
        "records_found": run.records_found,
        "error_message": run.error_message,
        "metadata": json.loads(run.metadata_json or "{}"),
    }


def connector_name(connector: object) -> str:
    return str(getattr(connector, "name", connector.__class__.__name__))


def source_name(connector: object) -> str:
    return str(getattr(connector, "source_name", connector.__class__.__name__))


def system_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.role == "admin").order_by(User.created_at))
    if user:
        return user
    user = User(
        email="system@openvalidations.com",
        full_name="APIP System",
        role="admin",
        status="active",
        password_hash="system-managed",
    )
    db.add(user)
    db.flush()
    return user


def write_audit_log(db: Session, action: str, metadata: dict[str, object]) -> None:
    db.add(
        AuditLog(
            actor_user_id=None,
            action=action,
            target_type="data_acquisition",
            target_id=None,
            metadata_json=json.dumps(metadata, sort_keys=True),
        )
    )
