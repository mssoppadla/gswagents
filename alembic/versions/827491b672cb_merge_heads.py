"""merge heads

Revision ID: 827491b672cb
Revises: 2025_01_initial_multitenant, 20251227_create_core_tables
Create Date: 2025-12-28 09:27:35.659558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '827491b672cb'
down_revision: Union[str, Sequence[str], None] = ('2025_01_initial_multitenant', '20251227_create_core_tables')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
