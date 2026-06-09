from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.domains.etl.csv_importer import write_audit_log

router = APIRouter()


@router.post("/public-beta/signups", status_code=status.HTTP_202_ACCEPTED)
def public_beta_signup(
    payload: dict[str, object],
    db: Session = Depends(get_db),
) -> dict[str, object]:
    email = required_text(payload, "email").lower()
    submission_type = optional_text(payload.get("submission_type")) or "waitlist"
    if submission_type not in {"waitlist", "enterprise"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_submission_type",
                "message": "submission_type must be waitlist or enterprise.",
            },
        )
    metadata = {
        "email": email,
        "name": optional_text(payload.get("name")),
        "organization": optional_text(payload.get("organization")),
        "role": optional_text(payload.get("role")),
        "interest": optional_text(payload.get("interest")),
        "submission_type": submission_type,
    }
    write_audit_log(
        db,
        actor_user_id=None,
        action=f"public_beta.{submission_type}.created",
        target_type="public_beta_submission",
        target_id=None,
        metadata=metadata,
    )
    db.commit()
    return {
        "status": "accepted",
        "submission_type": submission_type,
        "message": "Thanks. The OpenVals team received your APIP beta request.",
    }


def required_text(payload: dict[str, object], key: str) -> str:
    value = optional_text(payload.get(key))
    if not value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "validation_failed", "message": f"{key} is required."},
        )
    return value


def optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
