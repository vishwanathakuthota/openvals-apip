from app.db.session import SessionLocal
from app.domains.ingestion.service import run_live_ingestion
from app.workers.celery_app import celery_app


@celery_app.task(name="apip.recalculate_metrics")
def recalculate_metrics() -> dict[str, str]:
    return {"status": "queued_placeholder"}


@celery_app.task(name="apip.ingest_live_data")
def ingest_live_data() -> dict[str, object]:
    print("Starting APIP live data ingestion cycle")
    with SessionLocal() as db:
        result = run_live_ingestion(db)
    print(
        "Completed APIP live data ingestion cycle "
        f"status={result['status']} records_created={result['records_created']}"
    )
    return result
