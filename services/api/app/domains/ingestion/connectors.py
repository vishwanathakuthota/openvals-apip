from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Company, Source, SourceMetric
from app.domains.confidence.service import source_reliability_score
from app.domains.etl.csv_importer import imported_metric_confidence, parse_metric_row


@dataclass(frozen=True)
class EvidenceRecord:
    title: str
    source_type: str
    url: str
    publisher: str
    published_at: datetime
    methodology_note: str


class SecFilingsConnector:
    source_type = "sec_filing"

    def filing_index_url(self, cik: str) -> str:
        normalized = cik.strip().lstrip("0")
        if not normalized.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "invalid_cik", "message": "SEC CIK must be numeric."},
            )
        return f"https://www.sec.gov/edgar/browse/?CIK={normalized}"

    def source_record(
        self, company_name: str, cik: str, published_at: datetime | None = None
    ) -> EvidenceRecord:
        return EvidenceRecord(
            title=f"{company_name} SEC filing registry",
            source_type=self.source_type,
            url=self.filing_index_url(cik),
            publisher="SEC EDGAR",
            published_at=published_at or datetime.now(UTC),
            methodology_note=(
                "SEC filing connector registered official EDGAR evidence for APIP "
                "beta ingestion."
            ),
        )


class CsvImportConnector:
    required_columns = {"company", "year", "metric_type", "value", "source_url", "source_type"}

    def validate_row(self, row: dict[str, str], row_number: int = 2) -> dict[str, object]:
        return parse_metric_row(row, row_number)


class ManualResearchConnector:
    def create_source_metric(
        self,
        db: Session,
        company: Company,
        payload: dict[str, object],
        created_by_user_id: str,
    ) -> SourceMetric:
        source_type = required_text(payload, "source_type")
        source = Source(
            title=required_text(payload, "title"),
            source_type=source_type,
            url=required_text(payload, "source_url"),
            publisher=str(payload.get("publisher") or "Manual Research"),
            published_at=parse_optional_datetime(payload.get("published_at")),
            reliability_score=source_reliability_score(source_type),
            status="pending",
        )
        db.add(source)
        db.flush()
        parsed = {
            "methodology_note": required_text(payload, "methodology_note"),
        }
        confidence = imported_metric_confidence(parsed, source)
        source_metric = SourceMetric(
            company_id=company.id,
            year=required_int(payload, "year"),
            metric_type=required_text(payload, "metric_type").strip().lower().replace("-", "_"),
            value_numeric=required_decimal(payload, "value"),
            source_id=source.id,
            source_url=source.url or "",
            source_type=source.source_type,
            confidence_score=confidence,
            methodology_note=parsed["methodology_note"],
            created_by_user_id=created_by_user_id,
            approved_status="pending",
        )
        db.add(source_metric)
        db.flush()
        return source_metric


def required_text(payload: dict[str, object], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "validation_failed", "message": f"{key} is required."},
        )
    return value


def required_int(payload: dict[str, object], key: str) -> int:
    try:
        return int(required_text(payload, key))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "validation_failed", "message": f"{key} must be an integer."},
        ) from exc


def required_decimal(payload: dict[str, object], key: str) -> Decimal:
    try:
        return Decimal(required_text(payload, key))
    except (InvalidOperation, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "validation_failed", "message": f"{key} must be numeric."},
        ) from exc


def parse_optional_datetime(value: object) -> datetime:
    if not value:
        return datetime.now(UTC)
    if isinstance(value, datetime):
        return value
    text = str(value)
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed
