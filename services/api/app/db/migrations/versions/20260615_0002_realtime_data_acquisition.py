"""Add real-time data acquisition tracking.

Revision ID: 20260615_0002
Revises: 20260604_0001
Create Date: 2026-06-15
"""

import sqlalchemy as sa
from alembic import op

revision = "20260615_0002"
down_revision = "20260604_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sources", sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("sources", sa.Column("freshness_score", sa.Integer(), nullable=True))
    op.add_column(
        "source_metrics", sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("source_metrics", sa.Column("freshness_score", sa.Integer(), nullable=True))

    op.create_table(
        "data_acquisition_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("company_id", sa.String(length=36), nullable=True),
        sa.Column("connector", sa.String(length=120), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_found", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
    )
    op.create_index(
        "ix_data_acquisition_runs_company_id", "data_acquisition_runs", ["company_id"]
    )
    op.create_index("ix_data_acquisition_runs_connector", "data_acquisition_runs", ["connector"])
    op.create_index("ix_data_acquisition_runs_status", "data_acquisition_runs", ["status"])


def downgrade() -> None:
    op.drop_table("data_acquisition_runs")
    op.drop_column("source_metrics", "freshness_score")
    op.drop_column("source_metrics", "retrieved_at")
    op.drop_column("sources", "freshness_score")
    op.drop_column("sources", "retrieved_at")
