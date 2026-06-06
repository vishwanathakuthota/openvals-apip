from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.domains.autonomous_research.service import run_research_agent


@celery_app.task(name="apip.recalculate_metrics")
def recalculate_metrics() -> dict[str, str]:
    return {"status": "queued_placeholder"}


@celery_app.task(name="apip.autonomous_research_agent")
def autonomous_research_agent() -> dict[str, object]:
    with SessionLocal() as db:
        result = run_research_agent(db)
        db.commit()
        return result.__dict__
