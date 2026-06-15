from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.domains.ingestion.service import ingestion_status

router = APIRouter()


@router.get("/ingestion/status")
def get_ingestion_status(db: Session = Depends(get_db)) -> dict[str, object]:
    return ingestion_status(db)
