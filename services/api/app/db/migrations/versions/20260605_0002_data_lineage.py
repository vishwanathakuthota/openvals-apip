"""data lineage for real data imports

Revision ID: 20260605_0002
Revises: 20260604_0001
Create Date: 2026-06-05
"""

import sqlalchemy as sa
from alembic import op

revision = "20260605_0002"
down_revision = "20260604_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_lineage",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_type", sa.String(length=120), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("imported_by_user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("import_batch_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["imported_by_user_id"], ["users.id"]),
    )
    op.create_index("ix_data_lineage_entity_type", "data_lineage", ["entity_type"])
    op.create_index("ix_data_lineage_entity_id", "data_lineage", ["entity_id"])
    op.create_index("ix_data_lineage_source_id", "data_lineage", ["source_id"])
    op.create_index("ix_data_lineage_source_type", "data_lineage", ["source_type"])
    op.create_index("ix_data_lineage_imported_by_user_id", "data_lineage", ["imported_by_user_id"])
    op.create_index("ix_data_lineage_import_batch_id", "data_lineage", ["import_batch_id"])
    op.create_index("ix_data_lineage_action", "data_lineage", ["action"])


def downgrade() -> None:
    op.drop_table("data_lineage")
