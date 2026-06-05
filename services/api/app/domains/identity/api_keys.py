from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ApiKey

PLAN_LIMITS = {
    "free": 100,
    "pro": 5000,
    "enterprise": None,
}


@dataclass(frozen=True)
class GeneratedApiKey:
    plaintext_key: str
    record: ApiKey


def generate_api_key(db: Session, name: str, plan: str, created_by_user_id: str) -> GeneratedApiKey:
    normalized_plan = normalize_plan(plan)
    plaintext_key = f"apip_live_{token_urlsafe(32)}"
    record = ApiKey(
        name=name,
        key_prefix=plaintext_key[:16],
        key_hash=hash_api_key(plaintext_key),
        plan=normalized_plan,
        daily_limit=PLAN_LIMITS[normalized_plan],
        status="active",
        created_by_user_id=created_by_user_id,
        usage_count_today=0,
        usage_window_start=datetime.now(UTC).date(),
    )
    db.add(record)
    db.flush()
    return GeneratedApiKey(plaintext_key=plaintext_key, record=record)


def hash_api_key(api_key: str) -> str:
    return sha256(api_key.encode("utf-8")).hexdigest()


def normalize_plan(plan: str) -> str:
    normalized = plan.strip().lower()
    if normalized not in PLAN_LIMITS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_api_key_plan",
                "message": "Plan must be free, pro, or enterprise.",
            },
        )
    return normalized


def validate_api_key(db: Session, plaintext_key: str) -> ApiKey:
    key_hash = hash_api_key(plaintext_key.strip())
    api_key = db.scalar(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.status == "active")
    )
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_api_key", "message": "A valid X-API-Key is required."},
        )
    enforce_daily_limit(api_key)
    db.add(api_key)
    db.commit()
    return api_key


def enforce_daily_limit(api_key: ApiKey, today: date | None = None) -> None:
    current_day = today or datetime.now(UTC).date()
    if api_key.usage_window_start != current_day:
        api_key.usage_window_start = current_day
        api_key.usage_count_today = 0
    if api_key.daily_limit is not None and api_key.usage_count_today >= api_key.daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "api_key_rate_limited",
                "message": "Daily API key quota exceeded.",
            },
        )
    api_key.usage_count_today += 1
    api_key.last_used_at = datetime.now(UTC)


def api_key_payload(api_key: ApiKey) -> dict[str, object]:
    return {
        "id": api_key.id,
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "plan": api_key.plan,
        "daily_limit": api_key.daily_limit,
        "status": api_key.status,
        "usage_count_today": api_key.usage_count_today,
        "usage_window_start": api_key.usage_window_start.isoformat()
        if api_key.usage_window_start
        else None,
        "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        "created_at": api_key.created_at.isoformat() if api_key.created_at else None,
    }
