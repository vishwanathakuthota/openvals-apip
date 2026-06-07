from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def uuid_pk() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="analyst", index=True)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class ApiKey(TimestampMixin, Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    name: Mapped[str] = mapped_column(String(255))
    key_prefix: Mapped[str] = mapped_column(String(32), index=True)
    key_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(40), default="free", index=True)
    daily_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_count_today: Mapped[int] = mapped_column(Integer, default=0)
    usage_window_start: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_by: Mapped[User | None] = relationship()


class Country(TimestampMixin, Base):
    __tablename__ = "countries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    iso_code: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    region: Mapped[str | None] = mapped_column(String(80), nullable=True)


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    ticker: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    headquarters_country_id: Mapped[str | None] = mapped_column(
        ForeignKey("countries.id"), nullable=True
    )
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)


class Industry(TimestampMixin, Base):
    __tablename__ = "industries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)


class AIModel(TimestampMixin, Base):
    __tablename__ = "ai_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    provider_company_id: Mapped[str | None] = mapped_column(
        ForeignKey("companies.id"), nullable=True
    )
    model_family: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)


class MetricDefinition(TimestampMixin, Base):
    __tablename__ = "metric_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(40))
    higher_is_better: Mapped[int] = mapped_column(Integer, default=1)
    aggregation_method: Mapped[str] = mapped_column(String(80), default="latest")


class Source(TimestampMixin, Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    title: Mapped[str] = mapped_column(String(500))
    source_type: Mapped[str] = mapped_column(String(120), index=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reliability_score: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), default="approved", index=True)


class DataLineage(Base):
    __tablename__ = "data_lineage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    entity_type: Mapped[str] = mapped_column(String(40), index=True)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    source_url: Mapped[str] = mapped_column(String(1000))
    source_type: Mapped[str] = mapped_column(String(120), index=True)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2))
    imported_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    import_batch_id: Mapped[str] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(80), default="imported", index=True)
    metadata_json: Mapped[str] = mapped_column(Text)

    source: Mapped[Source] = relationship()
    imported_by: Mapped[User] = relationship()


class CompanyValidation(TimestampMixin, Base):
    __tablename__ = "company_validations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    openvals_validation_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    evidence_coverage_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    approved_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped[Company] = relationship()
    reviewed_by: Mapped[User | None] = relationship(foreign_keys=[reviewed_by_user_id])
    approved_by: Mapped[User | None] = relationship(foreign_keys=[approved_by_user_id])
    evidence_items: Mapped[list["CompanyValidationEvidence"]] = relationship(
        back_populates="validation"
    )
    source_reviews: Mapped[list["CompanyValidationSourceReview"]] = relationship(
        back_populates="validation"
    )


class CompanyValidationEvidence(TimestampMixin, Base):
    __tablename__ = "company_validation_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    validation_id: Mapped[str] = mapped_column(ForeignKey("company_validations.id"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    evidence_type: Mapped[str] = mapped_column(String(120), index=True)
    coverage_weight: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    review_status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    validation: Mapped[CompanyValidation] = relationship(back_populates="evidence_items")
    source: Mapped[Source] = relationship()
    reviewed_by: Mapped[User | None] = relationship()


class CompanyValidationSourceReview(TimestampMixin, Base):
    __tablename__ = "company_validation_source_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    validation_id: Mapped[str] = mapped_column(ForeignKey("company_validations.id"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    review_status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    validation: Mapped[CompanyValidation] = relationship(back_populates="source_reviews")
    source: Mapped[Source] = relationship()
    reviewed_by: Mapped[User | None] = relationship()


class CompanyValidationWorkspace(TimestampMixin, Base):
    __tablename__ = "company_validation_workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), unique=True, index=True)
    validation_id: Mapped[str | None] = mapped_column(
        ForeignKey("company_validations.id"), nullable=True, index=True
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    methodology_version: Mapped[str] = mapped_column(String(80), default="gold-standard-v1")
    evidence_coverage_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    openvals_validation_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    methodology_trace: Mapped[str] = mapped_column(Text)
    report_path: Mapped[str] = mapped_column(String(500))
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped[Company] = relationship()
    validation: Mapped[CompanyValidation | None] = relationship()
    sections: Mapped[list["CompanyValidationWorkspaceSection"]] = relationship(
        back_populates="workspace"
    )


class CompanyValidationWorkspaceSection(TimestampMixin, Base):
    __tablename__ = "company_validation_workspace_sections"
    __table_args__ = (
        UniqueConstraint("workspace_id", "section_key", name="uq_workspace_section_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("company_validation_workspaces.id"), index=True
    )
    section_key: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    required_source_types: Mapped[str] = mapped_column(Text)
    coverage_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    openvals_validation_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    methodology_trace: Mapped[str] = mapped_column(Text)
    lineage_json: Mapped[str] = mapped_column(Text)
    source_approval_status: Mapped[str] = mapped_column(String(40), default="pending", index=True)

    workspace: Mapped[CompanyValidationWorkspace] = relationship(back_populates="sections")
    evidence_links: Mapped[list["CompanyValidationWorkspaceEvidence"]] = relationship(
        back_populates="section"
    )


class CompanyValidationWorkspaceEvidence(TimestampMixin, Base):
    __tablename__ = "company_validation_workspace_evidence"
    __table_args__ = (
        UniqueConstraint("section_id", "source_id", name="uq_workspace_section_source"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    section_id: Mapped[str] = mapped_column(
        ForeignKey("company_validation_workspace_sections.id"), index=True
    )
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    evidence_role: Mapped[str] = mapped_column(String(120), index=True)
    approval_status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    methodology_trace: Mapped[str] = mapped_column(Text)
    lineage_snapshot_json: Mapped[str] = mapped_column(Text)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    section: Mapped[CompanyValidationWorkspaceSection] = relationship(
        back_populates="evidence_links"
    )
    source: Mapped[Source] = relationship()
    reviewed_by: Mapped[User | None] = relationship()


class ResearchQueueItem(TimestampMixin, Base):
    __tablename__ = "research_queue_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), unique=True, index=True)
    validation_id: Mapped[str | None] = mapped_column(
        ForeignKey("company_validations.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(40), default="not_started", index=True)
    priority: Mapped[str] = mapped_column(String(40), default="normal", index=True)
    assigned_to_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    reviewer_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    evidence_coverage_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped[Company] = relationship()
    validation: Mapped[CompanyValidation | None] = relationship()
    assigned_to: Mapped[User | None] = relationship(foreign_keys=[assigned_to_user_id])
    reviewer: Mapped[User | None] = relationship(foreign_keys=[reviewer_user_id])
    evidence_items: Mapped[list["ResearchEvidence"]] = relationship(back_populates="queue_item")


class ResearchEvidence(TimestampMixin, Base):
    __tablename__ = "research_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    queue_item_id: Mapped[str] = mapped_column(ForeignKey("research_queue_items.id"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    evidence_type: Mapped[str] = mapped_column(String(120), index=True)
    collection_status: Mapped[str] = mapped_column(String(40), default="collected", index=True)
    approval_status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    coverage_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    collected_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    reviewer_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    queue_item: Mapped[ResearchQueueItem] = relationship(back_populates="evidence_items")
    source: Mapped[Source] = relationship()
    collected_by: Mapped[User | None] = relationship(foreign_keys=[collected_by_user_id])
    reviewer: Mapped[User | None] = relationship(foreign_keys=[reviewer_user_id])


class ResearchAuditTrail(Base):
    __tablename__ = "research_audit_trail"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    queue_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("research_queue_items.id"), nullable=True, index=True
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(120), index=True)
    from_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    queue_item: Mapped[ResearchQueueItem | None] = relationship()
    actor: Mapped[User | None] = relationship()


class SourceMetric(TimestampMixin, Base):
    __tablename__ = "source_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    metric_type: Mapped[str] = mapped_column(String(120), index=True)
    value_numeric: Mapped[float] = mapped_column(Numeric(20, 6))
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    source_url: Mapped[str] = mapped_column(String(1000))
    source_type: Mapped[str] = mapped_column(String(120), index=True)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2))
    methodology_note: Mapped[str] = mapped_column(Text)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    approved_status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped[Company] = relationship()
    source: Mapped[Source] = relationship()
    created_by: Mapped[User] = relationship(foreign_keys=[created_by_user_id])
    reviewed_by: Mapped[User | None] = relationship(foreign_keys=[reviewed_by_user_id])


class MetricValue(TimestampMixin, Base):
    __tablename__ = "metric_values"
    __table_args__ = (
        UniqueConstraint(
            "metric_definition_id",
            "entity_type",
            "entity_id",
            "period_start",
            "period_end",
            name="uq_metric_entity_period",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    metric_definition_id: Mapped[str] = mapped_column(ForeignKey("metric_definitions.id"))
    entity_type: Mapped[str] = mapped_column(String(40), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    period_start: Mapped[datetime] = mapped_column(Date)
    period_end: Mapped[datetime] = mapped_column(Date)
    value_numeric: Mapped[float] = mapped_column(Numeric(20, 6))
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    methodology: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="approved", index=True)
    evidence_classification: Mapped[str] = mapped_column(String(40), default="Derived", index=True)
    validation_status: Mapped[str] = mapped_column(String(40), default="Published", index=True)
    evidence_coverage_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    openvals_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    metric_definition: Mapped[MetricDefinition] = relationship()
    confidence_score: Mapped["ConfidenceScore"] = relationship(back_populates="metric_value")
    source_links: Mapped[list["MetricSource"]] = relationship(back_populates="metric_value")
    autonomous_evidence_records: Mapped[list["AutonomousEvidenceRecord"]] = relationship(
        back_populates="metric_value"
    )


class AutonomousEvidenceRecord(TimestampMixin, Base):
    __tablename__ = "autonomous_evidence_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True)
    metric_definition_id: Mapped[str] = mapped_column(
        ForeignKey("metric_definitions.id"), index=True
    )
    metric_value_id: Mapped[str | None] = mapped_column(
        ForeignKey("metric_values.id"), nullable=True, index=True
    )
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    previous_value: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    discovered_value: Mapped[float] = mapped_column(Numeric(20, 6))
    source_url: Mapped[str] = mapped_column(String(1000))
    source_type: Mapped[str] = mapped_column(String(120), index=True)
    evidence_text: Mapped[str] = mapped_column(Text)
    collection_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    collection_method: Mapped[str] = mapped_column(String(120), default="approved_source_registry")
    status: Mapped[str] = mapped_column(String(40), default="Collected", index=True)
    evidence_classification: Mapped[str] = mapped_column(String(40), default="Reported", index=True)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    confidence_label: Mapped[str] = mapped_column(String(80), default="Speculative")
    evidence_coverage_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    validation_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    openvals_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    transparency_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    reproducibility_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    source_quality_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    validation_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    validation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_status: Mapped[str] = mapped_column(String(40), default="Collected", index=True)
    approval_recommendation: Mapped[str | None] = mapped_column(
        String(80), nullable=True, index=True
    )
    reviewer_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_decision: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)

    company: Mapped[Company] = relationship()
    metric_definition: Mapped[MetricDefinition] = relationship()
    metric_value: Mapped[MetricValue | None] = relationship(
        back_populates="autonomous_evidence_records"
    )
    source: Mapped[Source] = relationship()
    reviewer: Mapped[User | None] = relationship()


class TrustIndexSnapshot(Base):
    __tablename__ = "trust_index_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    entity_type: Mapped[str] = mapped_column(String(40), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    entity_name: Mapped[str] = mapped_column(String(255), index=True)
    trust_index: Mapped[float] = mapped_column(Numeric(5, 2))
    trust_rating: Mapped[str] = mapped_column(String(80), index=True)
    trust_classification: Mapped[str] = mapped_column(String(80), index=True)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2))
    evidence_coverage_score: Mapped[float] = mapped_column(Numeric(5, 2))
    transparency_score: Mapped[float] = mapped_column(Numeric(5, 2))
    reproducibility_score: Mapped[float] = mapped_column(Numeric(5, 2))
    source_quality_score: Mapped[float] = mapped_column(Numeric(5, 2))
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    published_record_count: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    methodology_version: Mapped[str] = mapped_column(String(80), default="trust-index-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TrustChangeNotification(Base):
    __tablename__ = "trust_change_notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    entity_type: Mapped[str] = mapped_column(String(40), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    entity_name: Mapped[str] = mapped_column(String(255), index=True)
    previous_trust_index: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    current_trust_index: Mapped[float] = mapped_column(Numeric(5, 2))
    change_amount: Mapped[float] = mapped_column(Numeric(5, 2))
    notification_type: Mapped[str] = mapped_column(String(80), index=True)
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="unread", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MetricSource(TimestampMixin, Base):
    __tablename__ = "metric_sources"
    __table_args__ = (
        UniqueConstraint("metric_value_id", "source_id", name="uq_metric_source_link"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    metric_value_id: Mapped[str] = mapped_column(ForeignKey("metric_values.id"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    evidence_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    metric_value: Mapped[MetricValue] = relationship(back_populates="source_links")
    source: Mapped[Source] = relationship()


class MetricVersion(TimestampMixin, Base):
    __tablename__ = "metric_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    source_metric_id: Mapped[str] = mapped_column(ForeignKey("source_metrics.id"), index=True)
    metric_value_id: Mapped[str | None] = mapped_column(
        ForeignKey("metric_values.id"), nullable=True, index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    value_numeric: Mapped[float] = mapped_column(Numeric(20, 6))
    approved_status: Mapped[str] = mapped_column(String(40), index=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)

    source_metric: Mapped[SourceMetric] = relationship()
    metric_value: Mapped[MetricValue | None] = relationship()
    created_by: Mapped[User] = relationship()


class ConfidenceScore(TimestampMixin, Base):
    __tablename__ = "confidence_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    metric_value_id: Mapped[str] = mapped_column(ForeignKey("metric_values.id"), unique=True)
    source_reliability: Mapped[int] = mapped_column(Integer)
    data_freshness: Mapped[int] = mapped_column(Integer)
    cross_verification: Mapped[int] = mapped_column(Integer)
    methodology_transparency: Mapped[int] = mapped_column(Integer)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2))
    confidence_label: Mapped[str] = mapped_column(String(80))
    source_count: Mapped[int] = mapped_column(Integer)
    methodology_note: Mapped[str] = mapped_column(Text)

    metric_value: Mapped[MetricValue] = relationship(back_populates="confidence_score")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_pk)
    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(120), index=True)
    target_type: Mapped[str] = mapped_column(String(120), index=True)
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    metadata_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    actor: Mapped[User | None] = relationship()
