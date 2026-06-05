from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Company,
    CompanyValidation,
    CompanyValidationEvidence,
    CompanyValidationSourceReview,
    Source,
)
from app.domains.sources.credibility import (
    evidence_coverage_score,
    source_credibility_score,
    source_tier,
)

APPROVED_STATUSES = {"approved", "verified"}


@dataclass(frozen=True)
class ValidationScores:
    openvals_validation_score: float
    evidence_coverage_score: float
    confidence_score: float
    approved_evidence_ratio: float


def ensure_company_validation(db: Session, company: Company) -> CompanyValidation:
    validation = db.scalar(
        select(CompanyValidation).where(CompanyValidation.company_id == company.id)
    )
    if validation:
        return validation
    validation = CompanyValidation(
        company_id=company.id,
        status="pending",
        openvals_validation_score=0,
        evidence_coverage_score=0,
        confidence_score=0,
    )
    db.add(validation)
    db.flush()
    return validation


def attach_source_evidence(
    db: Session,
    validation: CompanyValidation,
    source: Source,
    evidence_type: str | None = None,
    review_status: str = "pending",
) -> CompanyValidationEvidence:
    existing = db.scalar(
        select(CompanyValidationEvidence).where(
            CompanyValidationEvidence.validation_id == validation.id,
            CompanyValidationEvidence.source_id == source.id,
        )
    )
    if existing:
        return existing
    evidence = CompanyValidationEvidence(
        validation_id=validation.id,
        source_id=source.id,
        evidence_type=evidence_type or source.source_type,
        coverage_weight=coverage_weight_for_source(source),
        review_status=review_status,
    )
    db.add(evidence)
    db.flush()
    return evidence


def ensure_source_review(
    db: Session,
    validation: CompanyValidation,
    source: Source,
    review_status: str = "pending",
) -> CompanyValidationSourceReview:
    existing = db.scalar(
        select(CompanyValidationSourceReview).where(
            CompanyValidationSourceReview.validation_id == validation.id,
            CompanyValidationSourceReview.source_id == source.id,
        )
    )
    if existing:
        return existing
    review = CompanyValidationSourceReview(
        validation_id=validation.id,
        source_id=source.id,
        review_status=review_status,
    )
    db.add(review)
    db.flush()
    return review


def recalculate_company_validation(validation: CompanyValidation) -> ValidationScores:
    evidence_items = list(validation.evidence_items)
    approved_evidence = [
        item for item in evidence_items if item.review_status in APPROVED_STATUSES
    ]
    scored_sources = [item.source for item in approved_evidence] or [
        item.source for item in evidence_items
    ]
    coverage = evidence_coverage_score(scored_sources)
    confidence_score = average(
        [source_credibility_score(item.source.source_type, item.source.published_at) for item in approved_evidence]
    )
    if confidence_score == 0:
        confidence_score = average(
            [source_credibility_score(item.source.source_type, item.source.published_at) for item in evidence_items]
        )
    approved_ratio = (
        len(approved_evidence) / len(evidence_items) if evidence_items else 0
    )
    openvals_score = round(
        (coverage.score * 0.40) + (confidence_score * 0.40) + (approved_ratio * 100 * 0.20),
        2,
    )
    validation.evidence_coverage_score = coverage.score
    validation.confidence_score = round(confidence_score, 2)
    validation.openvals_validation_score = openvals_score
    return ValidationScores(
        openvals_validation_score=openvals_score,
        evidence_coverage_score=float(coverage.score),
        confidence_score=round(confidence_score, 2),
        approved_evidence_ratio=round(approved_ratio, 2),
    )


def review_evidence(
    evidence: CompanyValidationEvidence,
    review_status: str,
    reviewer_notes: str | None,
    reviewer_user_id: str,
) -> None:
    evidence.review_status = normalize_review_status(review_status)
    evidence.reviewer_notes = reviewer_notes
    evidence.reviewed_by_user_id = reviewer_user_id
    evidence.reviewed_at = datetime.now(UTC)


def review_source(
    review: CompanyValidationSourceReview,
    review_status: str,
    reviewer_notes: str | None,
    reviewer_user_id: str,
) -> None:
    review.review_status = normalize_review_status(review_status)
    review.reviewer_notes = reviewer_notes
    review.reviewed_by_user_id = reviewer_user_id
    review.reviewed_at = datetime.now(UTC)


def approve_validation(
    validation: CompanyValidation,
    reviewer_notes: str | None,
    actor_user_id: str,
) -> None:
    validation.status = "approved"
    validation.reviewer_notes = reviewer_notes
    validation.reviewed_by_user_id = actor_user_id
    validation.approved_by_user_id = actor_user_id
    validation.approved_at = datetime.now(UTC)


def reject_validation(
    validation: CompanyValidation,
    reviewer_notes: str | None,
    actor_user_id: str,
) -> None:
    validation.status = "rejected"
    validation.reviewer_notes = reviewer_notes
    validation.reviewed_by_user_id = actor_user_id
    validation.approved_by_user_id = None
    validation.approved_at = None


def validation_label(score: float) -> str:
    if score >= 90:
        return "Validated"
    if score >= 75:
        return "Strong Evidence"
    if score >= 60:
        return "Review Ready"
    if score >= 40:
        return "Evidence Gap"
    return "Insufficient Evidence"


def coverage_weight_for_source(source: Source) -> float:
    return {1: 45, 2: 25, 3: 20, 4: 10}[source_tier(source.source_type)]


def normalize_review_status(review_status: str) -> str:
    normalized = review_status.strip().lower().replace("-", "_")
    if normalized not in {"pending", "approved", "verified", "rejected"}:
        return "pending"
    return normalized


def average(values: list[float]) -> float:
    if not values:
        return 0
    return round(sum(values) / len(values), 2)
