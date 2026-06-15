from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import (
    Company,
    ConfidenceScore,
    IngestionRun,
    LiveDataRecord,
    MetricDefinition,
    MetricSource,
    MetricValue,
    Source,
)
from app.domains.confidence.service import score_metric_confidence, source_reliability_score
from app.domains.ingestion.connectors import SecEdgarConnector, YahooFinanceConnector
from app.domains.ingestion.records import NormalizedLiveRecord


@dataclass(frozen=True)
class IngestionTarget:
    slug: str
    ticker: str | None
    cik: str | None
    investor_relations_url: str | None = None


INGESTION_TARGETS: tuple[IngestionTarget, ...] = (
    IngestionTarget("microsoft", "MSFT", "789019", "https://www.microsoft.com/en-us/investor"),
    IngestionTarget("nvidia", "NVDA", "1045810", "https://investor.nvidia.com"),
    IngestionTarget("alphabet", "GOOGL", "1652044", "https://abc.xyz/investor"),
    IngestionTarget("meta", "META", "1326801", "https://investor.fb.com"),
    IngestionTarget("amazon", "AMZN", "1018724", "https://ir.aboutamazon.com"),
)

METRIC_DEFINITIONS = {
    "market_cap": ("Market Cap", "Latest public equity market capitalization.", "usd"),
    "stock_price": ("Stock Price", "Latest public equity stock price.", "usd"),
    "revenue": ("Revenue", "Latest reported or refreshed company revenue.", "usd"),
    "operating_income": (
        "Operating Income",
        "Latest reported operating income from filings or financial data.",
        "usd",
    ),
    "cash_flow": (
        "Operating Cash Flow",
        "Latest reported operating cash flow from filings or financial data.",
        "usd",
    ),
    "capex": ("Capital Expenditure", "Latest reported capital expenditure.", "usd"),
    "eps": ("EPS", "Latest reported diluted earnings per share.", "usd"),
}


def run_live_ingestion(db: Session) -> dict[str, Any]:
    run = IngestionRun(source_type="live_data", status="running", started_at=datetime.now(UTC))
    db.add(run)
    db.flush()
    records_created = 0
    records_failed = 0
    messages: list[str] = []

    yahoo = YahooFinanceConnector() if settings.yahoo_finance_enabled else None
    sec = SecEdgarConnector(settings.sec_user_agent)

    for target in INGESTION_TARGETS:
        company = db.scalar(select(Company).where(Company.slug == target.slug))
        if not company:
            messages.append(f"{target.slug}: company not configured")
            records_failed += 1
            continue

        connector_records: list[NormalizedLiveRecord] = []
        if yahoo and target.ticker:
            try:
                connector_records.extend(yahoo.fetch(target.slug, target.ticker))
            except Exception as exc:  # pragma: no cover - live network guard
                records_failed += 1
                messages.append(f"{target.slug}: yahoo_finance failed: {exc}")
        if target.cik:
            try:
                connector_records.extend(sec.fetch(target.slug, target.cik))
            except Exception as exc:  # pragma: no cover - live network guard
                records_failed += 1
                messages.append(f"{target.slug}: sec_edgar failed: {exc}")

        for record in connector_records:
            db.add(_live_data_record(run.id, company.id, record))
            records_created += 1
            if record.value is not None and record.metric_type != "sec_filing_metadata":
                _sync_metric_value(db, company, record)

    run.status = "completed" if records_failed == 0 else "partial"
    run.completed_at = datetime.now(UTC)
    run.records_created = records_created
    run.records_failed = records_failed
    run.message = "; ".join(messages) if messages else "Live ingestion completed."
    db.commit()
    db.refresh(run)
    return ingestion_run_payload(run)


def ingestion_status(db: Session) -> dict[str, Any]:
    last_run = db.scalar(select(IngestionRun).order_by(IngestionRun.started_at.desc()))
    recent_records = db.scalars(
        select(LiveDataRecord).order_by(LiveDataRecord.retrieved_at.desc()).limit(25)
    ).all()
    return {
        "enabled": True,
        "yahoo_finance_enabled": settings.yahoo_finance_enabled,
        "sec_edgar_enabled": bool(settings.sec_user_agent),
        "interval_minutes": settings.ingestion_interval_minutes,
        "scheduler_task": "apip.ingest_live_data",
        "last_run": ingestion_run_payload(last_run) if last_run else None,
        "recent_records": [live_data_record_payload(record) for record in recent_records],
    }


def ingestion_run_payload(run: IngestionRun) -> dict[str, Any]:
    return {
        "id": run.id,
        "source_type": run.source_type,
        "status": run.status,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "records_created": run.records_created,
        "records_failed": run.records_failed,
        "message": run.message,
    }


def live_data_record_payload(record: LiveDataRecord) -> dict[str, Any]:
    return {
        "id": record.id,
        "company_slug": record.company_slug,
        "symbol": record.symbol,
        "metric_type": record.metric_type,
        "value": float(record.value_numeric) if record.value_numeric is not None else None,
        "currency": record.currency,
        "source_url": record.source_url,
        "source_type": record.source_type,
        "retrieved_at": record.retrieved_at.isoformat(),
        "freshness_score": record.freshness_score,
        "confidence_score": float(record.confidence_score),
        "raw_payload_hash": record.raw_payload_hash,
        "ingestion_status": record.ingestion_status,
        "filing_accession": record.filing_accession,
        "filing_form": record.filing_form,
        "period_end": record.period_end.isoformat() if record.period_end else None,
    }


def _live_data_record(
    run_id: str,
    company_id: str,
    record: NormalizedLiveRecord,
) -> LiveDataRecord:
    return LiveDataRecord(
        run_id=run_id,
        company_id=company_id,
        company_slug=record.company_slug,
        symbol=record.symbol,
        metric_type=record.metric_type,
        value_numeric=record.value,
        currency=record.currency,
        fiscal_year=record.fiscal_year,
        fiscal_period=record.fiscal_period,
        source_url=record.source_url,
        source_type=record.source_type,
        retrieved_at=record.retrieved_at,
        freshness_score=record.freshness_score,
        confidence_score=record.confidence_score,
        raw_payload_hash=record.raw_payload_hash,
        raw_payload_snapshot=record.raw_payload_snapshot,
        ingestion_status=record.ingestion_status,
        filing_accession=record.filing_accession,
        filing_form=record.filing_form,
        period_end=record.period_end,
    )


def _sync_metric_value(db: Session, company: Company, record: NormalizedLiveRecord) -> None:
    definition = _metric_definition(db, record.metric_type)
    period_end = record.period_end or record.retrieved_at.date()
    period_start = date(period_end.year, 1, 1)
    if record.metric_type in {"market_cap", "stock_price"}:
        period_start = period_end
    metric_value = db.scalar(
        select(MetricValue).where(
            MetricValue.metric_definition_id == definition.id,
            MetricValue.entity_type == "company",
            MetricValue.entity_id == company.id,
            MetricValue.period_start == period_start,
            MetricValue.period_end == period_end,
        )
    )
    if not metric_value:
        metric_value = MetricValue(
            metric_definition_id=definition.id,
            entity_type="company",
            entity_id=company.id,
            period_start=period_start,
            period_end=period_end,
            value_numeric=record.value,
            currency=record.currency,
            methodology=(
                "Refreshed by APIP live data ingestion from approved free public sources."
            ),
            status="approved",
        )
        db.add(metric_value)
        db.flush()
    else:
        metric_value.value_numeric = record.value
        metric_value.currency = record.currency
        metric_value.methodology = (
            "Refreshed by APIP live data ingestion from approved free public sources."
        )

    source = _source(db, record)
    if not db.scalar(
        select(MetricSource).where(
            MetricSource.metric_value_id == metric_value.id,
            MetricSource.source_id == source.id,
        )
    ):
        db.add(
            MetricSource(
                metric_value_id=metric_value.id,
                source_id=source.id,
                evidence_note=f"Retrieved at {record.retrieved_at.isoformat()}",
            )
        )
    if not metric_value.confidence_score:
        confidence = score_metric_confidence(metric_value, [source])
        db.add(
            ConfidenceScore(
                metric_value_id=metric_value.id,
                source_reliability=confidence.source_reliability,
                data_freshness=confidence.data_freshness,
                cross_verification=confidence.cross_verification,
                methodology_transparency=confidence.methodology_transparency,
                confidence_score=record.confidence_score or confidence.confidence_score,
                confidence_label=confidence.confidence_label,
                source_count=confidence.source_count,
                methodology_note=confidence.methodology_note,
            )
        )


def _metric_definition(db: Session, metric_type: str) -> MetricDefinition:
    definition = db.scalar(select(MetricDefinition).where(MetricDefinition.key == metric_type))
    if definition:
        return definition
    name, description, unit = METRIC_DEFINITIONS.get(
        metric_type,
        (metric_type.replace("_", " ").title(), "Live data ingestion metric.", "value"),
    )
    definition = MetricDefinition(
        key=metric_type,
        name=name,
        description=description,
        unit=unit,
        higher_is_better=0 if metric_type in {"capex"} else 1,
        aggregation_method="latest",
    )
    db.add(definition)
    db.flush()
    return definition


def _source(db: Session, record: NormalizedLiveRecord) -> Source:
    source = db.scalar(select(Source).where(Source.url == record.source_url))
    if source:
        return source
    source = Source(
        title=f"{record.source_type.replace('_', ' ').title()} - {record.company_slug}",
        source_type=record.source_type,
        url=record.source_url,
        publisher="Yahoo Finance" if record.source_type == "yahoo_finance" else "SEC EDGAR",
        published_at=record.retrieved_at,
        reliability_score=source_reliability_score(record.source_type),
        status="approved",
    )
    db.add(source)
    db.flush()
    return source
