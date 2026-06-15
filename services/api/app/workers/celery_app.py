from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "apip",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.beat_schedule = {
    "refresh-company-metrics-every-30-minutes": {
        "task": "apip.refresh_company_metrics",
        "schedule": 30 * 60,
    }
}
