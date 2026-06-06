"""Add Microsoft validation workspace tables.

Revision ID: 20260605_0005
Revises: 20260605_0004
Create Date: 2026-06-05 00:05:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260605_0005"
down_revision: str | None = "20260605_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_validation_workspaces",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("validation_id", sa.String(length=36), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("methodology_version", sa.String(length=80), nullable=False),
        sa.Column("evidence_coverage_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("openvals_validation_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("methodology_trace", sa.Text(), nullable=False),
        sa.Column("report_path", sa.String(length=500), nullable=False),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["validation_id"], ["company_validations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_company_validation_workspaces_company_id", "company_validation_workspaces", ["company_id"])
    op.create_index("ix_company_validation_workspaces_slug", "company_validation_workspaces", ["slug"])
    op.create_index("ix_company_validation_workspaces_status", "company_validation_workspaces", ["status"])
    op.create_index(
        "ix_company_validation_workspaces_validation_id",
        "company_validation_workspaces",
        ["validation_id"],
    )

    op.create_table(
        "company_validation_workspace_sections",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("section_key", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("required_source_types", sa.Text(), nullable=False),
        sa.Column("coverage_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("openvals_validation_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("methodology_trace", sa.Text(), nullable=False),
        sa.Column("lineage_json", sa.Text(), nullable=False),
        sa.Column("source_approval_status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["company_validation_workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "section_key", name="uq_workspace_section_key"),
    )
    op.create_index(
        "ix_company_validation_workspace_sections_section_key",
        "company_validation_workspace_sections",
        ["section_key"],
    )
    op.create_index(
        "ix_company_validation_workspace_sections_source_approval_status",
        "company_validation_workspace_sections",
        ["source_approval_status"],
    )
    op.create_index(
        "ix_company_validation_workspace_sections_workspace_id",
        "company_validation_workspace_sections",
        ["workspace_id"],
    )

    op.create_table(
        "company_validation_workspace_evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("section_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_role", sa.String(length=120), nullable=False),
        sa.Column("approval_status", sa.String(length=40), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("methodology_trace", sa.Text(), nullable=False),
        sa.Column("lineage_snapshot_json", sa.Text(), nullable=False),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["section_id"], ["company_validation_workspace_sections.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("section_id", "source_id", name="uq_workspace_section_source"),
    )
    op.create_index(
        "ix_company_validation_workspace_evidence_approval_status",
        "company_validation_workspace_evidence",
        ["approval_status"],
    )
    op.create_index(
        "ix_company_validation_workspace_evidence_evidence_role",
        "company_validation_workspace_evidence",
        ["evidence_role"],
    )
    op.create_index(
        "ix_company_validation_workspace_evidence_reviewed_by_user_id",
        "company_validation_workspace_evidence",
        ["reviewed_by_user_id"],
    )
    op.create_index(
        "ix_company_validation_workspace_evidence_section_id",
        "company_validation_workspace_evidence",
        ["section_id"],
    )
    op.create_index(
        "ix_company_validation_workspace_evidence_source_id",
        "company_validation_workspace_evidence",
        ["source_id"],
    )


def downgrade() -> None:
    op.drop_table("company_validation_workspace_evidence")
    op.drop_table("company_validation_workspace_sections")
    op.drop_table("company_validation_workspaces")
