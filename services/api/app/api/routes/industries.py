from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.db.models import Industry
from app.domains.metrics.repository import entity_metrics

router = APIRouter()


@router.get("/industries")
def list_industries(_: dict[str, str] = Depends(require_api_key), db: Session = Depends(get_db)):
    items = db.scalars(
        select(Industry).where(Industry.status == "active").order_by(Industry.name)
    ).all()
    return {"items": [serialize_industry(item) for item in items], "next_cursor": None}


@router.get("/industries/{industry_id}")
def get_industry(
    industry_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    industry = db.get(Industry, industry_id)
    if not industry:
        raise HTTPException(status_code=404, detail={"code": "industry_not_found"})
    return {**serialize_industry(industry), "metrics": entity_metrics(db, "industry", industry_id)}


@router.get("/industries/{industry_id}/metrics")
def get_industry_metrics(
    industry_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    return {"items": entity_metrics(db, "industry", industry_id)}


def serialize_industry(industry: Industry) -> dict[str, object]:
    return {
        "id": industry.id,
        "name": industry.name,
        "slug": industry.slug,
        "status": industry.status,
    }
