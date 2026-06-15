from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "apip",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.timezone = "UTC"
celery_app.conf.imports = ("app.workers.tasks",)
celery_app.conf.beat_schedule = {
    "live-data-ingestion-every-30-minutes": {
        "task": "apip.ingest_live_data",
        "schedule": settings.ingestion_interval_minutes * 60,
    }
}
