from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_jwt
from app.db.models import MetricValue
from app.domains.metrics.repository import confidence_payload

router = APIRouter()


@router.get("/confidence/{metric_value_id}")
def get_confidence(
    metric_value_id: str,
    _: dict[str, str] = Depends(require_jwt),
    db: Session = Depends(get_db),
):
    metric = db.get(MetricValue, metric_value_id)
    if not metric:
        raise HTTPException(status_code=404, detail={"code": "metric_value_not_found"})
    return confidence_payload(metric.confidence_score)
