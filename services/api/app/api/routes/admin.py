import json
from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.db.models import (
    AuditLog,
    ConfidenceScore,
    MetricDefinition,
    MetricSource,
    MetricValue,
    MetricVersion,
    SourceMetric,
)
from app.domains.confidence.service import score_metric_confidence
from app.domains.etl.csv_importer import import_financial_metrics_csv, write_audit_log

router = APIRouter()


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
