"""Add commercial usage metering and billing foundation.

Revision ID: 20260609_0008
Revises: 20260607_0007
Create Date: 2026-06-09 00:08:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260609_0008"
down_revision: str | None = "20260607_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "api_usage_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("api_key_id", sa.String(length=36), nullable=False),
        sa.Column("endpoint", sa.String(length=500), nullable=False),
        sa.Column("method", sa.String(length=12), nullable=False),
        sa.Column("plan", sa.String(length=40), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_keys.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_usage_events_api_key_id", "api_usage_events", ["api_key_id"])
    op.create_index("ix_api_usage_events_endpoint", "api_usage_events", ["endpoint"])
    op.create_index("ix_api_usage_events_method", "api_usage_events", ["method"])
    op.create_index("ix_api_usage_events_plan", "api_usage_events", ["plan"])
    op.create_index("ix_api_usage_events_usage_date", "api_usage_events", ["usage_date"])

    op.create_table(
        "api_subscriptions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("api_key_id", sa.String(length=36), nullable=False),
        sa.Column("plan", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("monthly_price_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("daily_quota", sa.Integer(), nullable=True),
        sa.Column("entitlements_json", sa.Text(), nullable=False),
        sa.Column("current_period_start", sa.Date(), nullable=False),
        sa.Column("current_period_end", sa.Date(), nullable=False),
        sa.Column("payment_provider", sa.String(length=80), nullable=False),
        sa.Column("external_subscription_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_keys.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_subscriptions_api_key_id", "api_subscriptions", ["api_key_id"])
    op.create_index("ix_api_subscriptions_plan", "api_subscriptions", ["plan"])
    op.create_index("ix_api_subscriptions_status", "api_subscriptions", ["status"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("subscription_id", sa.String(length=36), nullable=False),
        sa.Column("invoice_number", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("amount_due_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("amount_paid_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("payment_provider", sa.String(length=80), nullable=False),
        sa.Column("external_invoice_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["subscription_id"], ["api_subscriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)
    op.create_index("ix_invoices_status", "invoices", ["status"])
    op.create_index("ix_invoices_subscription_id", "invoices", ["subscription_id"])


def downgrade() -> None:
    op.drop_table("invoices")
    op.drop_table("api_subscriptions")
    op.drop_table("api_usage_events")
