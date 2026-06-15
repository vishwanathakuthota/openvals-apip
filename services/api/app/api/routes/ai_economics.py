from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.domains.ai_economics.service import (
    get_ai_economics_dashboard,
    get_company_intelligence_report,
    list_ai_investment_estimates,
    list_ai_profitability_scores,
    list_ai_revenue_estimates,
)

router = APIRouter()


@router.get("/ai-revenue")
def ai_revenue(
    company_slug: str | None = None,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return _with_company_not_found(lambda: list_ai_revenue_estimates(db, company_slug))


@router.get("/ai-investment")
def ai_investment(
    company_slug: str | None = None,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return _with_company_not_found(lambda: list_ai_investment_estimates(db, company_slug))


@router.get("/ai-profitability")
def ai_profitability(
    company_slug: str | None = None,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return _with_company_not_found(lambda: list_ai_profitability_scores(db, company_slug))


@router.get("/ai-economics")
def ai_economics(
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return get_ai_economics_dashboard(db)


@router.get("/ai-economics/reports/{company_slug}")
def ai_economics_report(
    company_slug: str,
    _: dict[str, str] = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return _with_company_not_found(lambda: get_company_intelligence_report(db, company_slug))


def _with_company_not_found(callback):
    try:
        return callback()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "company_not_found", "message": str(exc)},
        ) from exc
