"""Add stock column to products

Revision ID: caa91757efb3
Revises: 
Create Date: 2025-09-24 13:33:15.733374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'caa91757efb3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This initial revision should not drop anything; make it a no-op.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # No-op to avoid conflicting create/drop with later revisions.
    pass
