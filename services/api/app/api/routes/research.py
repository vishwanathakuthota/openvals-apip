import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.db.models import ResearchAuditTrail, ResearchEvidence, ResearchQueueItem
from app.domains.research.service import research_progress_metrics, status_label
from app.domains.sources.credibility import source_credibility_score, source_tier

router = APIRouter()


@router.get("/research-operations")
def research_operations_dashboard(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items = db.scalars(select(ResearchQueueItem).order_by(ResearchQueueItem.created_at)).all()
    return {
        "items": [research_queue_payload(item) for item in items],
        "metrics": progress_metrics_payload(items),
        "next_cursor": None,
    }


@router.get("/research-operations/{queue_item_id}")
def get_research_queue_item(
    queue_item_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    item = db.get(ResearchQueueItem, queue_item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "research_queue_item_not_found"},
        )
    return research_queue_payload(item)


def progress_metrics_payload(items: list[ResearchQueueItem]) -> dict[str, object]:
    metrics = research_progress_metrics(items)
    return {
        "total_items": metrics.total_items,
        "status_counts": metrics.status_counts,
        "assigned_items": metrics.assigned_items,
        "unassigned_items": metrics.unassigned_items,
        "average_progress_percent": metrics.average_progress_percent,
        "average_evidence_coverage_score": metrics.average_evidence_coverage_score,
        "collected_evidence_count": metrics.collected_evidence_count,
        "approved_evidence_count": metrics.approved_evidence_count,
    }


def research_queue_payload(item: ResearchQueueItem) -> dict[str, object]:
    return {
        "id": item.id,
        "company_id": item.company_id,
        "company": item.company.name,
        "validation_id": item.validation_id,
        "status": status_label(item.status),
        "status_key": item.status,
        "priority": item.priority,
        "assigned_to": item.assigned_to.full_name if item.assigned_to else None,
        "assigned_to_user_id": item.assigned_to_user_id,
        "reviewer": item.reviewer.full_name if item.reviewer else None,
        "reviewer_user_id": item.reviewer_user_id,
        "progress_percent": float(item.progress_percent),
        "evidence_coverage_score": float(item.evidence_coverage_score),
        "notes": item.notes,
        "last_updated": item.updated_at.isoformat() if item.updated_at else None,
        "evidence_count": len(item.evidence_items),
        "evidence": [research_evidence_payload(evidence) for evidence in item.evidence_items],
    }


def research_evidence_payload(evidence: ResearchEvidence) -> dict[str, object]:
    return {
        "id": evidence.id,
        "evidence_type": evidence.evidence_type,
        "collection_status": evidence.collection_status,
        "approval_status": evidence.approval_status,
        "coverage_score": float(evidence.coverage_score),
        "collected_by": evidence.collected_by.full_name if evidence.collected_by else None,
        "reviewer": evidence.reviewer.full_name if evidence.reviewer else None,
        "reviewer_notes": evidence.reviewer_notes,
        "collected_at": evidence.collected_at.isoformat() if evidence.collected_at else None,
        "reviewed_at": evidence.reviewed_at.isoformat() if evidence.reviewed_at else None,
        "source": {
            "id": evidence.source.id,
            "title": evidence.source.title,
            "source_type": evidence.source.source_type,
            "source_tier": source_tier(evidence.source.source_type),
            "credibility_score": source_credibility_score(
                evidence.source.source_type, evidence.source.published_at
            ),
            "publisher": evidence.source.publisher,
            "url": evidence.source.url,
            "published_at": evidence.source.published_at.isoformat()
            if evidence.source.published_at
            else None,
            "status": evidence.source.status,
        },
    }


def research_audit_payload(audit: ResearchAuditTrail) -> dict[str, object]:
    return {
        "id": audit.id,
        "queue_item_id": audit.queue_item_id,
        "actor": audit.actor.full_name if audit.actor else None,
        "action": audit.action,
        "from_status": status_label(audit.from_status) if audit.from_status else None,
        "to_status": status_label(audit.to_status) if audit.to_status else None,
        "notes": audit.notes,
        "metadata": json.loads(audit.metadata_json or "{}"),
        "created_at": audit.created_at.isoformat() if audit.created_at else None,
    }
