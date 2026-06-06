from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.db.models import CompanyValidationWorkspace
from app.domains.microsoft_validation.service import (
    MICROSOFT_WORKSPACE_SLUG,
    ensure_microsoft_validation_workspace,
    microsoft_validation_report_payload,
)

router = APIRouter()


@router.get("/companies/microsoft/validation-report")
def get_microsoft_validation_report(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    workspace = db.scalar(
        select(CompanyValidationWorkspace).where(
            CompanyValidationWorkspace.slug == MICROSOFT_WORKSPACE_SLUG
        )
    )
    if not workspace:
        workspace = ensure_microsoft_validation_workspace(db)
        db.commit()
    return microsoft_validation_report_payload(workspace)


@router.get("/company-validation-workspaces/{company_slug}")
def get_company_validation_workspace(
    company_slug: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if company_slug != MICROSOFT_WORKSPACE_SLUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "validation_workspace_not_found"},
        )
    workspace = db.scalar(
        select(CompanyValidationWorkspace).where(CompanyValidationWorkspace.slug == company_slug)
    )
    if not workspace:
        workspace = ensure_microsoft_validation_workspace(db)
        db.commit()
    return microsoft_validation_report_payload(workspace)
