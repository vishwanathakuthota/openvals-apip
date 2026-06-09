import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ApiKey, ApiSubscription, ApiUsageEvent, Invoice

PLAN_LIMITS = {
    "community": 100,
    "research": 1000,
    "professional": 5000,
    "enterprise": None,
}
PLAN_ALIASES = {
    "free": "community",
    "pro": "professional",
}
PLAN_CONFIG = {
    "community": {
        "name": "Community",
        "daily_quota": 100,
        "monthly_price_usd": 0,
        "entitlements": ["public_api", "developer_docs", "community_rate_limit"],
    },
    "research": {
        "name": "Research",
        "daily_quota": 1000,
        "monthly_price_usd": 99,
        "entitlements": ["public_api", "research_exports", "source_lineage", "email_support"],
    },
    "professional": {
        "name": "Professional",
        "daily_quota": 5000,
        "monthly_price_usd": 499,
        "entitlements": [
            "public_api",
            "research_exports",
            "source_lineage",
            "trust_index_history",
            "priority_support",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "daily_quota": None,
        "monthly_price_usd": 2500,
        "entitlements": [
            "public_api",
            "research_exports",
            "source_lineage",
            "trust_index_history",
            "custom_contract",
            "sla",
        ],
    },
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
    ensure_subscription(db, record)
    return GeneratedApiKey(plaintext_key=plaintext_key, record=record)


def hash_api_key(api_key: str) -> str:
    return sha256(api_key.encode("utf-8")).hexdigest()


def normalize_plan(plan: str) -> str:
    normalized = PLAN_ALIASES.get(plan.strip().lower(), plan.strip().lower())
    if normalized not in PLAN_LIMITS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_api_key_plan",
                "message": "Plan must be community, research, professional, or enterprise.",
            },
        )
    return normalized


def validate_api_key(
    db: Session,
    plaintext_key: str,
    endpoint: str | None = None,
    method: str | None = None,
) -> ApiKey:
    key_hash = hash_api_key(plaintext_key.strip())
    api_key = db.scalar(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.status == "active")
    )
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_api_key", "message": "A valid X-API-Key is required."},
        )
    if api_key.plan in PLAN_ALIASES:
        api_key.plan = normalize_plan(api_key.plan)
        api_key.daily_limit = PLAN_LIMITS[api_key.plan]
    enforce_daily_limit(api_key)
    record_usage_event(db, api_key, endpoint=endpoint, method=method)
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


def rotate_api_key(db: Session, api_key: ApiKey) -> GeneratedApiKey:
    plaintext_key = f"apip_live_{token_urlsafe(32)}"
    api_key.key_prefix = plaintext_key[:16]
    api_key.key_hash = hash_api_key(plaintext_key)
    api_key.status = "active"
    api_key.usage_count_today = 0
    api_key.usage_window_start = datetime.now(UTC).date()
    db.add(api_key)
    db.flush()
    return GeneratedApiKey(plaintext_key=plaintext_key, record=api_key)


def revoke_api_key(api_key: ApiKey) -> None:
    api_key.status = "revoked"


def record_usage_event(
    db: Session,
    api_key: ApiKey,
    endpoint: str | None,
    method: str | None,
) -> None:
    db.add(
        ApiUsageEvent(
            api_key_id=api_key.id,
            endpoint=endpoint or "unknown",
            method=method or "GET",
            plan=api_key.plan,
            status_code=200,
            request_count=1,
            usage_date=datetime.now(UTC).date(),
        )
    )


def ensure_subscription(db: Session, api_key: ApiKey) -> ApiSubscription:
    plan = normalize_plan(api_key.plan)
    api_key.plan = plan
    api_key.daily_limit = PLAN_LIMITS[plan]
    subscription = db.scalar(
        select(ApiSubscription).where(
            ApiSubscription.api_key_id == api_key.id,
            ApiSubscription.status == "active",
        )
    )
    today = datetime.now(UTC).date()
    period_end = today + timedelta(days=30)
    config = PLAN_CONFIG[plan]
    if not subscription:
        subscription = ApiSubscription(
            api_key_id=api_key.id,
            plan=plan,
            status="active",
            monthly_price_usd=config["monthly_price_usd"],
            daily_quota=config["daily_quota"],
            entitlements_json=json.dumps(config["entitlements"]),
            current_period_start=today,
            current_period_end=period_end,
            payment_provider="manual",
        )
        db.add(subscription)
        db.flush()
        ensure_invoice(db, subscription)
        return subscription
    subscription.plan = plan
    subscription.monthly_price_usd = config["monthly_price_usd"]
    subscription.daily_quota = config["daily_quota"]
    subscription.entitlements_json = json.dumps(config["entitlements"])
    return subscription


def ensure_invoice(db: Session, subscription: ApiSubscription) -> Invoice:
    existing = db.scalar(
        select(Invoice).where(
            Invoice.subscription_id == subscription.id,
            Invoice.period_start == subscription.current_period_start,
        )
    )
    if existing:
        return existing
    invoice = Invoice(
        subscription_id=subscription.id,
        invoice_number=f"APIP-{subscription.current_period_start:%Y%m%d}-{subscription.id[:8]}",
        status="draft",
        amount_due_usd=subscription.monthly_price_usd,
        amount_paid_usd=0,
        currency="USD",
        period_start=subscription.current_period_start,
        period_end=subscription.current_period_end,
        payment_provider=subscription.payment_provider,
    )
    db.add(invoice)
    db.flush()
    return invoice


def plan_payloads() -> list[dict[str, object]]:
    return [
        {
            "key": key,
            "name": config["name"],
            "daily_quota": config["daily_quota"],
            "monthly_price_usd": config["monthly_price_usd"],
            "entitlements": config["entitlements"],
        }
        for key, config in PLAN_CONFIG.items()
    ]


def subscription_payload(subscription: ApiSubscription) -> dict[str, object]:
    return {
        "id": subscription.id,
        "api_key_id": subscription.api_key_id,
        "plan": subscription.plan,
        "status": subscription.status,
        "monthly_price_usd": float(subscription.monthly_price_usd),
        "daily_quota": subscription.daily_quota,
        "entitlements": json.loads(subscription.entitlements_json),
        "current_period_start": subscription.current_period_start.isoformat(),
        "current_period_end": subscription.current_period_end.isoformat(),
        "payment_provider": subscription.payment_provider,
        "external_subscription_id": subscription.external_subscription_id,
    }


def invoice_payload(invoice: Invoice) -> dict[str, object]:
    return {
        "id": invoice.id,
        "subscription_id": invoice.subscription_id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
        "amount_due_usd": float(invoice.amount_due_usd),
        "amount_paid_usd": float(invoice.amount_paid_usd),
        "currency": invoice.currency,
        "period_start": invoice.period_start.isoformat(),
        "period_end": invoice.period_end.isoformat(),
        "payment_provider": invoice.payment_provider,
        "external_invoice_id": invoice.external_invoice_id,
    }


def usage_event_payload(event: ApiUsageEvent) -> dict[str, object]:
    return {
        "id": event.id,
        "api_key_id": event.api_key_id,
        "endpoint": event.endpoint,
        "method": event.method,
        "plan": event.plan,
        "status_code": event.status_code,
        "request_count": event.request_count,
        "usage_date": event.usage_date.isoformat(),
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def commercial_dashboard_payload(db: Session) -> dict[str, object]:
    today = datetime.now(UTC).date()
    api_keys = db.scalars(select(ApiKey)).all()
    subscriptions = db.scalars(select(ApiSubscription)).all()
    invoices = db.scalars(select(Invoice)).all()
    usage_events = db.scalars(select(ApiUsageEvent)).all()
    requests_today = sum(event.request_count for event in usage_events if event.usage_date == today)
    endpoint_rows = db.execute(
        select(ApiUsageEvent.endpoint, func.sum(ApiUsageEvent.request_count))
        .group_by(ApiUsageEvent.endpoint)
        .order_by(func.sum(ApiUsageEvent.request_count).desc())
        .limit(10)
    ).all()
    return {
        "revenue": {
            "monthly_recurring_revenue": round(
                sum(
                    float(subscription.monthly_price_usd)
                    for subscription in subscriptions
                    if subscription.status == "active"
                ),
                2,
            ),
            "draft_invoice_amount": round(
                sum(
                    float(invoice.amount_due_usd)
                    for invoice in invoices
                    if invoice.status == "draft"
                ),
                2,
            ),
            "invoice_count": len(invoices),
        },
        "active_users": {
            "active_api_keys": len([item for item in api_keys if item.status == "active"]),
            "active_subscriptions": len(
                [item for item in subscriptions if item.status == "active"]
            ),
        },
        "api_consumption": {
            "requests_today": requests_today,
            "total_requests": sum(event.request_count for event in usage_events),
            "top_endpoints": [
                {"endpoint": endpoint, "request_count": int(request_count or 0)}
                for endpoint, request_count in endpoint_rows
            ],
        },
        "plan_distribution": {
            plan: len([item for item in api_keys if normalize_plan(item.plan) == plan])
            for plan in PLAN_LIMITS
        },
    }


def api_key_payload(api_key: ApiKey) -> dict[str, object]:
    plan = normalize_plan(api_key.plan)
    return {
        "id": api_key.id,
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "plan": plan,
        "daily_limit": api_key.daily_limit,
        "entitlements": PLAN_CONFIG[plan]["entitlements"],
        "status": api_key.status,
        "usage_count_today": api_key.usage_count_today,
        "usage_window_start": api_key.usage_window_start.isoformat()
        if api_key.usage_window_start
        else None,
        "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        "created_at": api_key.created_at.isoformat() if api_key.created_at else None,
    }
