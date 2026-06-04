from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_access_token
from app.db.session import SessionLocal


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
