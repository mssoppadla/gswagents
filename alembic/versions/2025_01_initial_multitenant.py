"""initial multitenant schema"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = "2025_01_initial_multitenant"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("public_api_key_hash", sa.String(255), nullable=False),
        sa.Column("allowed_domain", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("org_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("workos_user_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "guest_identities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("org_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("origin", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "config_themes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("org_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("logo_url", sa.String(255)),
        sa.Column("welcome_message", sa.Text),
        sa.Column("theme_json", sa.Text),
        sa.Column("published", sa.Boolean, default=False),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("org_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("url", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), default="active"),
        sa.Column("published", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("documents")
    op.drop_table("config_themes")
    op.drop_table("guest_identities")
    op.drop_table("users")
    op.drop_table("organizations")
