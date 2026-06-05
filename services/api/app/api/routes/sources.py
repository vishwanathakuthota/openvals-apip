from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.db.models import Source
from app.domains.sources.credibility import source_credibility_score, source_tier

router = APIRouter()


@router.get("/sources")
def list_sources(_: dict[str, str] = Depends(require_api_key), db: Session = Depends(get_db)):
    items = db.scalars(
        select(Source).where(Source.status == "approved").order_by(Source.title)
    ).all()
    return {"items": [serialize_source(item) for item in items], "next_cursor": None}


@router.get("/sources/{source_id}")
def get_source(
    source_id: str, _: dict[str, str] = Depends(require_api_key), db: Session = Depends(get_db)
):
    source = db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail={"code": "source_not_found"})
    return serialize_source(source)


def serialize_source(source: Source) -> dict[str, object]:
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "source_tier": source_tier(source.source_type),
        "url": source.url,
        "publisher": source.publisher,
        "reliability_score": source.reliability_score,
        "credibility_score": source_credibility_score(source.source_type, source.published_at),
        "status": source.status,
    }
