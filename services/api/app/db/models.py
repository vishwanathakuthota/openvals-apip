from datetime import datetime
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

    metric_definition: Mapped[MetricDefinition] = relationship()
    confidence_score: Mapped["ConfidenceScore"] = relationship(back_populates="metric_value")
    source_links: Mapped[list["MetricSource"]] = relationship(back_populates="metric_value")


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
