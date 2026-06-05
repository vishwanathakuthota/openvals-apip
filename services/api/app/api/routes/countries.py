from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.db.models import Country
from app.domains.metrics.repository import entity_metrics

router = APIRouter()


@router.get("/countries")
def list_countries(_: dict[str, str] = Depends(require_api_key), db: Session = Depends(get_db)):
    items = db.scalars(select(Country).order_by(Country.name)).all()
    return {"items": [serialize_country(item) for item in items], "next_cursor": None}


@router.get("/countries/{country_id}")
def get_country(
    country_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    country = db.get(Country, country_id)
    if not country:
        raise HTTPException(status_code=404, detail={"code": "country_not_found"})
    return {**serialize_country(country), "metrics": entity_metrics(db, "country", country_id)}


@router.get("/countries/{country_id}/metrics")
def get_country_metrics(
    country_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    return {"items": entity_metrics(db, "country", country_id)}


def serialize_country(country: Country) -> dict[str, object]:
    return {
        "id": country.id,
        "name": country.name,
        "slug": country.slug,
        "iso_code": country.iso_code,
        "region": country.region,
    }
