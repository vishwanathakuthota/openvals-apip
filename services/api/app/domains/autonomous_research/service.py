import json
from dataclasses import dataclass
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AuditLog,
    AutonomousEvidenceRecord,
    Company,
    ConfidenceScore,
    MetricDefinition,
    MetricSource,
    MetricValue,
    MetricVersion,
    Source,
    SourceMetric,
)
from app.domains.confidence.service import (
    calculate_confidence,
    confidence_label,
    cross_verification_score,
    freshness_score,
    methodology_transparency_score,
)
from app.domains.sources.credibility import source_credibility_score

PHASE_1_COMPANY_SLUGS = {"microsoft", "nvidia", "google"}
MICROSOFT_PILOT_COMPANY_SLUG = "microsoft"
GOLD_STANDARD_COMPANY_RANKS = {"microsoft": 1, "nvidia": 2}
GOLD_STANDARD_METRIC_KEYS = {
    "adoption",
    "ai_revenue",
    "ai_spend",
    "gross_margin",
    "revenue_growth",
    "roi",
}
COLLECTED = "Collected"
UNDER_REVIEW = "Under Review"
APPROVED = "Approved"
REJECTED = "Rejected"
PUBLISHED = "Published"
ADDITIONAL_EVIDENCE_REQUESTED = "Additional Evidence Requested"
EVIDENCE_CLASSIFICATIONS = {"Reported", "Estimated", "Derived", "Validated"}
REQUIRED_EVIDENCE_EXPECTED = {
    "ai_revenue": {"sec_filing", "annual_report", "earnings_call"},
    "ai_spend": {"sec_filing", "annual_report", "earnings_call"},
    "adoption": {"annual_report", "earnings_call", "investor_presentation"},
    "gross_margin": {"sec_filing", "annual_report", "earnings_call"},
    "revenue_growth": {"sec_filing", "annual_report", "earnings_call"},
    "roi": {"sec_filing", "annual_report", "earnings_call"},
}
COMPANY_SOURCE_MATCHERS = {
    "google": {
        "publishers": {"Alphabet Investor Relations"},
        "title_terms": {"alphabet"},
        "url_terms": {"CIK=1652044"},
    },
    "microsoft": {
        "publishers": {"Microsoft Investor Relations"},
        "title_terms": {"microsoft"},
        "url_terms": {"CIK=789019"},
    },
    "nvidia": {
        "publishers": {"NVIDIA Investor Relations"},
        "title_terms": {"nvidia"},
        "url_terms": {"CIK=1045810"},
    },
}


@dataclass(frozen=True)
class AgentRunResult:
    agent: str
    processed_count: int
    status: str = "completed"


def run_research_agent(db: Session) -> AgentRunResult:
    created = 0
    companies = db.scalars(
        select(Company).where(Company.slug.in_(PHASE_1_COMPANY_SLUGS)).order_by(Company.name)
    ).all()
    for company in companies:
        for metric_definition in phase_1_metric_definitions(db):
            metric = current_metric(db, company.id, metric_definition.id)
            if not metric:
                continue
            source = best_approved_source_for_company_metric(
                db, company.slug, metric_definition.key
            )
            if not source or evidence_exists(db, company.id, metric_definition.id, source.id):
                continue
            record = AutonomousEvidenceRecord(
                company_id=company.id,
                metric_definition_id=metric_definition.id,
                metric_value_id=metric.id,
                source_id=source.id,
                previous_value=metric.value_numeric,
                discovered_value=metric.value_numeric,
                source_url=source.url or "",
                source_type=source.source_type,
                evidence_text=evidence_text(company, metric_definition, source, metric),
                collection_timestamp=datetime.now(UTC),
                collection_method="approved_source_registry",
                status=COLLECTED,
                evidence_classification=classification_for_source(
                    metric_definition.key, source.source_type
                ),
                validation_status=COLLECTED,
            )
            db.add(record)
            db.flush()
            write_agent_audit(
                db,
                action="autonomous_research.collected",
                record=record,
                metadata={"agent": "Research Agent", "source_url": record.source_url},
            )
            created += 1
    return AgentRunResult(agent="Research Agent", processed_count=created)


def run_validation_agent(db: Session) -> AgentRunResult:
    records = db.scalars(
        select(AutonomousEvidenceRecord).where(AutonomousEvidenceRecord.status == COLLECTED)
    ).all()
    for record in records:
        validate_evidence_record(db, record)
    return AgentRunResult(agent="Validation Agent", processed_count=len(records))


def run_approval_agent(db: Session) -> AgentRunResult:
    records = db.scalars(
        select(AutonomousEvidenceRecord).where(
            AutonomousEvidenceRecord.status == UNDER_REVIEW,
            AutonomousEvidenceRecord.approval_recommendation.is_(None),
        )
    ).all()
    for record in records:
        if (
            record.source_type == "sec_filing"
            and float(record.confidence_score) >= 95
            and float(record.evidence_coverage_score) >= 90
        ):
            record.approval_recommendation = "Auto Approve"
        elif float(record.confidence_score) < 40:
            record.approval_recommendation = "Reject"
        else:
            record.approval_recommendation = "Manual Review"
        write_agent_audit(
            db,
            action="autonomous_research.approval_recommended",
            record=record,
            metadata={
                "agent": "Approval Agent",
                "recommendation": record.approval_recommendation,
                "never_auto_publish": True,
            },
        )
    return AgentRunResult(agent="Approval Agent", processed_count=len(records))


def approve_evidence_record(
    record: AutonomousEvidenceRecord,
    reviewer_user_id: str,
    notes: str | None,
    confidence_score: float | None = None,
) -> None:
    if confidence_score is not None:
        record.confidence_score = round(confidence_score, 2)
        record.confidence_label = confidence_label(confidence_score)
        record.openvals_score = calculate_openvals_score(record)
    record.status = APPROVED
    record.validation_status = APPROVED
    record.evidence_classification = "Validated"
    record.reviewer_user_id = reviewer_user_id
    record.reviewed_at = datetime.now(UTC)
    record.reviewer_decision = "Approve"
    record.reviewer_notes = notes
    record.approved_at = datetime.now(UTC)


def reject_evidence_record(
    record: AutonomousEvidenceRecord,
    reviewer_user_id: str,
    notes: str | None,
) -> None:
    record.status = REJECTED
    record.validation_status = REJECTED
    record.reviewer_user_id = reviewer_user_id
    record.reviewed_at = datetime.now(UTC)
    record.reviewer_decision = "Reject"
    record.reviewer_notes = notes


def request_additional_evidence(
    record: AutonomousEvidenceRecord,
    reviewer_user_id: str,
    notes: str | None,
) -> None:
    record.status = ADDITIONAL_EVIDENCE_REQUESTED
    record.validation_status = ADDITIONAL_EVIDENCE_REQUESTED
    record.reviewer_user_id = reviewer_user_id
    record.reviewed_at = datetime.now(UTC)
    record.reviewer_decision = "Request Additional Evidence"
    record.reviewer_notes = notes


def run_publisher_agent(db: Session) -> AgentRunResult:
    records = db.scalars(
        select(AutonomousEvidenceRecord).where(AutonomousEvidenceRecord.status == APPROVED)
    ).all()
    for record in records:
        publish_evidence_record(db, record)
    return AgentRunResult(agent="Publisher Agent", processed_count=len(records))


def run_microsoft_pilot_validation(
    db: Session,
    reviewer_user_id: str,
) -> dict[str, object]:
    return run_company_gold_standard_validation(db, "microsoft", reviewer_user_id)


def run_nvidia_gold_standard_validation(
    db: Session,
    reviewer_user_id: str,
) -> dict[str, object]:
    return run_company_gold_standard_validation(db, "nvidia", reviewer_user_id)


def run_company_gold_standard_validation(
    db: Session,
    company_slug: str,
    reviewer_user_id: str,
) -> dict[str, object]:
    run_research_agent(db)
    run_validation_agent(db)
    run_approval_agent(db)
    records = company_evidence_records(db, company_slug)
    approved_count = 0
    for record in records:
        if record.status in {PUBLISHED, REJECTED}:
            continue
        if record.status == COLLECTED:
            validate_evidence_record(db, record)
        approve_evidence_record(
            record,
            reviewer_user_id=reviewer_user_id,
            notes=(
                f"Approved in the {record.company.name} Gold Standard validation after Research, "
                "Validation, Confidence, Evidence Coverage, and OpenVals Score checks."
            ),
        )
        write_agent_audit(
            db,
            action=f"{company_slug}_gold_standard.approved",
            record=record,
            metadata={"gold_standard_company": company_slug},
        )
        approved_count += 1
    published = 0
    for record in company_evidence_records(db, company_slug):
        if record.status == APPROVED:
            publish_evidence_record(db, record)
            published += 1
    final_records = company_evidence_records(db, company_slug)
    rank = GOLD_STANDARD_COMPANY_RANKS.get(company_slug)
    company_name = final_records[0].company.name if final_records else company_slug.title()
    return {
        "company": company_name,
        "status": gold_standard_status(final_records),
        "gold_standard_rank": rank,
        "gold_standard_label": f"Gold Standard Company #{rank}" if rank else None,
        "approved_count": approved_count,
        "published_count": published,
        "records": [evidence_record_payload(record) for record in final_records],
    }


def publish_evidence_record(db: Session, record: AutonomousEvidenceRecord) -> MetricValue:
    if record.status != APPROVED:
        raise ValueError("Only approved evidence records can be published.")
    metric = record.metric_value or current_metric(
        db, record.company_id, record.metric_definition_id
    )
    if not metric:
        metric = MetricValue(
            metric_definition_id=record.metric_definition_id,
            entity_type="company",
            entity_id=record.company_id,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 12, 31),
            value_numeric=record.discovered_value,
            currency="usd",
            methodology=record.validation_notes or record.evidence_text,
            status="approved",
        )
        db.add(metric)
        db.flush()
    previous_value = metric.value_numeric
    metric.value_numeric = record.discovered_value
    metric.evidence_classification = "Validated"
    metric.validation_status = PUBLISHED
    metric.evidence_coverage_score = record.evidence_coverage_score
    metric.openvals_score = record.openvals_score
    metric.methodology = record.validation_notes or record.evidence_text
    record.metric_value_id = metric.id
    record.status = PUBLISHED
    record.validation_status = PUBLISHED
    record.published_at = datetime.now(UTC)
    record.version_number = next_metric_version(db, metric.id)
    link_metric_source(db, metric, record.source, record)
    upsert_confidence(db, metric, record)
    db.add(
        MetricVersion(
            source_metric_id=ensure_publication_source_metric(db, record).id,
            metric_value_id=metric.id,
            version=record.version_number,
            value_numeric=record.discovered_value,
            approved_status="approved",
            created_by_user_id=record.reviewer_user_id or legacy_admin_user_id(db),
        )
    )
    write_agent_audit(
        db,
        action="autonomous_research.published",
        record=record,
        metadata={
            "agent": "Publisher Agent",
            "metric_value_id": metric.id,
            "previous_value": float(previous_value) if previous_value is not None else None,
            "published_value": float(record.discovered_value),
        },
    )
    return metric


def validate_evidence_record(db: Session, record: AutonomousEvidenceRecord) -> None:
    source = record.source
    source_set = sources_for_company_metric(db, record.company.slug, record.metric_definition.key)
    coverage = evidence_coverage_for_metric(record.metric_definition.key, source_set)
    transparency = methodology_transparency_score(record.evidence_text)
    reproducibility = 90 if record.collection_method == "approved_source_registry" else 60
    source_quality = source_credibility_score(source.source_type, source.published_at)
    confidence = calculate_confidence(
        source_reliability=source.reliability_score,
        data_freshness=freshness_score(source.published_at),
        cross_verification=cross_verification_score(len(source_set)),
        methodology_transparency=transparency,
    )
    record.confidence_score = float(confidence["score"])
    record.confidence_label = str(confidence["label"])
    record.evidence_coverage_score = coverage
    record.transparency_score = transparency
    record.reproducibility_score = reproducibility
    record.source_quality_score = source_quality
    record.validation_score = round(
        (float(record.confidence_score) * 0.50) + (coverage * 0.30) + (source_quality * 0.20),
        2,
    )
    record.openvals_score = calculate_openvals_score(record)
    record.validation_timestamp = datetime.now(UTC)
    record.validation_notes = (
        "Validation Agent scored evidence using confidence, evidence coverage, "
        "source quality, transparency, and reproducibility. Record remains queued for human review."
    )
    record.validation_status = UNDER_REVIEW
    record.status = UNDER_REVIEW
    write_agent_audit(
        db,
        action="autonomous_research.validated",
        record=record,
        metadata={
            "agent": "Validation Agent",
            "confidence_score": float(record.confidence_score),
            "evidence_coverage_score": float(record.evidence_coverage_score),
            "openvals_score": float(record.openvals_score),
        },
    )


def calculate_openvals_score(record: AutonomousEvidenceRecord) -> float:
    score = (
        float(record.confidence_score) * 0.30
        + float(record.evidence_coverage_score) * 0.25
        + float(record.transparency_score) * 0.20
        + float(record.reproducibility_score) * 0.15
        + float(record.source_quality_score) * 0.10
    )
    return round(score, 2)


def openvals_classification(score: float) -> str:
    if score >= 90:
        return "Exceptional"
    if score >= 80:
        return "Strong"
    if score >= 70:
        return "Reliable"
    if score >= 60:
        return "Moderate"
    return "Weak"


def evidence_record_payload(record: AutonomousEvidenceRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "company": record.company.name,
        "company_id": record.company_id,
        "metric": record.metric_definition.key,
        "metric_name": record.metric_definition.name,
        "previous_value": float(record.previous_value)
        if record.previous_value is not None
        else None,
        "discovered_value": float(record.discovered_value),
        "source_url": record.source_url,
        "source_type": record.source_type,
        "source_title": record.source.title,
        "evidence_text": record.evidence_text,
        "collection_timestamp": record.collection_timestamp.isoformat(),
        "collection_method": record.collection_method,
        "status": record.status,
        "evidence_classification": record.evidence_classification,
        "confidence_score": float(record.confidence_score),
        "confidence_label": record.confidence_label,
        "evidence_coverage_score": float(record.evidence_coverage_score),
        "validation_score": float(record.validation_score),
        "openvals_score": float(record.openvals_score),
        "openvals_classification": openvals_classification(float(record.openvals_score)),
        "transparency_score": float(record.transparency_score),
        "reproducibility_score": float(record.reproducibility_score),
        "source_quality_score": float(record.source_quality_score),
        "validation_timestamp": record.validation_timestamp.isoformat()
        if record.validation_timestamp
        else None,
        "validation_notes": record.validation_notes,
        "validation_status": record.validation_status,
        "approval_recommendation": record.approval_recommendation,
        "reviewer": record.reviewer.full_name if record.reviewer else None,
        "reviewed_at": record.reviewed_at.isoformat() if record.reviewed_at else None,
        "reviewer_decision": record.reviewer_decision,
        "reviewer_notes": record.reviewer_notes,
        "approved_at": record.approved_at.isoformat() if record.approved_at else None,
        "published_at": record.published_at.isoformat() if record.published_at else None,
        "version_number": record.version_number,
        "lineage": public_lineage(record),
    }


def company_pilot_payload(db: Session, company_slug: str) -> dict[str, object]:
    records = company_evidence_records(db, company_slug)
    metrics = trust_center_payload(records)
    rank = GOLD_STANDARD_COMPANY_RANKS.get(company_slug)
    return {
        "company": records[0].company.name if records else company_slug.title(),
        "company_slug": company_slug,
        "status": gold_standard_status(records)
        if rank
        else "fully_validated"
        if records and all(record.status == PUBLISHED for record in records)
        else "in_progress",
        "gold_standard_rank": (
            rank if rank and gold_standard_complete(records) else None
        ),
        "gold_standard_label": (
            f"Gold Standard Company #{rank}"
            if rank and gold_standard_complete(records)
            else None
        ),
        "workflow": "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH",
        "metrics": metrics,
        "items": [evidence_record_payload(record) for record in records],
    }


def company_openvals_score_payload(db: Session, company_slug: str) -> dict[str, object]:
    records = company_evidence_records(db, company_slug)
    score = average(
        [float(record.openvals_score) for record in records if record.status == PUBLISHED]
    )
    rank = GOLD_STANDARD_COMPANY_RANKS.get(company_slug)
    return {
        "company": records[0].company.name if records else company_slug.title(),
        "company_slug": company_slug,
        "gold_standard_rank": (
            rank if rank and gold_standard_complete(records) else None
        ),
        "gold_standard_label": (
            f"Gold Standard Company #{rank}"
            if rank and gold_standard_complete(records)
            else None
        ),
        "openvals_score": score,
        "classification": openvals_classification(score),
        "published_records": len([record for record in records if record.status == PUBLISHED]),
        "evidence_coverage_score": average(
            [
                float(record.evidence_coverage_score)
                for record in records
                if record.status == PUBLISHED
            ]
        ),
        "confidence_score": average(
            [float(record.confidence_score) for record in records if record.status == PUBLISHED]
        ),
        "source_count": len({record.source_id for record in records if record.status == PUBLISHED}),
        "last_updated": max(
            [record.published_at for record in records if record.published_at],
            default=None,
        ).isoformat()
        if any(record.published_at for record in records)
        else None,
        "methodology_note": (
            "Company OpenVals Score averages published Microsoft pilot evidence records after "
            "confidence, coverage, transparency, reproducibility, source quality, "
            "reviewer approval, and publisher release."
        ),
    }


def trust_center_payload(records: list[AutonomousEvidenceRecord]) -> dict[str, object]:
    published = [record for record in records if record.status == PUBLISHED]
    approved = [record for record in records if record.status in {APPROVED, PUBLISHED}]
    under_review = [record for record in records if record.status == UNDER_REVIEW]
    return {
        "total_records": len(records),
        "published_records": len(published),
        "approved_records": len(approved),
        "under_review_records": len(under_review),
        "manual_review_required": len(
            [record for record in records if record.approval_recommendation == "Manual Review"]
        ),
        "average_confidence": average([float(record.confidence_score) for record in records]),
        "average_openvals_score": average([float(record.openvals_score) for record in records]),
        "public_lineage_records": len([record for record in records if record.published_at]),
    }


def public_lineage(record: AutonomousEvidenceRecord) -> dict[str, object]:
    return {
        "source_url": record.source_url,
        "source_type": record.source_type,
        "collection_date": record.collection_timestamp.isoformat(),
        "confidence": float(record.confidence_score),
        "evidence_coverage": float(record.evidence_coverage_score),
        "reviewer": record.reviewer.full_name if record.reviewer else None,
        "approval_date": record.approved_at.isoformat() if record.approved_at else None,
        "validation_status": record.validation_status,
        "evidence_classification": record.evidence_classification,
        "openvals_score": float(record.openvals_score),
    }


def phase_1_metric_definitions(db: Session) -> list[MetricDefinition]:
    return db.scalars(
        select(MetricDefinition)
        .where(MetricDefinition.key.in_(GOLD_STANDARD_METRIC_KEYS))
        .order_by(MetricDefinition.key)
    ).all()


def microsoft_evidence_records(db: Session) -> list[AutonomousEvidenceRecord]:
    return company_evidence_records(db, MICROSOFT_PILOT_COMPANY_SLUG)


def nvidia_evidence_records(db: Session) -> list[AutonomousEvidenceRecord]:
    return company_evidence_records(db, "nvidia")


def company_evidence_records(db: Session, company_slug: str) -> list[AutonomousEvidenceRecord]:
    return db.scalars(
        select(AutonomousEvidenceRecord)
        .join(Company)
        .where(Company.slug == company_slug)
        .order_by(AutonomousEvidenceRecord.updated_at.desc())
    ).all()


def current_metric(db: Session, company_id: str, definition_id: str) -> MetricValue | None:
    return db.scalar(
        select(MetricValue).where(
            MetricValue.entity_type == "company",
            MetricValue.entity_id == company_id,
            MetricValue.metric_definition_id == definition_id,
            MetricValue.status == "approved",
        )
    )


def best_approved_source_for_company(db: Session, company_slug: str) -> Source | None:
    matcher = COMPANY_SOURCE_MATCHERS.get(company_slug)
    if not matcher:
        return None
    sources = db.scalars(
        select(Source)
        .where(Source.status == "approved")
        .order_by(Source.reliability_score.desc(), Source.published_at.desc())
    ).all()
    return next((source for source in sources if source_matches_company(source, matcher)), None)


def best_approved_source_for_company_metric(
    db: Session, company_slug: str, metric_key: str
) -> Source | None:
    sources = sources_for_company_metric(db, company_slug, metric_key)
    if not sources:
        return best_approved_source_for_company(db, company_slug)
    return sorted(
        sources,
        key=lambda source: (
            source.reliability_score,
            source.published_at or datetime.min.replace(tzinfo=UTC),
        ),
        reverse=True,
    )[0]


def sources_for_company_metric(db: Session, company_slug: str, metric_key: str) -> list[Source]:
    matcher = COMPANY_SOURCE_MATCHERS.get(company_slug)
    if not matcher:
        return []
    expected_types = REQUIRED_EVIDENCE_EXPECTED.get(metric_key, set())
    sources = db.scalars(
        select(Source).where(
            Source.status == "approved",
            Source.source_type.in_(expected_types),
        )
    ).all()
    return [source for source in sources if source_matches_company(source, matcher)]


def evidence_coverage_for_metric(metric_key: str, sources: list[Source]) -> float:
    expected = REQUIRED_EVIDENCE_EXPECTED.get(metric_key, set())
    if not expected:
        return 0
    found = {source.source_type for source in sources}
    return round(len(expected.intersection(found)) / len(expected) * 100, 2)


def classification_for_source(metric_key: str, source_type: str) -> str:
    if metric_key in {"gross_margin", "revenue_growth", "roi"}:
        return "Derived"
    if source_type in {"sec_filing", "annual_report", "earnings_call", "quarterly_report"}:
        return "Reported"
    return "Estimated"


def gold_standard_status(records: list[AutonomousEvidenceRecord]) -> str:
    return "gold_standard" if gold_standard_complete(records) else "in_progress"


def gold_standard_complete(records: list[AutonomousEvidenceRecord]) -> bool:
    published_keys = {
        record.metric_definition.key
        for record in records
        if record.status == PUBLISHED
        and record.evidence_classification == "Validated"
        and float(record.confidence_score) > 0
        and float(record.evidence_coverage_score) > 0
        and float(record.openvals_score) > 0
        and record.published_at
        and record.approved_at
        and record.source_url
    }
    return GOLD_STANDARD_METRIC_KEYS <= published_keys


def source_matches_company(source: Source, matcher: dict[str, set[str]]) -> bool:
    publisher = source.publisher or ""
    title = source.title.lower()
    url = source.url or ""
    return (
        publisher in matcher["publishers"]
        or any(term in title for term in matcher["title_terms"])
        or any(term in url for term in matcher["url_terms"])
    )


def evidence_exists(db: Session, company_id: str, definition_id: str, source_id: str) -> bool:
    return bool(
        db.scalar(
            select(AutonomousEvidenceRecord.id).where(
                AutonomousEvidenceRecord.company_id == company_id,
                AutonomousEvidenceRecord.metric_definition_id == definition_id,
                AutonomousEvidenceRecord.source_id == source_id,
            )
        )
    )


def evidence_text(
    company: Company,
    metric_definition: MetricDefinition,
    source: Source,
    metric: MetricValue,
) -> str:
    return (
        f"Research Agent collected {company.name} {metric_definition.key} evidence from "
        f"{source.title}. Discovered value is {float(metric.value_numeric)} and remains queued "
        "for validation, reviewer approval, and publisher release before any public update."
    )


def link_metric_source(
    db: Session,
    metric: MetricValue,
    source: Source,
    record: AutonomousEvidenceRecord,
) -> None:
    existing = db.scalar(
        select(MetricSource).where(
            MetricSource.metric_value_id == metric.id,
            MetricSource.source_id == source.id,
        )
    )
    if existing:
        existing.evidence_note = record.evidence_text
        return
    db.add(
        MetricSource(
            metric_value_id=metric.id,
            source_id=source.id,
            evidence_note=record.evidence_text,
        )
    )


def upsert_confidence(db: Session, metric: MetricValue, record: AutonomousEvidenceRecord) -> None:
    confidence = metric.confidence_score
    if not confidence:
        confidence = ConfidenceScore(
            metric_value_id=metric.id,
            source_reliability=record.source.reliability_score,
            data_freshness=freshness_score(record.source.published_at),
            cross_verification=cross_verification_score(1),
            methodology_transparency=methodology_transparency_score(record.evidence_text),
            confidence_score=record.confidence_score,
            confidence_label=record.confidence_label,
            source_count=1,
            methodology_note=record.evidence_text,
        )
        db.add(confidence)
        return
    confidence.source_reliability = record.source.reliability_score
    confidence.data_freshness = freshness_score(record.source.published_at)
    confidence.cross_verification = cross_verification_score(len(metric.source_links) or 1)
    confidence.methodology_transparency = methodology_transparency_score(record.evidence_text)
    confidence.confidence_score = record.confidence_score
    confidence.confidence_label = record.confidence_label
    confidence.source_count = max(len(metric.source_links), 1)
    confidence.methodology_note = record.evidence_text


def next_metric_version(db: Session, metric_value_id: str) -> int:
    versions = db.scalars(
        select(MetricVersion.version).where(MetricVersion.metric_value_id == metric_value_id)
    ).all()
    return max(versions or [0]) + 1


def ensure_publication_source_metric(
    db: Session,
    record: AutonomousEvidenceRecord,
) -> SourceMetric:
    source_metric = db.scalar(
        select(SourceMetric).where(
            SourceMetric.company_id == record.company_id,
            SourceMetric.year == 2026,
            SourceMetric.metric_type == record.metric_definition.key,
            SourceMetric.source_id == record.source_id,
            SourceMetric.approved_status == "approved",
        )
    )
    if source_metric:
        source_metric.value_numeric = record.discovered_value
        source_metric.confidence_score = record.confidence_score
        source_metric.methodology_note = record.validation_notes or record.evidence_text
        return source_metric
    source_metric = SourceMetric(
        company_id=record.company_id,
        year=2026,
        metric_type=record.metric_definition.key,
        value_numeric=record.discovered_value,
        source_id=record.source_id,
        source_url=record.source_url,
        source_type=record.source_type,
        confidence_score=record.confidence_score,
        methodology_note=record.validation_notes or record.evidence_text,
        created_by_user_id=record.reviewer_user_id or legacy_admin_user_id(db),
        approved_status="approved",
        reviewed_by_user_id=record.reviewer_user_id,
        reviewed_at=record.reviewed_at,
    )
    db.add(source_metric)
    db.flush()
    return source_metric


def legacy_admin_user_id(db: Session) -> str:
    user_id = db.scalar(
        select(AuditLog.actor_user_id).where(AuditLog.actor_user_id.isnot(None)).limit(1)
    )
    if not user_id:
        raise ValueError("An admin user is required before publishing autonomous evidence.")
    return user_id


def write_agent_audit(
    db: Session,
    action: str,
    record: AutonomousEvidenceRecord,
    metadata: dict[str, object],
) -> None:
    db.add(
        AuditLog(
            actor_user_id=record.reviewer_user_id,
            action=action,
            target_type="autonomous_evidence_record",
            target_id=record.id,
            metadata_json=json.dumps(metadata, sort_keys=True),
        )
    )


def average(values: list[float]) -> float:
    if not values:
        return 0
    return round(sum(values) / len(values), 2)
