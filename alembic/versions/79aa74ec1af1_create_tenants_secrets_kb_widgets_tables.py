"""create tenants, secrets, kb, widgets tables

Revision ID: 79aa74ec1af1
Revises: 2025_01_initial_multitenant
Create Date: 2025-12-28 00:04:21.946557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "20251227_create_core_tables"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("logo_url", sa.String(255)),
        sa.Column("theme_color", sa.String(50)),
        sa.Column("chat_logo_url", sa.String(255)),
        sa.Column("welcome_message", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "secrets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("org_id", sa.Integer, sa.ForeignKey("tenants.id")),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "knowledge_bases",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("org_id", sa.Integer, sa.ForeignKey("tenants.id")),
        sa.Column("kb_name", sa.String(255), nullable=False),
        sa.Column("kb_url", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "widgets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("org_id", sa.Integer, sa.ForeignKey("tenants.id")),
        sa.Column("position", sa.String(50)),
        sa.Column("chat_logo_url", sa.String(255)),
        sa.Column("welcome_message", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("widgets")
    op.drop_table("knowledge_bases")
    op.drop_table("secrets")
    op.drop_table("tenants")
