from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ConfidenceScore, MetricDefinition, MetricValue


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
    }


def metric_payload(metric: MetricValue) -> dict[str, object]:
    return {
        "id": metric.id,
        "metric_key": metric.metric_definition.key,
        "entity_type": metric.entity_type,
        "entity_id": metric.entity_id,
        "value": float(metric.value_numeric),
        "unit": metric.metric_definition.unit,
        "currency": metric.currency,
        "period_start": metric.period_start.isoformat(),
        "period_end": metric.period_end.isoformat(),
        "methodology": metric.methodology,
        "confidence": confidence_payload(metric.confidence_score),
    }


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
