from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AIModel, Company, Country, Industry, MetricDefinition, MetricValue

INDEX_COMPONENTS = {
    "roi": ("roi",),
    "revenue_growth": ("revenue_growth",),
    "margin": ("margin", "net_margin", "gross_margin"),
    "adoption": ("adoption",),
}

REALITY_ENTITY_TYPES = ("company", "industry", "country")


@dataclass(frozen=True)
class RealityIndexRecord:
    entity_type: str
    entity_id: str
    entity_name: str
    score: float
    label: str
    classification: str
    roi: float
    revenue_growth: float
    margin: float
    adoption: float
    confidence_score: float
    source_count: int
    last_updated: str | None
    methodology_note: str


def ai_reality_label(score: float) -> str:
    if score >= 90:
        return "Elite"
    if score >= 70:
        return "Strong"
    if score >= 50:
        return "Emerging"
    if score >= 30:
        return "Speculative"
    return "Cash Burn Zone"


def calculate_ai_reality_index(
    roi: float,
    revenue_growth: float,
    margin: float,
    adoption: float,
) -> dict[str, float | str]:
    score = roi * 0.4 + revenue_growth * 0.3 + margin * 0.2 + adoption * 0.1
    label = ai_reality_label(score)
    return {"score": round(score, 2), "label": label, "classification": label}


def list_ai_reality_indexes(
    db: Session,
    entity_type: str | None = None,
    limit: int = 25,
) -> list[dict[str, object]]:
    entity_types = [entity_type] if entity_type else list(REALITY_ENTITY_TYPES)
    items: list[RealityIndexRecord] = []
    for current_entity_type in entity_types:
        if current_entity_type not in REALITY_ENTITY_TYPES:
            continue
        items.extend(build_entity_type_indexes(db, current_entity_type))
    ranked = sorted(items, key=lambda item: item.score, reverse=True)
    return [reality_index_payload(item) for item in ranked[:limit]]


def build_entity_type_indexes(db: Session, entity_type: str) -> list[RealityIndexRecord]:
    metric_rows = db.scalars(
        select(MetricValue)
        .join(MetricDefinition)
        .where(
            MetricValue.entity_type == entity_type,
            MetricValue.status == "approved",
            MetricDefinition.key.in_(component_metric_keys()),
        )
        .order_by(MetricValue.entity_id, MetricDefinition.key, MetricValue.period_end.desc())
    ).all()
    latest_by_entity: dict[str, dict[str, MetricValue]] = {}
    for metric in metric_rows:
        if not metric.entity_id:
            continue
        component = component_for_metric(metric.metric_definition.key)
        if not component:
            continue
        entity_metrics = latest_by_entity.setdefault(metric.entity_id, {})
        entity_metrics.setdefault(component, metric)

    records: list[RealityIndexRecord] = []
    for entity_id, metrics in latest_by_entity.items():
        if set(metrics) != set(INDEX_COMPONENTS):
            continue
        components = {
            component: normalize_component_score(metric.value_numeric)
            for component, metric in metrics.items()
        }
        index = calculate_ai_reality_index(
            roi=components["roi"],
            revenue_growth=components["revenue_growth"],
            margin=components["margin"],
            adoption=components["adoption"],
        )
        records.append(
            RealityIndexRecord(
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name(db, entity_type, entity_id),
                score=float(index["score"]),
                label=str(index["label"]),
                classification=str(index["classification"]),
                roi=components["roi"],
                revenue_growth=components["revenue_growth"],
                margin=components["margin"],
                adoption=components["adoption"],
                confidence_score=average_confidence(metrics.values()),
                source_count=sum(source_count(metric) for metric in metrics.values()),
                last_updated=latest_update(metrics.values()),
                methodology_note=methodology_note(metrics.values()),
            )
        )
    return records


def component_metric_keys() -> list[str]:
    return [metric_key for keys in INDEX_COMPONENTS.values() for metric_key in keys]


def component_for_metric(metric_key: str) -> str | None:
    for component, keys in INDEX_COMPONENTS.items():
        if metric_key in keys:
            return component
    return None


def normalize_component_score(value: Decimal | float | int) -> float:
    numeric = float(value)
    if numeric <= 2:
        numeric *= 100
    return round(min(max(numeric, 0), 100), 2)


def average_confidence(metrics: object) -> float:
    scores = [
        float(metric.confidence_score.confidence_score)
        for metric in metrics
        if metric.confidence_score is not None
    ]
    if not scores:
        return 0
    return round(sum(scores) / len(scores), 2)


def source_count(metric: MetricValue) -> int:
    if metric.confidence_score:
        return metric.confidence_score.source_count
    return len(metric.source_links)


def latest_update(metrics: object) -> str | None:
    dates: list[datetime] = []
    for metric in metrics:
        if metric.confidence_score and metric.confidence_score.updated_at:
            dates.append(metric.confidence_score.updated_at)
        elif metric.updated_at:
            dates.append(metric.updated_at)
    if not dates:
        return None
    return max(dates).isoformat()


def methodology_note(metrics: object) -> str:
    source_total = sum(source_count(metric) for metric in metrics)
    return (
        "AI Reality Index is calculated from approved ROI, revenue growth, margin, "
        f"and adoption metrics with {source_total} linked source records."
    )


def entity_name(db: Session, entity_type: str, entity_id: str) -> str:
    model_by_type = {
        "company": Company,
        "industry": Industry,
        "country": Country,
        "model": AIModel,
    }
    model = model_by_type.get(entity_type)
    if not model:
        return entity_id
    entity = db.get(model, entity_id)
    return entity.name if entity else entity_id


def reality_index_payload(record: RealityIndexRecord) -> dict[str, object]:
    return {
        "entity_type": record.entity_type,
        "entity_id": record.entity_id,
        "entity_name": record.entity_name,
        "score": record.score,
        "label": record.label,
        "classification": record.classification,
        "components": {
            "roi": record.roi,
            "revenue_growth": record.revenue_growth,
            "margin": record.margin,
            "adoption": record.adoption,
        },
        "confidence": {
            "score": record.confidence_score,
            "label": confidence_label(record.confidence_score),
            "source_count": record.source_count,
            "last_updated": record.last_updated,
            "methodology_note": record.methodology_note,
        },
        "confidence_score": record.confidence_score,
        "source_count": record.source_count,
        "last_updated": record.last_updated,
        "methodology_note": record.methodology_note,
    }


def confidence_label(score: float) -> str:
    if score >= 90:
        return "Verified"
    if score >= 75:
        return "High Confidence"
    if score >= 60:
        return "Medium Confidence"
    if score >= 40:
        return "Low Confidence"
    return "Speculative"
