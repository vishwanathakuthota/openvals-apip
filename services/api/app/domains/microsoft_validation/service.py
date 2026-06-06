import json
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AuditLog,
    Company,
    CompanyValidation,
    CompanyValidationWorkspace,
    CompanyValidationWorkspaceEvidence,
    CompanyValidationWorkspaceSection,
    Source,
)
from app.domains.sources.credibility import source_credibility_score, source_tier
from app.domains.validation.service import (
    attach_source_evidence,
    ensure_company_validation,
    ensure_source_review,
    recalculate_company_validation,
    validation_label,
)

MICROSOFT_WORKSPACE_SLUG = "microsoft"
MICROSOFT_REPORT_PATH = "/companies/microsoft/validation-report"
MICROSOFT_SECTION_SOURCE_MAP = {
    "revenue_evidence": ["sec_filing", "annual_report"],
    "ai_revenue_evidence": ["annual_report", "earnings_call", "investor_presentation"],
    "ai_investment_evidence": ["sec_filing", "annual_report", "earnings_call"],
    "infrastructure_investment_evidence": [
        "annual_report",
        "earnings_call",
        "investor_presentation",
    ],
    "earnings_call_evidence": ["earnings_call"],
    "investor_presentation_evidence": ["investor_presentation"],
}


@dataclass(frozen=True)
class MicrosoftValidationSectionSpec:
    key: str
    title: str
    description: str
    required_source_types: list[str]
    reviewer_notes: str
    methodology_trace: str


MICROSOFT_VALIDATION_SECTIONS = [
    MicrosoftValidationSectionSpec(
        key="revenue_evidence",
        title="Revenue Evidence",
        description="Validates Microsoft total revenue context before AI attribution.",
        required_source_types=MICROSOFT_SECTION_SOURCE_MAP["revenue_evidence"],
        reviewer_notes="Revenue baseline uses audited filing and annual report evidence.",
        methodology_trace=(
            "Trace revenue baseline to Microsoft SEC filing registry and annual report before "
            "using it as denominator or reconciliation context for AI-specific estimates."
        ),
    ),
    MicrosoftValidationSectionSpec(
        key="ai_revenue_evidence",
        title="AI Revenue Evidence",
        description=(
            "Tracks AI-related revenue signals across cloud, Copilot, and AI "
            "product disclosures."
        ),
        required_source_types=MICROSOFT_SECTION_SOURCE_MAP["ai_revenue_evidence"],
        reviewer_notes=(
            "AI revenue remains a sourced estimate because Microsoft does not "
            "report a full audited AI segment."
        ),
        methodology_trace=(
            "Use public company evidence to map AI revenue signals to APIP metric definitions; "
            "label direct disclosure gaps in methodology notes."
        ),
    ),
    MicrosoftValidationSectionSpec(
        key="ai_investment_evidence",
        title="AI Investment Evidence",
        description=(
            "Tracks AI investment commitments, operating spend, and AI product "
            "investment disclosures."
        ),
        required_source_types=MICROSOFT_SECTION_SOURCE_MAP["ai_investment_evidence"],
        reviewer_notes=(
            "AI investment evidence is cross-checked against filings and earnings "
            "commentary."
        ),
        methodology_trace=(
            "Separate AI investment from general R&D where possible, and preserve source-level "
            "lineage when a metric uses infrastructure or product investment proxies."
        ),
    ),
    MicrosoftValidationSectionSpec(
        key="infrastructure_investment_evidence",
        title="Infrastructure Investment Evidence",
        description=(
            "Validates cloud, data center, accelerator, and AI infrastructure "
            "investment signals."
        ),
        required_source_types=MICROSOFT_SECTION_SOURCE_MAP["infrastructure_investment_evidence"],
        reviewer_notes=(
            "Infrastructure investment is tracked separately because it is a major "
            "AI economics driver."
        ),
        methodology_trace=(
            "Map infrastructure evidence to AI spend methodology only when the source explicitly "
            "connects capacity, cloud, or data center investment to AI demand."
        ),
    ),
    MicrosoftValidationSectionSpec(
        key="earnings_call_evidence",
        title="Earnings Call Evidence",
        description=(
            "Captures management commentary and call transcript evidence used for "
            "cross verification."
        ),
        required_source_types=MICROSOFT_SECTION_SOURCE_MAP["earnings_call_evidence"],
        reviewer_notes=(
            "Earnings call evidence is approved when the transcript source is "
            "attributable and dated."
        ),
        methodology_trace=(
            "Use earnings calls for management commentary and cross-verification, "
            "not as standalone audited financial proof."
        ),
    ),
    MicrosoftValidationSectionSpec(
        key="investor_presentation_evidence",
        title="Investor Presentation Evidence",
        description=(
            "Tracks investor presentation and deck evidence used to explain AI "
            "product and investment claims."
        ),
        required_source_types=MICROSOFT_SECTION_SOURCE_MAP["investor_presentation_evidence"],
        reviewer_notes="Investor presentation evidence is approved as Tier 2 source support.",
        methodology_trace=(
            "Use investor presentations for traceable company statements and reconcile them back "
            "to filings, annual reports, or earnings calls where possible."
        ),
    ),
]


def ensure_microsoft_validation_workspace(
    db: Session,
    reviewer_user_id: str | None = None,
) -> CompanyValidationWorkspace:
    company = db.scalar(select(Company).where(Company.slug == MICROSOFT_WORKSPACE_SLUG))
    if not company:
        raise ValueError("Microsoft company seed record is required.")
    validation = ensure_company_validation(db, company)
    workspace = db.scalar(
        select(CompanyValidationWorkspace).where(
            CompanyValidationWorkspace.slug == MICROSOFT_WORKSPACE_SLUG
        )
    )
    if not workspace:
        workspace = CompanyValidationWorkspace(
            company_id=company.id,
            validation_id=validation.id,
            slug=MICROSOFT_WORKSPACE_SLUG,
            status="under_review",
            methodology_version="gold-standard-v1",
            reviewer_notes="Gold standard Microsoft validation workspace initialized for V1 beta.",
            methodology_trace=workspace_methodology_trace(),
            report_path=MICROSOFT_REPORT_PATH,
        )
        db.add(workspace)
        db.flush()
    else:
        workspace.company_id = company.id
        workspace.validation_id = validation.id
        workspace.methodology_trace = workspace_methodology_trace()
        workspace.report_path = MICROSOFT_REPORT_PATH

    for spec in MICROSOFT_VALIDATION_SECTIONS:
        ensure_workspace_section(db, workspace, validation, spec, reviewer_user_id)
    recalculate_workspace_scores(workspace)
    workspace.exported_at = datetime.now(UTC)
    return workspace


def ensure_workspace_section(
    db: Session,
    workspace: CompanyValidationWorkspace,
    validation: CompanyValidation,
    spec: MicrosoftValidationSectionSpec,
    reviewer_user_id: str | None,
) -> CompanyValidationWorkspaceSection:
    section = db.scalar(
        select(CompanyValidationWorkspaceSection).where(
            CompanyValidationWorkspaceSection.workspace_id == workspace.id,
            CompanyValidationWorkspaceSection.section_key == spec.key,
        )
    )
    if not section:
        section = CompanyValidationWorkspaceSection(
            workspace_id=workspace.id,
            section_key=spec.key,
            title=spec.title,
            description=spec.description,
            required_source_types=json.dumps(spec.required_source_types),
            reviewer_notes=spec.reviewer_notes,
            methodology_trace=spec.methodology_trace,
            lineage_json="[]",
            source_approval_status="pending",
        )
        db.add(section)
        db.flush()
    else:
        section.title = spec.title
        section.description = spec.description
        section.required_source_types = json.dumps(spec.required_source_types)
        section.reviewer_notes = spec.reviewer_notes
        section.methodology_trace = spec.methodology_trace

    sources = microsoft_sources_for_section(db, spec.required_source_types)
    for source in sources:
        attach_source_evidence(
            db,
            validation,
            source,
            evidence_type=spec.key,
            review_status="approved",
        )
        ensure_source_review(db, validation, source, review_status="approved")
        ensure_workspace_evidence(db, section, source, spec, reviewer_user_id)
    section.lineage_json = json.dumps([source_lineage(source, spec.key) for source in sources])
    recalculate_section_score(section)
    recalculate_company_validation(validation)
    return section


def ensure_workspace_evidence(
    db: Session,
    section: CompanyValidationWorkspaceSection,
    source: Source,
    spec: MicrosoftValidationSectionSpec,
    reviewer_user_id: str | None,
) -> CompanyValidationWorkspaceEvidence:
    evidence = db.scalar(
        select(CompanyValidationWorkspaceEvidence).where(
            CompanyValidationWorkspaceEvidence.section_id == section.id,
            CompanyValidationWorkspaceEvidence.source_id == source.id,
        )
    )
    snapshot = source_lineage(source, spec.key)
    if not evidence:
        evidence = CompanyValidationWorkspaceEvidence(
            section_id=section.id,
            source_id=source.id,
            evidence_role=spec.key,
            approval_status="approved",
            reviewer_notes=f"Approved for {spec.title}.",
            methodology_trace=spec.methodology_trace,
            lineage_snapshot_json=json.dumps(snapshot),
            reviewed_by_user_id=reviewer_user_id,
            reviewed_at=datetime.now(UTC),
        )
        db.add(evidence)
        db.flush()
    else:
        evidence.evidence_role = spec.key
        evidence.methodology_trace = spec.methodology_trace
        evidence.lineage_snapshot_json = json.dumps(snapshot)
        evidence.reviewed_by_user_id = reviewer_user_id or evidence.reviewed_by_user_id
        evidence.reviewed_at = evidence.reviewed_at or datetime.now(UTC)
    return evidence


def review_workspace_source(
    workspace_evidence: CompanyValidationWorkspaceEvidence,
    approval_status: str,
    reviewer_notes: str | None,
    reviewer_user_id: str,
) -> None:
    normalized = normalize_approval_status(approval_status)
    workspace_evidence.approval_status = normalized
    workspace_evidence.reviewer_notes = reviewer_notes
    workspace_evidence.reviewed_by_user_id = reviewer_user_id
    workspace_evidence.reviewed_at = datetime.now(UTC)
    workspace_evidence.source.status = (
        "approved" if normalized in {"approved", "verified"} else "rejected"
    )
    recalculate_section_score(workspace_evidence.section)
    recalculate_workspace_scores(workspace_evidence.section.workspace)


def recalculate_workspace_scores(workspace: CompanyValidationWorkspace) -> None:
    sections = list(workspace.sections)
    if not sections:
        workspace.evidence_coverage_score = 0
        workspace.openvals_validation_score = 0
        return
    workspace.evidence_coverage_score = round(
        sum(float(section.coverage_score) for section in sections) / len(sections), 2
    )
    workspace.openvals_validation_score = round(
        sum(float(section.openvals_validation_score) for section in sections) / len(sections),
        2,
    )


def recalculate_section_score(section: CompanyValidationWorkspaceSection) -> None:
    required_source_types = set(json.loads(section.required_source_types))
    approved_links = [
        link for link in section.evidence_links if link.approval_status in {"approved", "verified"}
    ]
    approved_source_types = {link.source.source_type for link in approved_links}
    coverage = (
        len(required_source_types.intersection(approved_source_types))
        / len(required_source_types)
        * 100
        if required_source_types
        else 0
    )
    credibility = average(
        [
            source_credibility_score(link.source.source_type, link.source.published_at)
            for link in approved_links
        ]
    )
    approval_ratio = (
        len(approved_links) / len(section.evidence_links) if section.evidence_links else 0
    )
    section.coverage_score = round(coverage, 2)
    section.openvals_validation_score = round(
        (coverage * 0.45) + (credibility * 0.40) + (approval_ratio * 100 * 0.15),
        2,
    )
    section.source_approval_status = "approved" if coverage >= 100 and approved_links else "partial"


def microsoft_validation_report_payload(
    workspace: CompanyValidationWorkspace,
) -> dict[str, object]:
    sections = [workspace_section_payload(section) for section in sorted_sections(workspace)]
    return {
        "id": workspace.id,
        "company": workspace.company.name,
        "company_slug": workspace.company.slug,
        "status": workspace.status,
        "report_path": workspace.report_path,
        "methodology_version": workspace.methodology_version,
        "methodology_trace": workspace.methodology_trace,
        "reviewer_notes": workspace.reviewer_notes,
        "evidence_coverage_score": float(workspace.evidence_coverage_score),
        "openvals_validation_score": float(workspace.openvals_validation_score),
        "openvals_validation_label": validation_label(float(workspace.openvals_validation_score)),
        "exported_at": workspace.exported_at.isoformat() if workspace.exported_at else None,
        "last_updated": workspace.updated_at.isoformat() if workspace.updated_at else None,
        "sections": sections,
        "source_lineage": [lineage for section in sections for lineage in section["lineage"]],
    }


def workspace_section_payload(section: CompanyValidationWorkspaceSection) -> dict[str, object]:
    evidence = [
        workspace_evidence_payload(link)
        for link in sorted(section.evidence_links, key=lambda item: item.source.title)
    ]
    return {
        "id": section.id,
        "section_key": section.section_key,
        "title": section.title,
        "description": section.description,
        "required_source_types": json.loads(section.required_source_types),
        "coverage_score": float(section.coverage_score),
        "openvals_validation_score": float(section.openvals_validation_score),
        "reviewer_notes": section.reviewer_notes,
        "source_approval_status": section.source_approval_status,
        "methodology_trace": section.methodology_trace,
        "lineage": json.loads(section.lineage_json),
        "evidence": evidence,
    }


def workspace_evidence_payload(
    evidence: CompanyValidationWorkspaceEvidence,
) -> dict[str, object]:
    return {
        "id": evidence.id,
        "evidence_role": evidence.evidence_role,
        "approval_status": evidence.approval_status,
        "reviewer_notes": evidence.reviewer_notes,
        "methodology_trace": evidence.methodology_trace,
        "lineage_snapshot": json.loads(evidence.lineage_snapshot_json),
        "reviewed_by": evidence.reviewed_by.full_name if evidence.reviewed_by else None,
        "reviewed_at": evidence.reviewed_at.isoformat() if evidence.reviewed_at else None,
        "source": source_payload(evidence.source),
    }


def source_payload(source: Source) -> dict[str, object]:
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "source_tier": source_tier(source.source_type),
        "credibility_score": source_credibility_score(source.source_type, source.published_at),
        "publisher": source.publisher,
        "url": source.url,
        "published_at": source.published_at.isoformat() if source.published_at else None,
        "reliability_score": source.reliability_score,
        "status": source.status,
    }


def microsoft_sources_for_section(db: Session, source_types: list[str]) -> list[Source]:
    sources = db.scalars(
        select(Source).where(
            Source.publisher.in_(["SEC EDGAR", "Microsoft Investor Relations"]),
            Source.source_type.in_(source_types),
        )
    ).all()
    return sorted(sources, key=lambda source: (source_tier(source.source_type), source.title))


def source_lineage(source: Source, section_key: str) -> dict[str, object]:
    return {
        "source_id": source.id,
        "source_url": source.url,
        "source_type": source.source_type,
        "source_tier": source_tier(source.source_type),
        "publisher": source.publisher,
        "published_at": source.published_at.isoformat() if source.published_at else None,
        "reliability_score": source.reliability_score,
        "credibility_score": source_credibility_score(source.source_type, source.published_at),
        "section_key": section_key,
        "captured_at": datetime.now(UTC).isoformat(),
    }


def write_workspace_audit_log(
    db: Session,
    actor_user_id: str | None,
    action: str,
    workspace: CompanyValidationWorkspace,
    metadata: dict[str, object] | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type="company_validation_workspace",
            target_id=workspace.id,
            metadata_json=json.dumps(metadata or {}, sort_keys=True),
        )
    )


def sorted_sections(
    workspace: CompanyValidationWorkspace,
) -> list[CompanyValidationWorkspaceSection]:
    order = {spec.key: index for index, spec in enumerate(MICROSOFT_VALIDATION_SECTIONS)}
    return sorted(workspace.sections, key=lambda section: order.get(section.section_key, 999))


def workspace_methodology_trace() -> str:
    return (
        "Gold Standard v1 validates Microsoft through six required evidence sections. "
        "Each section stores source lineage, reviewer notes, approval status, and "
        "methodology traceability. Workspace coverage is the average section "
        "coverage. Workspace OpenVals score is the average section score, where "
        "each section uses coverage 45%, source credibility 40%, and "
        "approved-source ratio 15%."
    )


def normalize_approval_status(status: str) -> str:
    normalized = status.strip().lower().replace("-", "_")
    if normalized not in {"pending", "approved", "verified", "rejected"}:
        return "pending"
    return normalized


def average(values: list[int]) -> float:
    if not values:
        return 0
    return round(sum(values) / len(values), 2)
