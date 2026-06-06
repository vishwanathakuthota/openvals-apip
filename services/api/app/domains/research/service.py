import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Company,
    CompanyValidation,
    ResearchAuditTrail,
    ResearchEvidence,
    ResearchQueueItem,
    Source,
)
from app.domains.sources.credibility import evidence_coverage_score, source_credibility_score

RESEARCH_STATUSES = {
    "not_started": "Not Started",
    "researching": "Researching",
    "evidence_collected": "Evidence Collected",
    "under_review": "Under Review",
    "approved": "Approved",
    "published": "Published",
}

STATUS_PROGRESS = {
    "not_started": 0,
    "researching": 25,
    "evidence_collected": 50,
    "under_review": 75,
    "approved": 90,
    "published": 100,
}

APPROVED_EVIDENCE_STATUSES = {"approved", "verified"}


@dataclass(frozen=True)
class ResearchProgressMetrics:
    total_items: int
    status_counts: dict[str, int]
    assigned_items: int
    unassigned_items: int
    average_progress_percent: float
    average_evidence_coverage_score: float
    collected_evidence_count: int
    approved_evidence_count: int


def ensure_research_queue_item(
    db: Session,
    company: Company,
    validation: CompanyValidation | None = None,
) -> ResearchQueueItem:
    item = db.scalar(select(ResearchQueueItem).where(ResearchQueueItem.company_id == company.id))
    if item:
        return item
    item = ResearchQueueItem(
        company_id=company.id,
        validation_id=validation.id if validation else None,
        status="not_started",
        priority="normal",
        progress_percent=0,
        evidence_coverage_score=0,
        notes="Initial research queue item created for APIP beta operations.",
    )
    db.add(item)
    db.flush()
    return item


def assign_research(
    item: ResearchQueueItem,
    assigned_to_user_id: str | None,
    reviewer_user_id: str | None,
    notes: str | None = None,
) -> None:
    item.assigned_to_user_id = assigned_to_user_id
    item.reviewer_user_id = reviewer_user_id
    if notes:
        item.notes = notes


def update_research_status(item: ResearchQueueItem, status: str, notes: str | None = None) -> None:
    item.status = normalize_research_status(status)
    item.progress_percent = STATUS_PROGRESS[item.status]
    if notes:
        item.notes = notes


def collect_research_evidence(
    db: Session,
    item: ResearchQueueItem,
    source: Source,
    collected_by_user_id: str | None,
    evidence_type: str | None = None,
) -> ResearchEvidence:
    existing = db.scalar(
        select(ResearchEvidence).where(
            ResearchEvidence.queue_item_id == item.id,
            ResearchEvidence.source_id == source.id,
        )
    )
    if existing:
        return existing
    evidence = ResearchEvidence(
        queue_item_id=item.id,
        source_id=source.id,
        evidence_type=evidence_type or source.source_type,
        collection_status="collected",
        approval_status="pending",
        coverage_score=source_credibility_score(source.source_type, source.published_at),
        collected_by_user_id=collected_by_user_id,
        collected_at=datetime.now(UTC),
    )
    db.add(evidence)
    db.flush()
    recalculate_research_progress(item)
    return evidence


def review_research_evidence(
    evidence: ResearchEvidence,
    approval_status: str,
    reviewer_user_id: str,
    reviewer_notes: str | None = None,
) -> None:
    evidence.approval_status = normalize_evidence_status(approval_status)
    evidence.reviewer_user_id = reviewer_user_id
    evidence.reviewer_notes = reviewer_notes
    evidence.reviewed_at = datetime.now(UTC)
    recalculate_research_progress(evidence.queue_item)


def recalculate_research_progress(item: ResearchQueueItem) -> None:
    evidence_sources = [
        evidence.source
        for evidence in item.evidence_items
        if evidence.approval_status in APPROVED_EVIDENCE_STATUSES
    ] or [evidence.source for evidence in item.evidence_items]
    coverage = evidence_coverage_score(evidence_sources)
    item.evidence_coverage_score = coverage.score
    base_progress = STATUS_PROGRESS.get(item.status, 0)
    evidence_bonus = min(len(item.evidence_items) * 5, 15)
    approval_bonus = min(
        len(
            [
                evidence
                for evidence in item.evidence_items
                if evidence.approval_status in APPROVED_EVIDENCE_STATUSES
            ]
        )
        * 5,
        15,
    )
    item.progress_percent = min(
        100, max(base_progress, base_progress + evidence_bonus + approval_bonus)
    )


def research_progress_metrics(items: list[ResearchQueueItem]) -> ResearchProgressMetrics:
    status_counts = {label: 0 for label in RESEARCH_STATUSES.values()}
    collected_evidence = 0
    approved_evidence = 0
    for item in items:
        status_counts[status_label(item.status)] += 1
        collected_evidence += len(item.evidence_items)
        approved_evidence += len(
            [
                evidence
                for evidence in item.evidence_items
                if evidence.approval_status in APPROVED_EVIDENCE_STATUSES
            ]
        )
    total = len(items)
    assigned = len([item for item in items if item.assigned_to_user_id])
    return ResearchProgressMetrics(
        total_items=total,
        status_counts=status_counts,
        assigned_items=assigned,
        unassigned_items=total - assigned,
        average_progress_percent=average([float(item.progress_percent) for item in items]),
        average_evidence_coverage_score=average(
            [float(item.evidence_coverage_score) for item in items]
        ),
        collected_evidence_count=collected_evidence,
        approved_evidence_count=approved_evidence,
    )


def write_research_audit(
    db: Session,
    queue_item_id: str | None,
    actor_user_id: str | None,
    action: str,
    from_status: str | None = None,
    to_status: str | None = None,
    notes: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        ResearchAuditTrail(
            queue_item_id=queue_item_id,
            actor_user_id=actor_user_id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            notes=notes,
            metadata_json=json.dumps(metadata or {}, sort_keys=True),
        )
    )


def normalize_research_status(status: str) -> str:
    normalized = status.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized not in RESEARCH_STATUSES:
        return "not_started"
    return normalized


def normalize_evidence_status(status: str) -> str:
    normalized = status.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized not in {"pending", "approved", "verified", "rejected"}:
        return "pending"
    return normalized


def status_label(status: str) -> str:
    return RESEARCH_STATUSES.get(status, "Not Started")


def average(values: list[float]) -> float:
    if not values:
        return 0
    return round(sum(values) / len(values), 2)
