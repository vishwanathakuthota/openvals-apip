from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class NormalizedLiveRecord:
    company_slug: str
    metric_type: str
    source_url: str
    source_type: str
    retrieved_at: datetime
    raw_payload: dict[str, Any]
    value: float | None = None
    symbol: str | None = None
    currency: str | None = None
    fiscal_year: int | None = None
    fiscal_period: str | None = None
    freshness_score: int = 100
    confidence_score: float = 0
    ingestion_status: str = "success"
    filing_accession: str | None = None
    filing_form: str | None = None
    period_end: date | None = None
    raw_payload_hash: str = field(init=False)
    raw_payload_snapshot: str = field(init=False)

    def __post_init__(self) -> None:
        snapshot = json.dumps(_jsonable(self.raw_payload), sort_keys=True, separators=(",", ":"))
        object.__setattr__(self, "raw_payload_snapshot", snapshot[:10000])
        object.__setattr__(
            self,
            "raw_payload_hash",
            hashlib.sha256(snapshot.encode("utf-8")).hexdigest(),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["retrieved_at"] = self.retrieved_at.isoformat()
        payload["period_end"] = self.period_end.isoformat() if self.period_end else None
        return payload


def utc_now() -> datetime:
    return datetime.now(UTC)


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value
