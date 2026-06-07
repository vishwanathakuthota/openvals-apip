from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AutonomousEvidenceRecord,
    Company,
    TrustChangeNotification,
    TrustIndexSnapshot,
)
from app.domains.autonomous_research.service import PUBLISHED

TRUST_INDEX_METHODOLOGY_VERSION = "trust-index-v1"
TRUST_INDEX_WEIGHTS = {
    "confidence": 0.30,
    "evidence_coverage": 0.25,
    "transparency": 0.20,
    "reproducibility": 0.15,
    "source_quality": 0.10,
}


@dataclass(frozen=True)
class TrustIndexResult:
    entity_type: str
    entity_id: str | None
    entity_name: str
    trust_index: float
    trust_rating: str
    trust_classification: str
    confidence_score: float
    evidence_coverage_score: float
    transparency_score: float
    reproducibility_score: float
    source_quality_score: float
    source_count: int
    published_record_count: int
    methodology_version: str = TRUST_INDEX_METHODOLOGY_VERSION


def calculate_trust_index(
    confidence: float,
    evidence_coverage: float,
    transparency: float,
    reproducibility: float,
    source_quality: float,
) -> float:
    return round(
        confidence * TRUST_INDEX_WEIGHTS["confidence"]
        + evidence_coverage * TRUST_INDEX_WEIGHTS["evidence_coverage"]
        + transparency * TRUST_INDEX_WEIGHTS["transparency"]
        + reproducibility * TRUST_INDEX_WEIGHTS["reproducibility"]
        + source_quality * TRUST_INDEX_WEIGHTS["source_quality"],
        2,
    )


def trust_rating(score: float) -> str:
    if score >= 90:
        return "Verified"
    if score >= 80:
        return "High Trust"
    if score >= 70:
        return "Trusted"
    if score >= 60:
        return "Watchlist"
    return "Low Trust"


def trust_classification(score: float) -> str:
    if score >= 90:
        return "Gold Standard"
    if score >= 80:
        return "Strong Evidence"
    if score >= 70:
        return "Reliable"
    if score >= 60:
        return "Developing"
    return "Insufficient Evidence"


def company_trust_index(db: Session, company: Company) -> TrustIndexResult:
    records = published_company_records(db, company.id)
    return trust_index_from_records(
        entity_type="company",
        entity_id=company.id,
        entity_name=company_display_name(company),
        records=records,
    )


def global_trust_index(db: Session) -> TrustIndexResult:
    records = db.scalars(
        select(AutonomousEvidenceRecord).where(AutonomousEvidenceRecord.status == PUBLISHED)
    ).all()
    return trust_index_from_records(
        entity_type="global",
        entity_id=None,
        entity_name="APIP Global Trust Index",
        records=records,
    )


def trust_index_from_records(
    entity_type: str,
    entity_id: str | None,
    entity_name: str,
    records: list[AutonomousEvidenceRecord],
) -> TrustIndexResult:
    confidence = average([float(record.confidence_score) for record in records])
    coverage = average([float(record.evidence_coverage_score) for record in records])
    transparency = average([float(record.transparency_score) for record in records])
    reproducibility = average([float(record.reproducibility_score) for record in records])
    source_quality = average([float(record.source_quality_score) for record in records])
    score = calculate_trust_index(
        confidence=confidence,
        evidence_coverage=coverage,
        transparency=transparency,
        reproducibility=reproducibility,
        source_quality=source_quality,
    )
    return TrustIndexResult(
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        trust_index=score,
        trust_rating=trust_rating(score),
        trust_classification=trust_classification(score),
        confidence_score=confidence,
        evidence_coverage_score=coverage,
        transparency_score=transparency,
        reproducibility_score=reproducibility,
        source_quality_score=source_quality,
        source_count=len({record.source_id for record in records}),
        published_record_count=len(records),
    )


def trust_index_payload(result: TrustIndexResult) -> dict[str, object]:
    return {
        "entity_type": result.entity_type,
        "entity_id": result.entity_id,
        "entity_name": result.entity_name,
        "trust_index": result.trust_index,
        "trust_rating": result.trust_rating,
        "trust_classification": result.trust_classification,
        "components": {
            "confidence": result.confidence_score,
            "evidence_coverage": result.evidence_coverage_score,
            "transparency": result.transparency_score,
            "reproducibility": result.reproducibility_score,
            "source_quality": result.source_quality_score,
        },
        "weights": TRUST_INDEX_WEIGHTS,
        "source_count": result.source_count,
        "published_record_count": result.published_record_count,
        "methodology_version": result.methodology_version,
    }


def leaderboard_payload(db: Session) -> dict[str, object]:
    items = [
        trust_index_payload(company_trust_index(db, company))
        for company in db.scalars(select(Company).where(Company.status == "active")).all()
    ]
    ranked = sorted(items, key=lambda item: float(item["trust_index"]), reverse=True)
    return {"items": ranked, "next_cursor": None}


def trust_index_dashboard_payload(db: Session) -> dict[str, object]:
    global_result = global_trust_index(db)
    leaderboard = leaderboard_payload(db)["items"]
    snapshots = latest_snapshots(db)
    notifications = latest_notifications(db)
    return {
        "summary": trust_index_payload(global_result),
        "leaderboard": leaderboard,
        "trend": [trust_snapshot_payload(snapshot) for snapshot in snapshots],
        "notifications": [trust_notification_payload(item) for item in notifications],
        "methodology": methodology_payload(),
    }


def methodology_payload() -> dict[str, object]:
    return {
        "name": "OpenVals Trust Index",
        "version": TRUST_INDEX_METHODOLOGY_VERSION,
        "formula": (
            "30% Confidence + 25% Evidence Coverage + 20% Transparency + "
            "15% Reproducibility + 10% Source Quality"
        ),
        "weights": TRUST_INDEX_WEIGHTS,
        "rating_scale": {
            "90-100": "Verified / Gold Standard",
            "80-89": "High Trust / Strong Evidence",
            "70-79": "Trusted / Reliable",
            "60-69": "Watchlist / Developing",
            "0-59": "Low Trust / Insufficient Evidence",
        },
    }


def ensure_trust_index_snapshots(db: Session) -> None:
    today = date.today()
    previous_day = today - timedelta(days=1)
    results = [global_trust_index(db)] + [
        company_trust_index(db, company)
        for company in db.scalars(select(Company).where(Company.status == "active")).all()
    ]
    for result in results:
        if result.published_record_count == 0:
            continue
        previous = latest_snapshot_for_entity(db, result.entity_type, result.entity_id)
        if not previous:
            db.add(snapshot_from_result(result, previous_day, max(result.trust_index - 2, 0)))
            previous_score = result.trust_index - 2
        else:
            previous_score = float(previous.trust_index)
        current = db.scalar(
            select(TrustIndexSnapshot).where(
                TrustIndexSnapshot.entity_type == result.entity_type,
                TrustIndexSnapshot.entity_id == result.entity_id,
                TrustIndexSnapshot.snapshot_date == today,
            )
        )
        if not current:
            db.add(snapshot_from_result(result, today, result.trust_index))
        create_trust_notification(db, result, previous_score)


def snapshot_from_result(
    result: TrustIndexResult, snapshot_date: date, trust_index: float
) -> TrustIndexSnapshot:
    return TrustIndexSnapshot(
        entity_type=result.entity_type,
        entity_id=result.entity_id,
        entity_name=result.entity_name,
        trust_index=trust_index,
        trust_rating=trust_rating(trust_index),
        trust_classification=trust_classification(trust_index),
        confidence_score=result.confidence_score,
        evidence_coverage_score=result.evidence_coverage_score,
        transparency_score=result.transparency_score,
        reproducibility_score=result.reproducibility_score,
        source_quality_score=result.source_quality_score,
        source_count=result.source_count,
        published_record_count=result.published_record_count,
        snapshot_date=snapshot_date,
        methodology_version=result.methodology_version,
    )


def create_trust_notification(
    db: Session, result: TrustIndexResult, previous_score: float | None
) -> None:
    if previous_score is None:
        change = 0.0
    else:
        change = round(result.trust_index - previous_score, 2)
    notification_type = "trust_stable"
    if change >= 1:
        notification_type = "trust_increased"
    elif change <= -1:
        notification_type = "trust_decreased"
    existing = db.scalar(
        select(TrustChangeNotification).where(
            TrustChangeNotification.entity_type == result.entity_type,
            TrustChangeNotification.entity_id == result.entity_id,
            TrustChangeNotification.current_trust_index == result.trust_index,
            TrustChangeNotification.change_amount == change,
        )
    )
    if existing:
        return
    db.add(
        TrustChangeNotification(
            entity_type=result.entity_type,
            entity_id=result.entity_id,
            entity_name=result.entity_name,
            previous_trust_index=previous_score,
            current_trust_index=result.trust_index,
            change_amount=change,
            notification_type=notification_type,
            message=(
                f"{result.entity_name} Trust Index is {result.trust_index:.1f} "
                f"({result.trust_rating}), change {change:+.1f}."
            ),
        )
    )


def latest_snapshot_for_entity(
    db: Session, entity_type: str, entity_id: str | None
) -> TrustIndexSnapshot | None:
    return db.scalar(
        select(TrustIndexSnapshot)
        .where(
            TrustIndexSnapshot.entity_type == entity_type,
            TrustIndexSnapshot.entity_id == entity_id,
        )
        .order_by(TrustIndexSnapshot.snapshot_date.desc())
        .limit(1)
    )


def latest_snapshots(db: Session) -> list[TrustIndexSnapshot]:
    return db.scalars(
        select(TrustIndexSnapshot).order_by(
            TrustIndexSnapshot.snapshot_date.desc(), TrustIndexSnapshot.entity_name
        )
    ).all()


def latest_notifications(db: Session) -> list[TrustChangeNotification]:
    return db.scalars(
        select(TrustChangeNotification).order_by(TrustChangeNotification.created_at.desc()).limit(25)
    ).all()


def trust_snapshot_payload(snapshot: TrustIndexSnapshot) -> dict[str, object]:
    return {
        "entity_type": snapshot.entity_type,
        "entity_id": snapshot.entity_id,
        "entity_name": snapshot.entity_name,
        "trust_index": float(snapshot.trust_index),
        "trust_rating": snapshot.trust_rating,
        "trust_classification": snapshot.trust_classification,
        "snapshot_date": snapshot.snapshot_date.isoformat(),
        "methodology_version": snapshot.methodology_version,
    }


def trust_notification_payload(notification: TrustChangeNotification) -> dict[str, object]:
    return {
        "id": notification.id,
        "entity_type": notification.entity_type,
        "entity_id": notification.entity_id,
        "entity_name": notification.entity_name,
        "previous_trust_index": float(notification.previous_trust_index)
        if notification.previous_trust_index is not None
        else None,
        "current_trust_index": float(notification.current_trust_index),
        "change_amount": float(notification.change_amount),
        "notification_type": notification.notification_type,
        "message": notification.message,
        "status": notification.status,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


def published_company_records(db: Session, company_id: str) -> list[AutonomousEvidenceRecord]:
    return db.scalars(
        select(AutonomousEvidenceRecord).where(
            AutonomousEvidenceRecord.company_id == company_id,
            AutonomousEvidenceRecord.status == PUBLISHED,
        )
    ).all()


def company_display_name(company: Company) -> str:
    return "Alphabet" if company.slug == "google" else company.name


def average(values: list[float]) -> float:
    if not values:
        return 0
    return round(sum(values) / len(values), 2)
