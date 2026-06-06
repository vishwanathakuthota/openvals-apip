"""company validation framework

Revision ID: 20260605_0003
Revises: 20260605_0002
Create Date: 2026-06-05
"""

import sqlalchemy as sa
from alembic import op

revision = "20260605_0003"
down_revision = "20260605_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company_validations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("openvals_validation_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("evidence_coverage_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("approved_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_company_validations_company_id", "company_validations", ["company_id"], unique=True
    )
    op.create_index("ix_company_validations_status", "company_validations", ["status"])
    op.create_index(
        "ix_company_validations_reviewed_by_user_id",
        "company_validations",
        ["reviewed_by_user_id"],
    )
    op.create_index(
        "ix_company_validations_approved_by_user_id",
        "company_validations",
        ["approved_by_user_id"],
    )

    op.create_table(
        "company_validation_evidence",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("validation_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_type", sa.String(length=120), nullable=False),
        sa.Column("coverage_weight", sa.Numeric(5, 2), nullable=False),
        sa.Column("review_status", sa.String(length=40), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["validation_id"], ["company_validations.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_company_validation_evidence_validation_id",
        "company_validation_evidence",
        ["validation_id"],
    )
    op.create_index(
        "ix_company_validation_evidence_source_id", "company_validation_evidence", ["source_id"]
    )
    op.create_index(
        "ix_company_validation_evidence_evidence_type",
        "company_validation_evidence",
        ["evidence_type"],
    )
    op.create_index(
        "ix_company_validation_evidence_review_status",
        "company_validation_evidence",
        ["review_status"],
    )
    op.create_index(
        "ix_company_validation_evidence_reviewed_by_user_id",
        "company_validation_evidence",
        ["reviewed_by_user_id"],
    )

    op.create_table(
        "company_validation_source_reviews",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("validation_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("review_status", sa.String(length=40), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["validation_id"], ["company_validations.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_company_validation_source_reviews_validation_id",
        "company_validation_source_reviews",
        ["validation_id"],
    )
    op.create_index(
        "ix_company_validation_source_reviews_source_id",
        "company_validation_source_reviews",
        ["source_id"],
    )
    op.create_index(
        "ix_company_validation_source_reviews_review_status",
        "company_validation_source_reviews",
        ["review_status"],
    )
    op.create_index(
        "ix_company_validation_source_reviews_reviewed_by_user_id",
        "company_validation_source_reviews",
        ["reviewed_by_user_id"],
    )


def downgrade() -> None:
    op.drop_table("company_validation_source_reviews")
    op.drop_table("company_validation_evidence")
    op.drop_table("company_validations")
