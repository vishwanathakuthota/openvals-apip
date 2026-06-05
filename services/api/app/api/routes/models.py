from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.db.models import AIModel
from app.domains.metrics.repository import entity_metrics

router = APIRouter()


@router.get("/models")
def list_models(_: dict[str, str] = Depends(require_api_key), db: Session = Depends(get_db)):
    items = db.scalars(
        select(AIModel).where(AIModel.status == "active").order_by(AIModel.name)
    ).all()
    return {"items": [serialize_model(item) for item in items], "next_cursor": None}


@router.get("/models/{model_id}")
def get_model(
    model_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    model = db.get(AIModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail={"code": "model_not_found"})
    return {**serialize_model(model), "metrics": entity_metrics(db, "model", model_id)}


@router.get("/models/{model_id}/metrics")
def get_model_metrics(
    model_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    return {"items": entity_metrics(db, "model", model_id)}


def serialize_model(model: AIModel) -> dict[str, object]:
    return {
        "id": model.id,
        "name": model.name,
        "slug": model.slug,
        "model_family": model.model_family,
        "status": model.status,
    }
