from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.domains.indexes.service import list_ai_reality_indexes
from app.domains.metrics.service import get_scoreboard

router = APIRouter()


@router.get("/scoreboard")
def scoreboard(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return get_scoreboard(db)


@router.get("/ai-reality-index")
def ai_reality_index(
    entity_type: str | None = None,
    limit: int = 25,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return {"items": list_ai_reality_indexes(db, entity_type=entity_type, limit=limit)}
