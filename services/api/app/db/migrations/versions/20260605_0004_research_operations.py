"""research operations framework

Revision ID: 20260605_0004
Revises: 20260605_0003
Create Date: 2026-06-05
"""

import sqlalchemy as sa
from alembic import op

revision = "20260605_0004"
down_revision = "20260605_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_queue_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("validation_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.String(length=40), nullable=False),
        sa.Column("assigned_to_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewer_user_id", sa.String(length=36), nullable=True),
        sa.Column("progress_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("evidence_coverage_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["validation_id"], ["company_validations.id"]),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_research_queue_items_company_id", "research_queue_items", ["company_id"], unique=True
    )
    op.create_index(
        "ix_research_queue_items_validation_id", "research_queue_items", ["validation_id"]
    )
    op.create_index("ix_research_queue_items_status", "research_queue_items", ["status"])
    op.create_index("ix_research_queue_items_priority", "research_queue_items", ["priority"])
    op.create_index(
        "ix_research_queue_items_assigned_to_user_id",
        "research_queue_items",
        ["assigned_to_user_id"],
    )
    op.create_index(
        "ix_research_queue_items_reviewer_user_id",
        "research_queue_items",
        ["reviewer_user_id"],
    )

    op.create_table(
        "research_evidence",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("queue_item_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_type", sa.String(length=120), nullable=False),
        sa.Column("collection_status", sa.String(length=40), nullable=False),
        sa.Column("approval_status", sa.String(length=40), nullable=False),
        sa.Column("coverage_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("collected_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewer_user_id", sa.String(length=36), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["queue_item_id"], ["research_queue_items.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["collected_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["users.id"]),
    )
    op.create_index("ix_research_evidence_queue_item_id", "research_evidence", ["queue_item_id"])
    op.create_index("ix_research_evidence_source_id", "research_evidence", ["source_id"])
    op.create_index("ix_research_evidence_evidence_type", "research_evidence", ["evidence_type"])
    op.create_index(
        "ix_research_evidence_collection_status", "research_evidence", ["collection_status"]
    )
    op.create_index(
        "ix_research_evidence_approval_status", "research_evidence", ["approval_status"]
    )
    op.create_index(
        "ix_research_evidence_collected_by_user_id",
        "research_evidence",
        ["collected_by_user_id"],
    )
    op.create_index(
        "ix_research_evidence_reviewer_user_id",
        "research_evidence",
        ["reviewer_user_id"],
    )

    op.create_table(
        "research_audit_trail",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("queue_item_id", sa.String(length=36), nullable=True),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["queue_item_id"], ["research_queue_items.id"]),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_research_audit_trail_queue_item_id", "research_audit_trail", ["queue_item_id"]
    )
    op.create_index(
        "ix_research_audit_trail_actor_user_id", "research_audit_trail", ["actor_user_id"]
    )
    op.create_index("ix_research_audit_trail_action", "research_audit_trail", ["action"])


def downgrade() -> None:
    op.drop_table("research_audit_trail")
    op.drop_table("research_evidence")
    op.drop_table("research_queue_items")
