from fastapi import APIRouter
from sqlalchemy import text

from app.core.redis_client import redis_client
from app.db.session import SessionLocal

router = APIRouter()


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def ready() -> dict[str, object]:
    return readiness_payload()


@router.get("/api/v1/health")
def api_v1_health() -> dict[str, object]:
    return readiness_payload()


def readiness_payload() -> dict[str, object]:
    checks = {"api": "ok", "postgres": "ok", "redis": "ok"}
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        checks["postgres"] = "unavailable"
    try:
        redis_client().ping()
    except Exception:
        checks["redis"] = "unavailable"
    return {
        "status": "ok" if all(value == "ok" for value in checks.values()) else "degraded",
        "checks": checks,
    }
