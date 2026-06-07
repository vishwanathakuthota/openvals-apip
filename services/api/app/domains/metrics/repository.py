from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ConfidenceScore, MetricDefinition, MetricValue
from app.domains.autonomous_research.service import (
    PUBLISHED,
    openvals_classification,
    public_lineage,
)
from app.domains.sources.credibility import (
    evidence_coverage_score,
    source_credibility_score,
    source_tier,
)
from app.domains.trust_index.service import trust_classification, trust_rating


def confidence_payload(confidence: ConfidenceScore | None) -> dict[str, object] | None:
    if not confidence:
        return None
    return {
        "source_reliability": confidence.source_reliability,
        "data_freshness": confidence.data_freshness,
        "cross_verification": confidence.cross_verification,
        "methodology_transparency": confidence.methodology_transparency,
        "score": float(confidence.confidence_score),
        "label": confidence.confidence_label,
        "source_count": confidence.source_count,
        "last_updated": confidence.updated_at.isoformat() if confidence.updated_at else None,
        "methodology_note": confidence.methodology_note,
    }


def metric_payload(metric: MetricValue) -> dict[str, object]:
    confidence = confidence_payload(metric.confidence_score)
    linked_sources = [link.source for link in metric.source_links]
    coverage = evidence_coverage_score(linked_sources)
    sources = [
        {
            "id": link.source.id,
            "title": link.source.title,
            "source_type": link.source.source_type,
            "source_tier": source_tier(link.source.source_type),
            "credibility_score": source_credibility_score(
                link.source.source_type, link.source.published_at
            ),
            "publisher": link.source.publisher,
            "url": link.source.url,
            "published_at": link.source.published_at.isoformat()
            if link.source.published_at
            else None,
            "reliability_score": link.source.reliability_score,
            "evidence_note": link.evidence_note,
            "lineage": source_lineage_payload(metric, link.source.id),
        }
        for link in metric.source_links
    ]
    published_records = [
        record for record in metric.autonomous_evidence_records if record.status == PUBLISHED
    ]
    lineage = [public_lineage(record) for record in published_records]
    openvals_score = float(metric.openvals_score) if metric.openvals_score is not None else None
    return {
        "id": metric.id,
        "metric_key": metric.metric_definition.key,
        "entity_type": metric.entity_type,
        "entity_id": metric.entity_id,
        "value": float(metric.value_numeric),
        "confidence_score": confidence["score"] if confidence else None,
        "confidence_label": confidence["label"] if confidence else None,
        "source_count": confidence["source_count"] if confidence else 0,
        "coverage_score": coverage.score,
        "evidence_classification": metric.evidence_classification,
        "validation_status": metric.validation_status,
        "openvals_score": openvals_score,
        "openvals_classification": openvals_classification(openvals_score or 0),
        "trust_index": openvals_score,
        "trust_rating": trust_rating(openvals_score or 0),
        "trust_classification": trust_classification(openvals_score or 0),
        "coverage_label": coverage.label,
        "coverage": {
            "score": coverage.score,
            "label": coverage.label,
            "source_count": coverage.source_count,
            "tier_counts": coverage.tier_counts,
            "methodology_note": coverage.methodology_note,
        },
        "last_updated": confidence["last_updated"] if confidence else None,
        "methodology_note": confidence["methodology_note"] if confidence else metric.methodology,
        "unit": metric.metric_definition.unit,
        "currency": metric.currency,
        "period_start": metric.period_start.isoformat(),
        "period_end": metric.period_end.isoformat(),
        "methodology": metric.methodology,
        "confidence": confidence,
        "sources": sources,
        "source_lineage": lineage,
    }


def source_lineage_payload(metric: MetricValue, source_id: str) -> dict[str, object] | None:
    record = next(
        (
            item
            for item in metric.autonomous_evidence_records
            if item.source_id == source_id and item.status == PUBLISHED
        ),
        None,
    )
    if not record:
        return None
    return public_lineage(record)


def list_metric_definitions(db: Session) -> list[dict[str, object]]:
    definitions = db.scalars(select(MetricDefinition).order_by(MetricDefinition.key)).all()
    return [
        {
            "id": item.id,
            "key": item.key,
            "name": item.name,
            "description": item.description,
            "unit": item.unit,
            "higher_is_better": bool(item.higher_is_better),
            "aggregation_method": item.aggregation_method,
        }
        for item in definitions
    ]


def search_metric_values(
    db: Session,
    entity_type: str | None = None,
    entity_id: str | None = None,
    metric_key: str | None = None,
    confidence_min: float | None = None,
) -> list[dict[str, object]]:
    stmt = select(MetricValue).join(MetricDefinition).where(MetricValue.status == "approved")
    if entity_type:
        stmt = stmt.where(MetricValue.entity_type == entity_type)
    if entity_id:
        stmt = stmt.where(MetricValue.entity_id == entity_id)
    if metric_key:
        stmt = stmt.where(MetricDefinition.key == metric_key)
    if confidence_min is not None:
        stmt = stmt.join(ConfidenceScore).where(ConfidenceScore.confidence_score >= confidence_min)
    return [metric_payload(metric) for metric in db.scalars(stmt).all()]


def entity_metrics(db: Session, entity_type: str, entity_id: str) -> list[dict[str, object]]:
    return search_metric_values(db, entity_type=entity_type, entity_id=entity_id)
