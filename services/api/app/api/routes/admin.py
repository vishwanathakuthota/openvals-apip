from fastapi import APIRouter, Depends

from app.api.deps import require_admin

router = APIRouter()


@router.get("/audit-logs")
def audit_logs(_: str = Depends(require_admin)):
    return {"items": [], "next_cursor": None}


@router.post("/etl-jobs")
def create_etl_job(payload: dict[str, object], _: str = Depends(require_admin)):
    return {
        "id": "job_phase2_placeholder",
        "status": "queued",
        "job_type": payload.get("job_type", "unknown"),
    }


@router.get("/etl-jobs/{job_id}")
def get_etl_job(job_id: str, _: str = Depends(require_admin)):
    return {"id": job_id, "status": "not_started", "events": []}
