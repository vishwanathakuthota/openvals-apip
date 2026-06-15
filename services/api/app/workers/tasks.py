from app.db.session import SessionLocal
from app.domains.data_acquisition.service import refresh_realtime_company_metrics
from app.workers.celery_app import celery_app


@celery_app.task(name="apip.recalculate_metrics")
def recalculate_metrics() -> dict[str, str]:
    return {"status": "queued_placeholder"}


@celery_app.task(name="apip.refresh_company_metrics")
def refresh_company_metrics() -> dict[str, object]:
    db = SessionLocal()
    try:
        return refresh_realtime_company_metrics(db)
    finally:
        db.close()
