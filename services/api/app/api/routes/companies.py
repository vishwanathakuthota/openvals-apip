from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.db.models import Company
from app.domains.metrics.repository import entity_metrics

router = APIRouter()


@router.get("/companies")
def list_companies(
    q: str | None = None,
    limit: int = 50,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    stmt = select(Company).where(Company.status == "active").order_by(Company.name).limit(limit)
    if q:
        stmt = stmt.where(Company.name.ilike(f"%{q}%"))
    items = db.scalars(stmt).all()
    return {"items": [serialize_company(item) for item in items], "next_cursor": None}


@router.get("/companies/{company_id}")
def get_company(
    company_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail={"code": "company_not_found"})
    return {**serialize_company(company), "metrics": entity_metrics(db, "company", company_id)}


@router.get("/companies/{company_id}/metrics")
def get_company_metrics(
    company_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    return {"items": entity_metrics(db, "company", company_id)}


def serialize_company(company: Company) -> dict[str, object]:
    return {
        "id": company.id,
        "name": company.name,
        "slug": company.slug,
        "ticker": company.ticker,
        "website_url": company.website_url,
        "status": company.status,
    }
