from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin, require_api_key
from app.db.models import AutonomousEvidenceRecord
from app.domains.autonomous_research.service import (
    APPROVED,
    PUBLISHED,
    UNDER_REVIEW,
    approve_evidence_record,
    company_openvals_score_payload,
    company_pilot_payload,
    evidence_record_payload,
    microsoft_evidence_records,
    nvidia_evidence_records,
    reject_evidence_record,
    request_additional_evidence,
    run_approval_agent,
    run_microsoft_pilot_validation,
    run_nvidia_gold_standard_validation,
    run_publisher_agent,
    run_research_agent,
    run_validation_agent,
    trust_center_payload,
    write_agent_audit,
)

router = APIRouter()


@router.get("/trust-center")
def public_trust_center(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = list_records(db)
    return {
        "workflow": "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH",
        "auto_publish_enabled": False,
        "metrics": trust_center_payload(records),
        "items": [evidence_record_payload(record) for record in records],
    }


@router.get("/evidence-timeline")
def public_evidence_timeline(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = db.scalars(
        select(AutonomousEvidenceRecord).order_by(
            AutonomousEvidenceRecord.collection_timestamp.desc()
        )
    ).all()
    return {"items": [evidence_record_payload(record) for record in records], "next_cursor": None}


@router.get("/source-lineage")
def public_source_lineage(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = db.scalars(
        select(AutonomousEvidenceRecord)
        .where(AutonomousEvidenceRecord.status == PUBLISHED)
        .order_by(AutonomousEvidenceRecord.published_at.desc())
    ).all()
    return {
        "items": [evidence_record_payload(record)["lineage"] for record in records],
        "next_cursor": None,
    }


@router.get("/companies/microsoft/evidence-timeline")
def microsoft_evidence_timeline(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = microsoft_evidence_records(db)
    return {"items": [evidence_record_payload(record) for record in records], "next_cursor": None}


@router.get("/companies/microsoft/source-lineage")
def microsoft_source_lineage(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = [record for record in microsoft_evidence_records(db) if record.status == PUBLISHED]
    return {
        "company": "Microsoft",
        "items": [evidence_record_payload(record)["lineage"] for record in records],
        "next_cursor": None,
    }


@router.get("/companies/microsoft/openvals-score")
def microsoft_openvals_score(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return company_openvals_score_payload(db, "microsoft")


@router.get("/companies/microsoft/trust-report")
def microsoft_trust_report(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return company_pilot_payload(db, "microsoft")


@router.get("/companies/nvidia/evidence-timeline")
def nvidia_evidence_timeline(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = nvidia_evidence_records(db)
    return {"items": [evidence_record_payload(record) for record in records], "next_cursor": None}


@router.get("/companies/nvidia/source-lineage")
def nvidia_source_lineage(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = [record for record in nvidia_evidence_records(db) if record.status == PUBLISHED]
    return {
        "company": "NVIDIA",
        "items": [evidence_record_payload(record)["lineage"] for record in records],
        "next_cursor": None,
    }


@router.get("/companies/nvidia/openvals-score")
def nvidia_openvals_score(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return company_openvals_score_payload(db, "nvidia")


@router.get("/companies/nvidia/trust-report")
def nvidia_trust_report(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return company_pilot_payload(db, "nvidia")


@router.get("/research-queue")
def public_research_queue(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return queue_payload(db, "Research Queue", "Collected")


@router.get("/validation-queue")
def public_validation_queue(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return queue_payload(db, "Validation Queue", UNDER_REVIEW)


@router.get("/approval-queue")
def public_approval_queue(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = db.scalars(
        select(AutonomousEvidenceRecord)
        .where(AutonomousEvidenceRecord.status == UNDER_REVIEW)
        .order_by(AutonomousEvidenceRecord.validation_timestamp.desc())
    ).all()
    return {
        "queue": "Approval Queue",
        "items": [evidence_record_payload(record) for record in records],
    }


@router.get("/publishing-queue")
def public_publishing_queue(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return queue_payload(db, "Publishing Queue", APPROVED)


@router.get("/admin/autonomous-research")
def admin_autonomous_research_dashboard(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    records = list_records(db)
    return {
        "workflow": "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH",
        "auto_publish_enabled": False,
        "research_queue": [
            evidence_record_payload(record) for record in records if record.status == "Collected"
        ],
        "validation_queue": [
            evidence_record_payload(record) for record in records if record.status == UNDER_REVIEW
        ],
        "approval_queue": [
            evidence_record_payload(record)
            for record in records
            if record.status == UNDER_REVIEW and record.approval_recommendation
        ],
        "publishing_queue": [
            evidence_record_payload(record) for record in records if record.status == APPROVED
        ],
        "evidence_timeline": [evidence_record_payload(record) for record in records],
        "source_lineage": [
            evidence_record_payload(record)["lineage"]
            for record in records
            if record.status == PUBLISHED
        ],
        "trust_center": trust_center_payload(records),
    }


@router.post("/admin/autonomous-research/run/{agent_name}")
def admin_run_autonomous_agent(
    agent_name: str,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    normalized = agent_name.strip().lower().replace("-", "_")
    if normalized == "research":
        result = run_research_agent(db)
    elif normalized == "validation":
        result = run_validation_agent(db)
    elif normalized == "approval":
        result = run_approval_agent(db)
    elif normalized == "publisher":
        result = run_publisher_agent(db)
    elif normalized == "all":
        results = [
            run_research_agent(db),
            run_validation_agent(db),
            run_approval_agent(db),
            run_publisher_agent(db),
        ]
        db.commit()
        return {"items": [result.__dict__ for result in results]}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "unknown_agent"},
        )
    db.commit()
    return result.__dict__


@router.post("/admin/microsoft-pilot-validation/run")
def admin_run_microsoft_pilot_validation(
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    result = run_microsoft_pilot_validation(db, reviewer_user_id=claims["sub"])
    db.commit()
    return result


@router.post("/admin/nvidia-gold-standard/run")
def admin_run_nvidia_gold_standard_validation(
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    result = run_nvidia_gold_standard_validation(db, reviewer_user_id=claims["sub"])
    db.commit()
    return result


@router.patch("/admin/autonomous-research/evidence/{record_id}/review")
def admin_review_autonomous_evidence(
    record_id: str,
    payload: dict[str, object],
    claims: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    record = db.get(AutonomousEvidenceRecord, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "autonomous_evidence_not_found"},
        )
    decision = str(payload.get("decision") or "").strip().lower().replace("-", "_")
    notes = optional_text(payload.get("notes"))
    confidence_score = payload.get("confidence_score")
    if decision == "approve":
        approve_evidence_record(
            record,
            reviewer_user_id=claims["sub"],
            notes=notes,
            confidence_score=float(confidence_score) if confidence_score is not None else None,
        )
    elif decision == "reject":
        reject_evidence_record(record, reviewer_user_id=claims["sub"], notes=notes)
    elif decision == "request_additional_evidence":
        request_additional_evidence(record, reviewer_user_id=claims["sub"], notes=notes)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "invalid_reviewer_decision"},
        )
    write_agent_audit(
        db,
        action="autonomous_research.reviewed",
        record=record,
        metadata={"decision": record.reviewer_decision, "notes": notes},
    )
    db.commit()
    return evidence_record_payload(record)


def queue_payload(db: Session, name: str, status_value: str) -> dict[str, object]:
    records = db.scalars(
        select(AutonomousEvidenceRecord)
        .where(AutonomousEvidenceRecord.status == status_value)
        .order_by(AutonomousEvidenceRecord.updated_at.desc())
    ).all()
    return {"queue": name, "items": [evidence_record_payload(record) for record in records]}


def list_records(db: Session) -> list[AutonomousEvidenceRecord]:
    return db.scalars(
        select(AutonomousEvidenceRecord).order_by(AutonomousEvidenceRecord.updated_at.desc())
    ).all()


def optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
