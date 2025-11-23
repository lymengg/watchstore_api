"""add is_deleted column to products for soft delete

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-10-21 08:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('products', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    # Optionally, drop server_default after backfilling default on existing rows
    op.alter_column('products', 'is_deleted', server_default=None)


def downgrade() -> None:
    op.drop_column('products', 'is_deleted')
