from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_jwt
from app.domains.metrics.service import get_scoreboard

router = APIRouter()


@router.get("/scoreboard")
def scoreboard(
    _: dict[str, str] = Depends(require_jwt),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    # Phase 2 keeps this aggregate deterministic; persistence-backed rollups come next.
    return get_scoreboard()


@router.get("/ai-reality-index")
def ai_reality_index(
    entity_type: str | None = None,
    limit: int = 25,
    _: dict[str, str] = Depends(require_jwt),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    del db
    scoreboard_data = get_scoreboard()
    items = scoreboard_data["top_ai_reality_index"]
    if entity_type:
        items = [item for item in items if item["entity_type"] == entity_type]
    return {"items": items[:limit]}
