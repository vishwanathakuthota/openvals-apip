import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditLog, Company, MetricVersion, Source, SourceMetric
from app.domains.confidence.service import (
    calculate_confidence,
    cross_verification_score,
    freshness_score,
    methodology_transparency_score,
    source_reliability_score,
)

REQUIRED_COLUMNS = {
    "company",
    "year",
    "metric_type",
    "value",
    "source_url",
    "source_type",
}


@dataclass(frozen=True)
class ImportedSourceMetric:
    id: str
    company: str
    year: int
    metric_type: str
    value: float
    source_url: str
    source_type: str
    confidence_score: float
    approved_status: str


def import_financial_metrics_csv(
    db: Session,
    csv_text: str,
    created_by_user_id: str,
) -> list[ImportedSourceMetric]:
    reader = csv.DictReader(StringIO(csv_text))
    fieldnames = {field.strip() for field in reader.fieldnames or []}
    missing = sorted(REQUIRED_COLUMNS - fieldnames)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_csv_template",
                "message": f"CSV is missing required columns: {', '.join(missing)}.",
            },
        )

    imported: list[ImportedSourceMetric] = []
    for row_number, row in enumerate(reader, start=2):
        parsed = parse_metric_row(row, row_number)
        company = get_or_create_company(db, parsed["company"])
        source = create_source(db, parsed)
        confidence = imported_metric_confidence(parsed, source)
        source_metric = SourceMetric(
            company_id=company.id,
            year=parsed["year"],
            metric_type=parsed["metric_type"],
            value_numeric=parsed["value"],
            source_id=source.id,
            source_url=parsed["source_url"],
            source_type=parsed["source_type"],
            confidence_score=confidence,
            methodology_note=parsed["methodology_note"],
            created_by_user_id=created_by_user_id,
            approved_status="pending",
        )
        db.add(source_metric)
        db.flush()
        db.add(
            MetricVersion(
                source_metric_id=source_metric.id,
                metric_value_id=None,
                version=1,
                value_numeric=parsed["value"],
                approved_status="pending",
                created_by_user_id=created_by_user_id,
            )
        )
        write_audit_log(
            db,
            actor_user_id=created_by_user_id,
            action="source_metric.imported",
            target_type="source_metric",
            target_id=source_metric.id,
            metadata={
                "company": company.name,
                "year": parsed["year"],
                "metric_type": parsed["metric_type"],
                "source_id": source.id,
            },
        )
        imported.append(
            ImportedSourceMetric(
                id=source_metric.id,
                company=company.name,
                year=source_metric.year,
                metric_type=source_metric.metric_type,
                value=float(source_metric.value_numeric),
                source_url=source_metric.source_url,
                source_type=source_metric.source_type,
                confidence_score=float(source_metric.confidence_score),
                approved_status=source_metric.approved_status,
            )
        )
    if not imported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "empty_csv", "message": "CSV did not contain metric rows."},
        )
    return imported


def parse_metric_row(row: dict[str, str], row_number: int) -> dict[str, Any]:
    company = required_string(row, "company", row_number)
    metric_type = normalize_key(required_string(row, "metric_type", row_number))
    source_url = required_string(row, "source_url", row_number)
    source_type = normalize_key(required_string(row, "source_type", row_number))
    methodology_note = (
        row.get("methodology_note")
        or f"CSV import for {company} {metric_type} metric using {source_type} evidence."
    ).strip()
    try:
        year = int(required_string(row, "year", row_number))
    except ValueError as exc:
        raise row_error(row_number, "year must be an integer.") from exc
    if year < 1900 or year > 2100:
        raise row_error(row_number, "year must be between 1900 and 2100.")
    try:
        value = Decimal(required_string(row, "value", row_number))
    except (InvalidOperation, ValueError) as exc:
        raise row_error(row_number, "value must be numeric.") from exc
    if not source_url.startswith(("https://", "http://")):
        raise row_error(row_number, "source_url must start with http:// or https://.")
    return {
        "company": company,
        "year": year,
        "metric_type": metric_type,
        "value": value,
        "source_url": source_url,
        "source_type": source_type,
        "methodology_note": methodology_note,
        "publisher": (row.get("publisher") or "CSV Import").strip(),
        "published_at": parse_published_at(row.get("published_at"), row_number),
    }


def required_string(row: dict[str, str], column: str, row_number: int) -> str:
    value = (row.get(column) or "").strip()
    if not value:
        raise row_error(row_number, f"{column} is required.")
    return value


def row_error(row_number: int, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"code": "invalid_csv_row", "message": f"Row {row_number}: {message}"},
    )


def parse_published_at(value: str | None, row_number: int) -> datetime:
    if not value:
        return datetime.now(UTC)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise row_error(row_number, "published_at must be ISO 8601 when provided.") from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def get_or_create_company(db: Session, name: str) -> Company:
    slug = slugify(name)
    company = db.scalar(select(Company).where(Company.slug == slug))
    if company:
        return company
    company = Company(name=name, slug=slug, ticker=None, status="active")
    db.add(company)
    db.flush()
    return company


def create_source(db: Session, parsed: dict[str, Any]) -> Source:
    source = Source(
        title=f"{parsed['company']} {parsed['year']} {parsed['metric_type']} CSV source",
        source_type=parsed["source_type"],
        url=parsed["source_url"],
        publisher=parsed["publisher"],
        published_at=parsed["published_at"],
        reliability_score=source_reliability_score(parsed["source_type"]),
        status="pending",
    )
    db.add(source)
    db.flush()
    return source


def imported_metric_confidence(parsed: dict[str, Any], source: Source) -> float:
    confidence = calculate_confidence(
        source_reliability=source.reliability_score,
        data_freshness=freshness_score(source.published_at),
        cross_verification=cross_verification_score(1),
        methodology_transparency=methodology_transparency_score(parsed["methodology_note"]),
    )
    return float(confidence["score"])


def write_audit_log(
    db: Session,
    actor_user_id: str | None,
    action: str,
    target_type: str,
    target_id: str | None,
    metadata: dict[str, Any],
) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata_json=json.dumps(metadata, sort_keys=True),
        )
    )


def normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def slugify(value: str) -> str:
    return normalize_key(value).replace("_", "-")
