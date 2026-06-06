"""Add autonomous research operations lifecycle records.

Revision ID: 20260605_0006
Revises: 20260605_0005
Create Date: 2026-06-05 00:06:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260605_0006"
down_revision: str | None = "20260605_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "metric_values",
        sa.Column(
            "evidence_classification",
            sa.String(length=40),
            nullable=False,
            server_default="Derived",
        ),
    )
    op.add_column(
        "metric_values",
        sa.Column(
            "validation_status", sa.String(length=40), nullable=False, server_default="Published"
        ),
    )
    op.add_column(
        "metric_values",
        sa.Column("evidence_coverage_score", sa.Numeric(5, 2), nullable=True),
    )
    op.add_column(
        "metric_values",
        sa.Column("openvals_score", sa.Numeric(5, 2), nullable=True),
    )
    op.create_index(
        "ix_metric_values_evidence_classification", "metric_values", ["evidence_classification"]
    )
    op.create_index("ix_metric_values_validation_status", "metric_values", ["validation_status"])

    op.create_table(
        "autonomous_evidence_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("metric_definition_id", sa.String(length=36), nullable=False),
        sa.Column("metric_value_id", sa.String(length=36), nullable=True),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("previous_value", sa.Numeric(20, 6), nullable=True),
        sa.Column("discovered_value", sa.Numeric(20, 6), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_type", sa.String(length=120), nullable=False),
        sa.Column("evidence_text", sa.Text(), nullable=False),
        sa.Column("collection_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("collection_method", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("evidence_classification", sa.String(length=40), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("confidence_label", sa.String(length=80), nullable=False),
        sa.Column("evidence_coverage_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("validation_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("openvals_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("transparency_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("reproducibility_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("source_quality_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("validation_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validation_notes", sa.Text(), nullable=True),
        sa.Column("validation_status", sa.String(length=40), nullable=False),
        sa.Column("approval_recommendation", sa.String(length=80), nullable=True),
        sa.Column("reviewer_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer_decision", sa.String(length=80), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["metric_definition_id"], ["metric_definitions.id"]),
        sa.ForeignKeyConstraint(["metric_value_id"], ["metric_values.id"]),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_autonomous_evidence_records_approval_recommendation",
        "autonomous_evidence_records",
        ["approval_recommendation"],
    )
    op.create_index(
        "ix_autonomous_evidence_records_company_id", "autonomous_evidence_records", ["company_id"]
    )
    op.create_index(
        "ix_autonomous_evidence_records_evidence_classification",
        "autonomous_evidence_records",
        ["evidence_classification"],
    )
    op.create_index(
        "ix_autonomous_evidence_records_metric_definition_id",
        "autonomous_evidence_records",
        ["metric_definition_id"],
    )
    op.create_index(
        "ix_autonomous_evidence_records_metric_value_id",
        "autonomous_evidence_records",
        ["metric_value_id"],
    )
    op.create_index(
        "ix_autonomous_evidence_records_reviewer_decision",
        "autonomous_evidence_records",
        ["reviewer_decision"],
    )
    op.create_index(
        "ix_autonomous_evidence_records_reviewer_user_id",
        "autonomous_evidence_records",
        ["reviewer_user_id"],
    )
    op.create_index(
        "ix_autonomous_evidence_records_source_id", "autonomous_evidence_records", ["source_id"]
    )
    op.create_index(
        "ix_autonomous_evidence_records_source_type", "autonomous_evidence_records", ["source_type"]
    )
    op.create_index(
        "ix_autonomous_evidence_records_status", "autonomous_evidence_records", ["status"]
    )
    op.create_index(
        "ix_autonomous_evidence_records_validation_status",
        "autonomous_evidence_records",
        ["validation_status"],
    )


def downgrade() -> None:
    op.drop_table("autonomous_evidence_records")
    op.drop_index("ix_metric_values_validation_status", table_name="metric_values")
    op.drop_index("ix_metric_values_evidence_classification", table_name="metric_values")
    op.drop_column("metric_values", "openvals_score")
    op.drop_column("metric_values", "evidence_coverage_score")
    op.drop_column("metric_values", "validation_status")
    op.drop_column("metric_values", "evidence_classification")
