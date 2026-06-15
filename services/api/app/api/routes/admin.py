import json
from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.db.models import (
    AIModel,
    ApiKey,
    AuditLog,
    Company,
    ConfidenceScore,
    Country,
    Industry,
    IngestionRun,
    LiveDataRecord,
    MetricDefinition,
    MetricSource,
    MetricValue,
    MetricVersion,
    Source,
    SourceMetric,
)
from app.db.seed import seed_database
from app.domains.confidence.service import score_metric_confidence, source_reliability_score
from app.domains.etl.csv_importer import import_financial_metrics_csv, write_audit_log
from app.domains.identity.api_keys import api_key_payload, generate_api_key, normalize_plan
from app.domains.ingestion.service import (
    ingestion_run_payload,
    ingestion_status,
    run_live_ingestion,
)

router = APIRouter()


@router.get("/dashboard")
def admin_dashboard(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    last_ingestion_run = db.scalar(select(IngestionRun).order_by(IngestionRun.started_at.desc()))
    return {
        "counts": {
            "companies": len(db.scalars(select(Company)).all()),
            "industries": len(db.scalars(select(Industry)).all()),
            "countries": len(db.scalars(select(Country)).all()),
            "models": len(db.scalars(select(AIModel)).all()),
            "sources": len(db.scalars(select(Source)).all()),
            "pending_imported_metrics": len(
                db.scalars(
                    select(SourceMetric).where(SourceMetric.approved_status == "pending")
                ).all()
            ),
            "audit_logs": len(db.scalars(select(AuditLog)).all()),
            "api_keys": len(db.scalars(select(ApiKey)).all()),
            "live_data_records": len(db.scalars(select(LiveDataRecord)).all()),
        },
        "ingestion": ingestion_run_payload(last_ingestion_run) if last_ingestion_run else None,
    }


@router.get("/api-keys")
def admin_list_api_keys(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items = db.scalars(select(ApiKey).order_by(ApiKey.created_at.desc())).all()
    return {"items": [api_key_payload(item) for item in items]}


@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
def admin_generate_api_key(
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    generated = generate_api_key(
        db,
        name=required_text(payload, "name"),
        plan=str(payload.get("plan") or "free"),
        created_by_user_id=claims["sub"],
    )
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="api_key.created",
        target_type="api_key",
        target_id=generated.record.id,
        metadata={"name": generated.record.name, "plan": generated.record.plan},
    )
    db.commit()
    return {**api_key_payload(generated.record), "api_key": generated.plaintext_key}


@router.patch("/api-keys/{api_key_id}")
def admin_update_api_key(
    api_key_id: str,
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    api_key = get_or_404(db, ApiKey, api_key_id, "api_key_not_found")
    if "name" in payload:
        api_key.name = required_text(payload, "name")
    if "plan" in payload:
        api_key.plan = normalize_plan(str(payload["plan"]))
        api_key.daily_limit = {"free": 100, "pro": 5000, "enterprise": None}[api_key.plan]
    if "status" in payload:
        api_key.status = required_text(payload, "status")
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="api_key.updated",
        target_type="api_key",
        target_id=api_key.id,
        metadata={"name": api_key.name, "plan": api_key.plan, "status": api_key.status},
    )
    db.commit()
    return api_key_payload(api_key)


@router.get("/companies")
def admin_list_companies(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items = db.scalars(select(Company).order_by(Company.name)).all()
    return {"items": [company_payload(item) for item in items]}


@router.post("/companies", status_code=status.HTTP_201_CREATED)
def admin_create_company(
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    name = required_text(payload, "name")
    company = Company(
        name=name,
        slug=unique_slug(db, Company, str(payload.get("slug") or slugify(name))),
        ticker=optional_text(payload.get("ticker")),
        website_url=optional_text(payload.get("website_url")),
        status=str(payload.get("status") or "active"),
    )
    db.add(company)
    db.flush()
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="company.created",
        target_type="company",
        target_id=company.id,
        metadata={"name": company.name},
    )
    db.commit()
    return company_payload(company)


@router.patch("/companies/{company_id}")
def admin_update_company(
    company_id: str,
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    company = get_or_404(db, Company, company_id, "company_not_found")
    update_fields(company, payload, ["name", "ticker", "website_url", "status"])
    if "slug" in payload:
        company.slug = str(payload["slug"])
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="company.updated",
        target_type="company",
        target_id=company.id,
        metadata={"name": company.name},
    )
    db.commit()
    return company_payload(company)


@router.get("/industries")
def admin_list_industries(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items = db.scalars(select(Industry).order_by(Industry.name)).all()
    return {"items": [industry_payload(item) for item in items]}


@router.post("/industries", status_code=status.HTTP_201_CREATED)
def admin_create_industry(
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    name = required_text(payload, "name")
    industry = Industry(
        name=name,
        slug=unique_slug(db, Industry, str(payload.get("slug") or slugify(name))),
        status=str(payload.get("status") or "active"),
    )
    db.add(industry)
    db.flush()
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="industry.created",
        target_type="industry",
        target_id=industry.id,
        metadata={"name": industry.name},
    )
    db.commit()
    return industry_payload(industry)


@router.patch("/industries/{industry_id}")
def admin_update_industry(
    industry_id: str,
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    industry = get_or_404(db, Industry, industry_id, "industry_not_found")
    update_fields(industry, payload, ["name", "status"])
    if "slug" in payload:
        industry.slug = str(payload["slug"])
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="industry.updated",
        target_type="industry",
        target_id=industry.id,
        metadata={"name": industry.name},
    )
    db.commit()
    return industry_payload(industry)


@router.get("/countries")
def admin_list_countries(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items = db.scalars(select(Country).order_by(Country.name)).all()
    return {"items": [country_payload(item) for item in items]}


@router.post("/countries", status_code=status.HTTP_201_CREATED)
def admin_create_country(
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    name = required_text(payload, "name")
    country = Country(
        name=name,
        slug=unique_slug(db, Country, str(payload.get("slug") or slugify(name))),
        iso_code=required_text(payload, "iso_code").upper(),
        region=optional_text(payload.get("region")),
    )
    db.add(country)
    db.flush()
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="country.created",
        target_type="country",
        target_id=country.id,
        metadata={"name": country.name, "iso_code": country.iso_code},
    )
    db.commit()
    return country_payload(country)


@router.patch("/countries/{country_id}")
def admin_update_country(
    country_id: str,
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    country = get_or_404(db, Country, country_id, "country_not_found")
    update_fields(country, payload, ["name", "slug", "region"])
    if "iso_code" in payload:
        country.iso_code = required_text(payload, "iso_code").upper()
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="country.updated",
        target_type="country",
        target_id=country.id,
        metadata={"name": country.name},
    )
    db.commit()
    return country_payload(country)


@router.get("/models")
def admin_list_models(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items = db.scalars(select(AIModel).order_by(AIModel.name)).all()
    return {"items": [model_payload(item) for item in items]}


@router.post("/models", status_code=status.HTTP_201_CREATED)
def admin_create_model(
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    name = required_text(payload, "name")
    model = AIModel(
        name=name,
        slug=unique_slug(db, AIModel, str(payload.get("slug") or slugify(name))),
        model_family=required_text(payload, "model_family"),
        provider_company_id=optional_text(payload.get("provider_company_id")),
        status=str(payload.get("status") or "active"),
    )
    db.add(model)
    db.flush()
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="model.created",
        target_type="model",
        target_id=model.id,
        metadata={"name": model.name},
    )
    db.commit()
    return model_payload(model)


@router.patch("/models/{model_id}")
def admin_update_model(
    model_id: str,
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    model = get_or_404(db, AIModel, model_id, "model_not_found")
    update_fields(model, payload, ["name", "slug", "model_family", "provider_company_id", "status"])
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="model.updated",
        target_type="model",
        target_id=model.id,
        metadata={"name": model.name},
    )
    db.commit()
    return model_payload(model)


@router.get("/sources")
def admin_list_sources(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items = db.scalars(select(Source).order_by(Source.created_at.desc())).all()
    return {"items": [source_payload(item) for item in items]}


@router.post("/sources", status_code=status.HTTP_201_CREATED)
def admin_create_source(
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    source_type = required_text(payload, "source_type")
    source = Source(
        title=required_text(payload, "title"),
        source_type=source_type,
        url=optional_text(payload.get("url")),
        publisher=optional_text(payload.get("publisher")),
        published_at=None,
        reliability_score=source_reliability_score(source_type),
        status=str(payload.get("status") or "pending"),
    )
    db.add(source)
    db.flush()
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="source.created",
        target_type="source",
        target_id=source.id,
        metadata={"title": source.title},
    )
    db.commit()
    return source_payload(source)


@router.patch("/sources/{source_id}")
def admin_update_source(
    source_id: str,
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    source = get_or_404(db, Source, source_id, "source_not_found")
    update_fields(source, payload, ["title", "source_type", "url", "publisher", "status"])
    if "source_type" in payload:
        source.reliability_score = source_reliability_score(source.source_type)
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="source.updated",
        target_type="source",
        target_id=source.id,
        metadata={"title": source.title, "status": source.status},
    )
    db.commit()
    return source_payload(source)


@router.patch("/sources/{source_id}/approve")
def admin_approve_source(
    source_id: str,
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    source = get_or_404(db, Source, source_id, "source_not_found")
    source.status = "approved"
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="source.approved",
        target_type="source",
        target_id=source.id,
        metadata={"title": source.title},
    )
    db.commit()
    return source_payload(source)


@router.patch("/sources/{source_id}/reject")
def admin_reject_source(
    source_id: str,
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    source = get_or_404(db, Source, source_id, "source_not_found")
    source.status = "rejected"
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="source.rejected",
        target_type="source",
        target_id=source.id,
        metadata={"title": source.title},
    )
    db.commit()
    return source_payload(source)


@router.post("/seed-import")
def admin_seed_import(
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    seed_database(db)
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="seed_import.triggered",
        target_type="seed_import",
        target_id=None,
        metadata={"status": "completed"},
    )
    db.commit()
    return {"status": "completed"}


@router.get("/ingestion/status")
def admin_ingestion_status(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return ingestion_status(db)


@router.post("/ingestion/run")
def admin_run_ingestion(
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    result = run_live_ingestion(db)
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="live_ingestion.triggered",
        target_type="ingestion",
        target_id=str(result.get("id")),
        metadata={"status": result.get("status")},
    )
    db.commit()
    return result


@router.post("/imports/csv", status_code=status.HTTP_201_CREATED)
async def upload_financial_metrics_csv(
    file: UploadFile = File(...),
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "invalid_file_type", "message": "Upload a .csv file."},
        )
    csv_text = (await file.read()).decode("utf-8-sig")
    imported = import_financial_metrics_csv(db, csv_text, created_by_user_id=claims["sub"])
    db.commit()
    return {
        "imported_count": len(imported),
        "items": [item.__dict__ for item in imported],
    }


@router.get("/source-metrics")
def list_source_metrics(
    approved_status: str | None = None,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    stmt = select(SourceMetric).order_by(SourceMetric.created_at.desc())
    if approved_status:
        stmt = stmt.where(SourceMetric.approved_status == approved_status)
    return {"items": [source_metric_payload(item) for item in db.scalars(stmt).all()]}


@router.patch("/source-metrics/{source_metric_id}/approve")
def approve_source_metric(
    source_metric_id: str,
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    source_metric = get_source_metric(db, source_metric_id)
    if source_metric.approved_status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "source_metric_rejected",
                "message": "Rejected source metrics cannot be approved without re-import.",
            },
        )
    metric_value = publish_source_metric(db, source_metric, claims["sub"])
    source_metric.approved_status = "approved"
    source_metric.reviewed_by_user_id = claims["sub"]
    source_metric.reviewed_at = datetime.now(UTC)
    source_metric.source.status = "approved"
    db.add(
        MetricVersion(
            source_metric_id=source_metric.id,
            metric_value_id=metric_value.id,
            version=next_metric_version(db, source_metric.id),
            value_numeric=source_metric.value_numeric,
            approved_status="approved",
            created_by_user_id=claims["sub"],
        )
    )
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="source_metric.approved",
        target_type="source_metric",
        target_id=source_metric.id,
        metadata={"metric_value_id": metric_value.id, "source_id": source_metric.source_id},
    )
    db.commit()
    db.refresh(source_metric)
    return source_metric_payload(source_metric)


@router.patch("/source-metrics/{source_metric_id}/reject")
def reject_source_metric(
    source_metric_id: str,
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    source_metric = get_source_metric(db, source_metric_id)
    if source_metric.approved_status == "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "source_metric_approved",
                "message": "Approved source metrics cannot be rejected after publication.",
            },
        )
    source_metric.approved_status = "rejected"
    source_metric.reviewed_by_user_id = claims["sub"]
    source_metric.reviewed_at = datetime.now(UTC)
    source_metric.source.status = "rejected"
    db.add(
        MetricVersion(
            source_metric_id=source_metric.id,
            metric_value_id=None,
            version=next_metric_version(db, source_metric.id),
            value_numeric=source_metric.value_numeric,
            approved_status="rejected",
            created_by_user_id=claims["sub"],
        )
    )
    write_audit_log(
        db,
        actor_user_id=claims["sub"],
        action="source_metric.rejected",
        target_type="source_metric",
        target_id=source_metric.id,
        metadata={"source_id": source_metric.source_id},
    )
    db.commit()
    db.refresh(source_metric)
    return source_metric_payload(source_metric)


@router.get("/audit-logs")
def audit_logs(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)).all()
    return {"items": [audit_log_payload(log) for log in logs], "next_cursor": None}


def get_source_metric(db: Session, source_metric_id: str) -> SourceMetric:
    source_metric = db.get(SourceMetric, source_metric_id)
    if not source_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "source_metric_not_found", "message": "Source metric not found."},
        )
    return source_metric


def publish_source_metric(
    db: Session,
    source_metric: SourceMetric,
    actor_user_id: str,
) -> MetricValue:
    definition = get_or_create_metric_definition(db, source_metric.metric_type)
    period_start = date(source_metric.year, 1, 1)
    period_end = date(source_metric.year, 12, 31)
    metric_value = db.scalar(
        select(MetricValue).where(
            MetricValue.metric_definition_id == definition.id,
            MetricValue.entity_type == "company",
            MetricValue.entity_id == source_metric.company_id,
            MetricValue.period_start == period_start,
            MetricValue.period_end == period_end,
        )
    )
    methodology = source_metric.methodology_note
    if metric_value:
        metric_value.value_numeric = source_metric.value_numeric
        metric_value.methodology = methodology
        metric_value.status = "approved"
    else:
        metric_value = MetricValue(
            metric_definition_id=definition.id,
            entity_type="company",
            entity_id=source_metric.company_id,
            period_start=period_start,
            period_end=period_end,
            value_numeric=source_metric.value_numeric,
            currency="usd" if definition.unit == "usd" else None,
            methodology=methodology,
            status="approved",
        )
        db.add(metric_value)
        db.flush()

    link = db.scalar(
        select(MetricSource).where(
            MetricSource.metric_value_id == metric_value.id,
            MetricSource.source_id == source_metric.source_id,
        )
    )
    if not link:
        db.add(
            MetricSource(
                metric_value_id=metric_value.id,
                source_id=source_metric.source_id,
                evidence_note="Approved through APIP admin CSV source workflow.",
            )
        )
        db.flush()

    db.flush()
    links = db.scalars(
        select(MetricSource)
        .where(MetricSource.metric_value_id == metric_value.id)
        .order_by(MetricSource.created_at)
    ).all()
    sources = [metric_source.source for metric_source in links]
    confidence = score_metric_confidence(metric_value, sources)
    confidence_row = metric_value.confidence_score
    if confidence_row:
        confidence_row.source_reliability = confidence.source_reliability
        confidence_row.data_freshness = confidence.data_freshness
        confidence_row.cross_verification = confidence.cross_verification
        confidence_row.methodology_transparency = confidence.methodology_transparency
        confidence_row.confidence_score = confidence.confidence_score
        confidence_row.confidence_label = confidence.confidence_label
        confidence_row.source_count = confidence.source_count
        confidence_row.methodology_note = confidence.methodology_note
    else:
        db.add(
            ConfidenceScore(
                metric_value_id=metric_value.id,
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

    write_audit_log(
        db,
        actor_user_id=actor_user_id,
        action="metric_value.published",
        target_type="metric_value",
        target_id=metric_value.id,
        metadata={
            "source_metric_id": source_metric.id,
            "metric_type": source_metric.metric_type,
            "company_id": source_metric.company_id,
        },
    )
    return metric_value


def get_or_create_metric_definition(db: Session, metric_type: str) -> MetricDefinition:
    definition = db.scalar(select(MetricDefinition).where(MetricDefinition.key == metric_type))
    if definition:
        return definition
    aggregation_method = (
        "sum" if "spend" in metric_type or "revenue" in metric_type else "latest"
    )
    definition = MetricDefinition(
        key=metric_type,
        name=metric_type.replace("_", " ").title(),
        description=f"Financial metric imported from approved APIP source evidence: {metric_type}.",
        unit="ratio" if "roi" in metric_type or "margin" in metric_type else "usd",
        higher_is_better=0 if "spend" in metric_type or "cost" in metric_type else 1,
        aggregation_method=aggregation_method,
    )
    db.add(definition)
    db.flush()
    return definition


def next_metric_version(db: Session, source_metric_id: str) -> int:
    latest = db.scalar(
        select(MetricVersion)
        .where(MetricVersion.source_metric_id == source_metric_id)
        .order_by(MetricVersion.version.desc())
        .limit(1)
    )
    return (latest.version + 1) if latest else 1


def source_metric_payload(source_metric: SourceMetric) -> dict[str, object]:
    return {
        "id": source_metric.id,
        "company": source_metric.company.name,
        "company_id": source_metric.company_id,
        "year": source_metric.year,
        "metric_type": source_metric.metric_type,
        "value": float(source_metric.value_numeric),
        "source_url": source_metric.source_url,
        "source_type": source_metric.source_type,
        "confidence_score": float(source_metric.confidence_score),
        "created_by": source_metric.created_by.full_name,
        "approved_status": source_metric.approved_status,
        "last_updated": source_metric.updated_at.isoformat() if source_metric.updated_at else None,
        "methodology_note": source_metric.methodology_note,
        "source": {
            "id": source_metric.source.id,
            "title": source_metric.source.title,
            "status": source_metric.source.status,
            "reliability_score": source_metric.source.reliability_score,
            "published_at": source_metric.source.published_at.isoformat()
            if source_metric.source.published_at
            else None,
        },
    }


def audit_log_payload(log: AuditLog) -> dict[str, object]:
    return {
        "id": log.id,
        "actor": log.actor.full_name if log.actor else None,
        "actor_user_id": log.actor_user_id,
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "metadata": json.loads(log.metadata_json),
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


def company_payload(company: Company) -> dict[str, object]:
    return {
        "id": company.id,
        "name": company.name,
        "slug": company.slug,
        "ticker": company.ticker,
        "website_url": company.website_url,
        "status": company.status,
    }


def industry_payload(industry: Industry) -> dict[str, object]:
    return {
        "id": industry.id,
        "name": industry.name,
        "slug": industry.slug,
        "status": industry.status,
    }


def country_payload(country: Country) -> dict[str, object]:
    return {
        "id": country.id,
        "name": country.name,
        "slug": country.slug,
        "iso_code": country.iso_code,
        "region": country.region,
    }


def model_payload(model: AIModel) -> dict[str, object]:
    return {
        "id": model.id,
        "name": model.name,
        "slug": model.slug,
        "model_family": model.model_family,
        "provider_company_id": model.provider_company_id,
        "status": model.status,
    }


def source_payload(source: Source) -> dict[str, object]:
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "url": source.url,
        "publisher": source.publisher,
        "published_at": source.published_at.isoformat() if source.published_at else None,
        "reliability_score": source.reliability_score,
        "status": source.status,
    }


def get_or_404(db: Session, model: type, item_id: str, code: str):
    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": code})
    return item


def required_text(payload: dict[str, object], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "validation_failed", "message": f"{key} is required."},
        )
    return value


def optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def update_fields(item: object, payload: dict[str, object], fields: list[str]) -> None:
    for field in fields:
        if field not in payload:
            continue
        value = optional_text(payload[field])
        setattr(item, field, value)


def slugify(value: str) -> str:
    return value.strip().lower().replace(" ", "-").replace("_", "-")


def unique_slug(db: Session, model: type, slug: str) -> str:
    base = slugify(slug)
    candidate = base
    suffix = 2
    while db.scalar(select(model).where(model.slug == candidate)):
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate
