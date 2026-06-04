from app.workers.celery_app import celery_app


@celery_app.task(name="apip.recalculate_metrics")
def recalculate_metrics() -> dict[str, str]:
    return {"status": "queued_placeholder"}
