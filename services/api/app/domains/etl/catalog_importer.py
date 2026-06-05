import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from io import StringIO
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AIModel, Company, Country, DataLineage, Industry, Source
from app.domains.confidence.service import (
    calculate_confidence,
    cross_verification_score,
    freshness_score,
    methodology_transparency_score,
    source_reliability_score,
)
from app.domains.etl.csv_importer import write_audit_log

COMMON_COLUMNS = {"source_url", "source_type"}
REQUIRED_COLUMNS = {
    "companies": COMMON_COLUMNS | {"name"},
    "industries": COMMON_COLUMNS | {"name"},
    "countries": COMMON_COLUMNS | {"name", "iso_code"},
    "models": COMMON_COLUMNS | {"name", "model_family"},
}
ENTITY_TYPES = set(REQUIRED_COLUMNS)
ENTITY_ALIASES = {
    "company": "companies",
    "companies": "companies",
    "industry": "industries",
    "industries": "industries",
    "country": "countries",
    "countries": "countries",
    "model": "models",
    "models": "models",
    "ai_model": "models",
    "ai_models": "models",
}
SINGULAR_ENTITY_TYPES = {
    "companies": "company",
    "industries": "industry",
    "countries": "country",
    "models": "model",
}
STATUS_VALUES = {"active", "archived"}


@dataclass(frozen=True)
class ImportedCatalogRecord:
    id: str
    entity_type: str
    entity_id: str
    name: str
    source_url: str
    source_type: str
    confidence_score: float
    imported_by: str
    imported_at: str
    lineage_id: str
    import_batch_id: str


def import_catalog_csv(
    db: Session,
    entity_type: str,
    csv_text: str,
    imported_by_user_id: str,
) -> list[ImportedCatalogRecord]:
    normalized_entity_type = normalize_entity_type(entity_type)
    reader = csv.DictReader(StringIO(csv_text))
    fieldnames = {field.strip() for field in reader.fieldnames or []}
    missing = sorted(REQUIRED_COLUMNS[normalized_entity_type] - fieldnames)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_csv_template",
                "message": f"CSV is missing required columns: {', '.join(missing)}.",
            },
        )

    imported: list[ImportedCatalogRecord] = []
    import_batch_id = str(uuid4())
    for row_number, row in enumerate(reader, start=2):
        parsed = parse_catalog_row(normalized_entity_type, row, row_number)
        source = get_or_create_source(db, parsed, normalized_entity_type, imported_by_user_id)
        entity, action = upsert_entity(db, normalized_entity_type, parsed)
        confidence_score = catalog_confidence(parsed, source)
        imported_at = datetime.now(UTC)
        lineage = DataLineage(
            entity_type=normalized_entity_type,
            entity_id=entity.id,
            source_id=source.id,
            source_url=parsed["source_url"],
            source_type=parsed["source_type"],
            confidence_score=confidence_score,
            imported_by_user_id=imported_by_user_id,
            imported_at=imported_at,
            import_batch_id=import_batch_id,
            action=action,
            metadata_json=json.dumps(parsed["lineage_metadata"], sort_keys=True),
        )
        db.add(lineage)
        db.flush()
        singular_entity_type = SINGULAR_ENTITY_TYPES[normalized_entity_type]
        write_audit_log(
            db,
            actor_user_id=imported_by_user_id,
            action=f"{singular_entity_type}.{action}",
            target_type=singular_entity_type,
            target_id=entity.id,
            metadata={
                "source_id": source.id,
                "lineage_id": lineage.id,
                "confidence_score": confidence_score,
                "import_batch_id": import_batch_id,
            },
        )
        imported.append(
            ImportedCatalogRecord(
                id=lineage.id,
                entity_type=normalized_entity_type,
                entity_id=entity.id,
                name=entity.name,
                source_url=lineage.source_url,
                source_type=lineage.source_type,
                confidence_score=float(lineage.confidence_score),
                imported_by=imported_by_user_id,
                imported_at=imported_at.isoformat(),
                lineage_id=lineage.id,
                import_batch_id=import_batch_id,
            )
        )
    if not imported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "empty_csv", "message": "CSV did not contain catalog rows."},
        )
    return imported


def normalize_entity_type(entity_type: str) -> str:
    normalized = entity_type.strip().lower().replace("-", "_")
    plural = ENTITY_ALIASES.get(normalized)
    if not plural:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_catalog_import_type",
                "message": "Import type must be companies, industries, countries, or models.",
            },
        )
    return plural


def parse_catalog_row(entity_type: str, row: dict[str, str], row_number: int) -> dict[str, Any]:
    name = required_string(row, "name", row_number)
    source_url = required_string(row, "source_url", row_number)
    source_type = normalize_key(required_string(row, "source_type", row_number))
    if not source_url.startswith(("https://", "http://")):
        raise row_error(row_number, "source_url must start with http:// or https://.")
    status_value = (row.get("status") or "active").strip().lower()
    if status_value not in STATUS_VALUES:
        raise row_error(row_number, "status must be active or archived.")
    parsed: dict[str, Any] = {
        "name": name,
        "slug": slugify(row.get("slug") or name),
        "status": status_value,
        "source_url": source_url,
        "source_type": source_type,
        "source_title": (row.get("source_title") or f"{name} catalog source").strip(),
        "publisher": (row.get("publisher") or "CSV Import").strip(),
        "published_at": parse_published_at(row.get("published_at"), row_number),
        "methodology_note": (
            row.get("methodology_note")
            or f"Catalog import for {entity_type} record {name} using {source_type} evidence."
        ).strip(),
    }
    if entity_type == "companies":
        parsed["ticker"] = optional_string(row.get("ticker"))
        parsed["website_url"] = optional_url(row.get("website_url"), row_number, "website_url")
        parsed["headquarters_country_iso_code"] = optional_string(
            row.get("headquarters_country_iso_code")
        )
    elif entity_type == "countries":
        parsed["iso_code"] = required_string(row, "iso_code", row_number).upper()
        if len(parsed["iso_code"]) != 2:
            raise row_error(row_number, "iso_code must be a two-letter ISO code.")
        parsed["region"] = optional_string(row.get("region"))
    elif entity_type == "models":
        parsed["model_family"] = required_string(row, "model_family", row_number)
        parsed["provider_company_slug"] = optional_string(row.get("provider_company_slug"))
    parsed["lineage_metadata"] = {key: serialize_value(value) for key, value in parsed.items()}
    return parsed


def upsert_entity(db: Session, entity_type: str, parsed: dict[str, Any]) -> tuple[Any, str]:
    if entity_type == "companies":
        company = db.scalar(select(Company).where(Company.slug == parsed["slug"]))
        country_id = country_id_for_iso(db, parsed.get("headquarters_country_iso_code"))
        if company:
            company.name = parsed["name"]
            company.ticker = parsed["ticker"]
            company.website_url = parsed["website_url"]
            company.headquarters_country_id = country_id
            company.status = parsed["status"]
            return company, "updated"
        company = Company(
            name=parsed["name"],
            slug=parsed["slug"],
            ticker=parsed["ticker"],
            website_url=parsed["website_url"],
            headquarters_country_id=country_id,
            status=parsed["status"],
        )
        db.add(company)
        db.flush()
        return company, "imported"
    if entity_type == "industries":
        industry = db.scalar(select(Industry).where(Industry.slug == parsed["slug"]))
        if industry:
            industry.name = parsed["name"]
            industry.status = parsed["status"]
            return industry, "updated"
        industry = Industry(name=parsed["name"], slug=parsed["slug"], status=parsed["status"])
        db.add(industry)
        db.flush()
        return industry, "imported"
    if entity_type == "countries":
        country = db.scalar(select(Country).where(Country.iso_code == parsed["iso_code"]))
        if country:
            country.name = parsed["name"]
            country.slug = parsed["slug"]
            country.region = parsed["region"]
            return country, "updated"
        country = Country(
            name=parsed["name"],
            slug=parsed["slug"],
            iso_code=parsed["iso_code"],
            region=parsed["region"],
        )
        db.add(country)
        db.flush()
        return country, "imported"
    model = db.scalar(select(AIModel).where(AIModel.slug == parsed["slug"]))
    provider_company_id = company_id_for_slug(db, parsed.get("provider_company_slug"))
    if model:
        model.name = parsed["name"]
        model.model_family = parsed["model_family"]
        model.provider_company_id = provider_company_id
        model.status = parsed["status"]
        return model, "updated"
    model = AIModel(
        name=parsed["name"],
        slug=parsed["slug"],
        model_family=parsed["model_family"],
        provider_company_id=provider_company_id,
        status=parsed["status"],
    )
    db.add(model)
    db.flush()
    return model, "imported"


def get_or_create_source(
    db: Session,
    parsed: dict[str, Any],
    entity_type: str,
    imported_by_user_id: str,
) -> Source:
    source = db.scalar(select(Source).where(Source.url == parsed["source_url"]))
    if source:
        source.title = parsed["source_title"]
        source.source_type = parsed["source_type"]
        source.publisher = parsed["publisher"]
        source.published_at = parsed["published_at"]
        source.reliability_score = source_reliability_score(parsed["source_type"])
        source.status = "approved"
        return source
    source = Source(
        title=parsed["source_title"],
        source_type=parsed["source_type"],
        url=parsed["source_url"],
        publisher=parsed["publisher"],
        published_at=parsed["published_at"],
        reliability_score=source_reliability_score(parsed["source_type"]),
        status="approved",
    )
    db.add(source)
    db.flush()
    write_audit_log(
        db,
        actor_user_id=imported_by_user_id,
        action="source.catalog_attached",
        target_type="source",
        target_id=source.id,
        metadata={"entity_type": entity_type, "source_url": source.url},
    )
    return source


def catalog_confidence(parsed: dict[str, Any], source: Source) -> float:
    confidence = calculate_confidence(
        source_reliability=source.reliability_score,
        data_freshness=freshness_score(source.published_at),
        cross_verification=cross_verification_score(1),
        methodology_transparency=methodology_transparency_score(parsed["methodology_note"]),
    )
    return float(confidence["score"])


def country_id_for_iso(db: Session, iso_code: str | None) -> str | None:
    if not iso_code:
        return None
    country = db.scalar(select(Country).where(Country.iso_code == iso_code.upper()))
    if not country:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "country_not_found",
                "message": f"Country with ISO code {iso_code.upper()} must be imported first.",
            },
        )
    return country.id


def company_id_for_slug(db: Session, slug: str | None) -> str | None:
    if not slug:
        return None
    company = db.scalar(select(Company).where(Company.slug == slugify(slug)))
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "provider_company_not_found",
                "message": f"Provider company {slug} must be imported first.",
            },
        )
    return company.id


def required_string(row: dict[str, str], column: str, row_number: int) -> str:
    value = (row.get(column) or "").strip()
    if not value:
        raise row_error(row_number, f"{column} is required.")
    return value


def optional_string(value: str | None) -> str | None:
    stripped = (value or "").strip()
    return stripped or None


def optional_url(value: str | None, row_number: int, column: str) -> str | None:
    stripped = optional_string(value)
    if stripped and not stripped.startswith(("https://", "http://")):
        raise row_error(row_number, f"{column} must start with http:// or https://.")
    return stripped


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


def normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def slugify(value: str) -> str:
    return normalize_key(value).replace("_", "-")


def serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value
