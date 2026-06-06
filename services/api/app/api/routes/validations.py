from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.db.models import CompanyValidation
from app.domains.sources.credibility import source_credibility_score, source_tier
from app.domains.validation.service import validation_label

router = APIRouter()


@router.get("/company-validations")
def list_company_validations(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    validations = db.scalars(select(CompanyValidation).order_by(CompanyValidation.created_at)).all()
    return {
        "items": [company_validation_payload(item) for item in validations],
        "next_cursor": None,
    }


@router.get("/company-validations/{validation_id}")
def get_company_validation(
    validation_id: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    validation = db.get(CompanyValidation, validation_id)
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "company_validation_not_found"},
        )
    return company_validation_payload(validation)


def company_validation_payload(validation: CompanyValidation) -> dict[str, object]:
    score = float(validation.openvals_validation_score)
    evidence = [
        {
            "id": item.id,
            "evidence_type": item.evidence_type,
            "coverage_weight": float(item.coverage_weight),
            "review_status": item.review_status,
            "reviewer_notes": item.reviewer_notes,
            "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
            "source": {
                "id": item.source.id,
                "title": item.source.title,
                "source_type": item.source.source_type,
                "source_tier": source_tier(item.source.source_type),
                "credibility_score": source_credibility_score(
                    item.source.source_type, item.source.published_at
                ),
                "publisher": item.source.publisher,
                "url": item.source.url,
                "published_at": item.source.published_at.isoformat()
                if item.source.published_at
                else None,
                "reliability_score": item.source.reliability_score,
                "status": item.source.status,
            },
        }
        for item in validation.evidence_items
    ]
    source_reviews = [
        {
            "id": review.id,
            "source_id": review.source_id,
            "source_title": review.source.title,
            "review_status": review.review_status,
            "reviewer_notes": review.reviewer_notes,
            "reviewed_by": review.reviewed_by.full_name if review.reviewed_by else None,
            "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
        }
        for review in validation.source_reviews
    ]
    return {
        "id": validation.id,
        "company_id": validation.company_id,
        "company": validation.company.name,
        "status": validation.status,
        "openvals_validation_score": score,
        "openvals_validation_label": validation_label(score),
        "evidence_coverage_score": float(validation.evidence_coverage_score),
        "confidence_score": float(validation.confidence_score),
        "reviewer_notes": validation.reviewer_notes,
        "reviewed_by": validation.reviewed_by.full_name if validation.reviewed_by else None,
        "approved_by": validation.approved_by.full_name if validation.approved_by else None,
        "approved_at": validation.approved_at.isoformat() if validation.approved_at else None,
        "last_updated": validation.updated_at.isoformat() if validation.updated_at else None,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "source_reviews": source_reviews,
    }
