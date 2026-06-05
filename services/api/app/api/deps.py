from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_access_token
from app.db.session import SessionLocal
from app.domains.identity.api_keys import validate_api_key


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_jwt(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, str]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "jwt_required", "message": "Bearer token is required."},
        )
    token = authorization.removeprefix("Bearer ").strip()
    return verify_access_token(token)


def require_admin(claims: dict[str, str] = Depends(require_jwt)) -> dict[str, str]:
    if claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "admin_required", "message": "Admin role is required."},
        )
    return claims


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> dict[str, str | int | None]:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "api_key_required", "message": "X-API-Key header is required."},
        )
    api_key = validate_api_key(db, x_api_key)
    return {
        "api_key_id": api_key.id,
        "plan": api_key.plan,
        "daily_limit": api_key.daily_limit,
    }
