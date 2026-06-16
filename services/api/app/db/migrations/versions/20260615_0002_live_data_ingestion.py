"""live data ingestion

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
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_type", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_created", sa.Integer(), nullable=False),
        sa.Column("records_failed", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
    )
    op.create_index("ix_ingestion_runs_source_type", "ingestion_runs", ["source_type"])
    op.create_index("ix_ingestion_runs_status", "ingestion_runs", ["status"])

    op.create_table(
        "live_data_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("run_id", sa.String(length=36), nullable=True),
        sa.Column("company_id", sa.String(length=36), nullable=True),
        sa.Column("company_slug", sa.String(length=255), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=True),
        sa.Column("metric_type", sa.String(length=120), nullable=False),
        sa.Column("value_numeric", sa.Numeric(20, 6), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("fiscal_year", sa.Integer(), nullable=True),
        sa.Column("fiscal_period", sa.String(length=40), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_type", sa.String(length=120), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("freshness_score", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("raw_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("raw_payload_snapshot", sa.Text(), nullable=False),
        sa.Column("ingestion_status", sa.String(length=40), nullable=False),
        sa.Column("filing_accession", sa.String(length=80), nullable=True),
        sa.Column("filing_form", sa.String(length=20), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
    )
    op.create_index("ix_live_data_records_company_id", "live_data_records", ["company_id"])
    op.create_index("ix_live_data_records_company_slug", "live_data_records", ["company_slug"])
    op.create_index("ix_live_data_records_symbol", "live_data_records", ["symbol"])
    op.create_index("ix_live_data_records_metric_type", "live_data_records", ["metric_type"])
    op.create_index("ix_live_data_records_source_type", "live_data_records", ["source_type"])
    op.create_index("ix_live_data_records_retrieved_at", "live_data_records", ["retrieved_at"])
    op.create_index(
        "ix_live_data_records_raw_payload_hash",
        "live_data_records",
        ["raw_payload_hash"],
    )
    op.create_index(
        "ix_live_data_records_ingestion_status",
        "live_data_records",
        ["ingestion_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_live_data_records_ingestion_status", table_name="live_data_records")
    op.drop_index("ix_live_data_records_raw_payload_hash", table_name="live_data_records")
    op.drop_index("ix_live_data_records_retrieved_at", table_name="live_data_records")
    op.drop_index("ix_live_data_records_source_type", table_name="live_data_records")
    op.drop_index("ix_live_data_records_metric_type", table_name="live_data_records")
    op.drop_index("ix_live_data_records_symbol", table_name="live_data_records")
    op.drop_index("ix_live_data_records_company_slug", table_name="live_data_records")
    op.drop_index("ix_live_data_records_company_id", table_name="live_data_records")
    op.drop_table("live_data_records")
    op.drop_index("ix_ingestion_runs_status", table_name="ingestion_runs")
    op.drop_index("ix_ingestion_runs_source_type", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
