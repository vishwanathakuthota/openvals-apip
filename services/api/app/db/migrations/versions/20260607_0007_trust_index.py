"""Add OpenVals Trust Index history and notifications.

Revision ID: 20260607_0007
Revises: 20260605_0006
Create Date: 2026-06-07 00:07:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260607_0007"
down_revision: str | None = "20260605_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "trust_index_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("entity_name", sa.String(length=255), nullable=False),
        sa.Column("trust_index", sa.Numeric(5, 2), nullable=False),
        sa.Column("trust_rating", sa.String(length=80), nullable=False),
        sa.Column("trust_classification", sa.String(length=80), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("evidence_coverage_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("transparency_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("reproducibility_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("source_quality_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("published_record_count", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("methodology_version", sa.String(length=80), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trust_index_snapshots_entity_id", "trust_index_snapshots", ["entity_id"])
    op.create_index(
        "ix_trust_index_snapshots_entity_name", "trust_index_snapshots", ["entity_name"]
    )
    op.create_index(
        "ix_trust_index_snapshots_entity_type", "trust_index_snapshots", ["entity_type"]
    )
    op.create_index(
        "ix_trust_index_snapshots_snapshot_date", "trust_index_snapshots", ["snapshot_date"]
    )
    op.create_index(
        "ix_trust_index_snapshots_trust_classification",
        "trust_index_snapshots",
        ["trust_classification"],
    )
    op.create_index(
        "ix_trust_index_snapshots_trust_rating", "trust_index_snapshots", ["trust_rating"]
    )

    op.create_table(
        "trust_change_notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("entity_name", sa.String(length=255), nullable=False),
        sa.Column("previous_trust_index", sa.Numeric(5, 2), nullable=True),
        sa.Column("current_trust_index", sa.Numeric(5, 2), nullable=False),
        sa.Column("change_amount", sa.Numeric(5, 2), nullable=False),
        sa.Column("notification_type", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_trust_change_notifications_entity_id", "trust_change_notifications", ["entity_id"]
    )
    op.create_index(
        "ix_trust_change_notifications_entity_name",
        "trust_change_notifications",
        ["entity_name"],
    )
    op.create_index(
        "ix_trust_change_notifications_entity_type",
        "trust_change_notifications",
        ["entity_type"],
    )
    op.create_index(
        "ix_trust_change_notifications_notification_type",
        "trust_change_notifications",
        ["notification_type"],
    )
    op.create_index(
        "ix_trust_change_notifications_status", "trust_change_notifications", ["status"]
    )


def downgrade() -> None:
    op.drop_table("trust_change_notifications")
    op.drop_table("trust_index_snapshots")
