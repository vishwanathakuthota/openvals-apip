from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_jwt
from app.domains.metrics.repository import list_metric_definitions, search_metric_values

router = APIRouter()


@router.get("/metrics")
def list_metrics(_: dict[str, str] = Depends(require_jwt), db: Session = Depends(get_db)):
    return {"items": list_metric_definitions(db)}


@router.get("/metrics/search")
def search(
    entity_type: str | None = None,
    entity_id: str | None = None,
    metric_key: str | None = None,
    confidence_min: float | None = None,
    _: dict[str, str] = Depends(require_jwt),
    db: Session = Depends(get_db),
):
    return {
        "items": search_metric_values(
            db,
            entity_type=entity_type,
            entity_id=entity_id,
            metric_key=metric_key,
            confidence_min=confidence_min,
        )
    }
