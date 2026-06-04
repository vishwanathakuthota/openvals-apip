"""backend v1 schema

Revision ID: 20260604_0001
Revises:
Create Date: 2026-06-04
"""

import sqlalchemy as sa
from alembic import op

revision = "20260604_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_status", "users", ["status"])

    op.create_table(
        "countries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("iso_code", sa.String(length=2), nullable=False),
        sa.Column("region", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_countries_name", "countries", ["name"])
    op.create_index("ix_countries_slug", "countries", ["slug"], unique=True)
    op.create_index("ix_countries_iso_code", "countries", ["iso_code"], unique=True)

    op.create_table(
        "industries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_industries_name", "industries", ["name"])
    op.create_index("ix_industries_slug", "industries", ["slug"], unique=True)
    op.create_index("ix_industries_status", "industries", ["status"])

    op.create_table(
        "companies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=True),
        sa.Column("headquarters_country_id", sa.String(length=36), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["headquarters_country_id"], ["countries.id"]),
    )
    op.create_index("ix_companies_name", "companies", ["name"])
    op.create_index("ix_companies_slug", "companies", ["slug"], unique=True)
    op.create_index("ix_companies_ticker", "companies", ["ticker"])
    op.create_index("ix_companies_status", "companies", ["status"])

    op.create_table(
        "ai_models",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("provider_company_id", sa.String(length=36), nullable=True),
        sa.Column("model_family", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["provider_company_id"], ["companies.id"]),
    )
    op.create_index("ix_ai_models_name", "ai_models", ["name"])
    op.create_index("ix_ai_models_slug", "ai_models", ["slug"], unique=True)
    op.create_index("ix_ai_models_model_family", "ai_models", ["model_family"])
    op.create_index("ix_ai_models_status", "ai_models", ["status"])

    op.create_table(
        "metric_definitions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("higher_is_better", sa.Integer(), nullable=False),
        sa.Column("aggregation_method", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_metric_definitions_key", "metric_definitions", ["key"], unique=True)

    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source_type", sa.String(length=120), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reliability_score", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_sources_source_type", "sources", ["source_type"])
    op.create_index("ix_sources_status", "sources", ["status"])

    op.create_table(
        "source_metrics",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("metric_type", sa.String(length=120), nullable=False),
        sa.Column("value_numeric", sa.Numeric(20, 6), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_type", sa.String(length=120), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("methodology_note", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("approved_status", sa.String(length=40), nullable=False),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
    )
    op.create_index("ix_source_metrics_company_id", "source_metrics", ["company_id"])
    op.create_index("ix_source_metrics_year", "source_metrics", ["year"])
    op.create_index("ix_source_metrics_metric_type", "source_metrics", ["metric_type"])
    op.create_index("ix_source_metrics_source_id", "source_metrics", ["source_id"])
    op.create_index("ix_source_metrics_source_type", "source_metrics", ["source_type"])
    op.create_index(
        "ix_source_metrics_created_by_user_id", "source_metrics", ["created_by_user_id"]
    )
    op.create_index("ix_source_metrics_approved_status", "source_metrics", ["approved_status"])

    op.create_table(
        "metric_values",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("metric_definition_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("value_numeric", sa.Numeric(20, 6), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("methodology", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["metric_definition_id"], ["metric_definitions.id"]),
        sa.UniqueConstraint(
            "metric_definition_id",
            "entity_type",
            "entity_id",
            "period_start",
            "period_end",
            name="uq_metric_entity_period",
        ),
    )
    op.create_index("ix_metric_values_entity_type", "metric_values", ["entity_type"])
    op.create_index("ix_metric_values_entity_id", "metric_values", ["entity_id"])
    op.create_index("ix_metric_values_status", "metric_values", ["status"])

    op.create_table(
        "metric_sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("metric_value_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["metric_value_id"], ["metric_values.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.UniqueConstraint("metric_value_id", "source_id", name="uq_metric_source_link"),
    )
    op.create_index("ix_metric_sources_metric_value_id", "metric_sources", ["metric_value_id"])
    op.create_index("ix_metric_sources_source_id", "metric_sources", ["source_id"])

    op.create_table(
        "metric_versions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_metric_id", sa.String(length=36), nullable=False),
        sa.Column("metric_value_id", sa.String(length=36), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("value_numeric", sa.Numeric(20, 6), nullable=False),
        sa.Column("approved_status", sa.String(length=40), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["source_metric_id"], ["source_metrics.id"]),
        sa.ForeignKeyConstraint(["metric_value_id"], ["metric_values.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
    )
    op.create_index("ix_metric_versions_source_metric_id", "metric_versions", ["source_metric_id"])
    op.create_index("ix_metric_versions_metric_value_id", "metric_versions", ["metric_value_id"])
    op.create_index("ix_metric_versions_approved_status", "metric_versions", ["approved_status"])
    op.create_index(
        "ix_metric_versions_created_by_user_id", "metric_versions", ["created_by_user_id"]
    )

    op.create_table(
        "confidence_scores",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("metric_value_id", sa.String(length=36), nullable=False),
        sa.Column("source_reliability", sa.Integer(), nullable=False),
        sa.Column("data_freshness", sa.Integer(), nullable=False),
        sa.Column("cross_verification", sa.Integer(), nullable=False),
        sa.Column("methodology_transparency", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("confidence_label", sa.String(length=80), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("methodology_note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["metric_value_id"], ["metric_values.id"]),
    )
    op.create_index(
        "ix_confidence_scores_metric_value_id",
        "confidence_scores",
        ["metric_value_id"],
        unique=True,
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("target_type", sa.String(length=120), nullable=False),
        sa.Column("target_id", sa.String(length=36), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
    )
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_target_type", "audit_logs", ["target_type"])
    op.create_index("ix_audit_logs_target_id", "audit_logs", ["target_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("confidence_scores")
    op.drop_table("metric_versions")
    op.drop_table("metric_sources")
    op.drop_table("metric_values")
    op.drop_table("source_metrics")
    op.drop_table("sources")
    op.drop_table("metric_definitions")
    op.drop_table("ai_models")
    op.drop_table("companies")
    op.drop_table("industries")
    op.drop_table("countries")
    op.drop_table("users")
