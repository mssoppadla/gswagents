from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "<timestamp>"
down_revision = "<previous_revision_id>"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("documents", sa.Column("source_type", sa.String(length=50), nullable=True))
    op.add_column("documents", sa.Column("source_url", sa.String(length=1024), nullable=True))
    op.add_column("documents", sa.Column("external_id", sa.String(length=255), nullable=True))
    op.add_column("documents", sa.Column("mime_type", sa.String(length=255), nullable=True))
    op.add_column("documents", sa.Column("ingest_status", sa.String(length=50), nullable=True))
    op.add_column("documents", sa.Column("ingest_error", sa.Text(), nullable=True))

def downgrade():
    op.drop_column("documents", "ingest_error")
    op.drop_column("documents", "ingest_status")
    op.drop_column("documents", "mime_type")
    op.drop_column("documents", "external_id")
    op.drop_column("documents", "source_url")
    op.drop_column("documents", "source_type")
