"""add orders, order_items, shippings, payments tables

Revision ID: a1b2c3d4e5f6
Revises: f2b1f1a3c9a6
Create Date: 2025-10-18 18:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f2b1f1a3c9a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('status', sa.String(), nullable=False, server_default='Pending Payment'),
        sa.Column('subtotal', sa.Float(), nullable=False, server_default='0'),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)

    # order_items
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('line_total', sa.Float(), nullable=False),
    )
    op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)

    # shippings
    op.create_table(
        'shippings',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('address1', sa.String(), nullable=False),
        sa.Column('address2', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False),
    )
    op.create_index(op.f('ix_shippings_id'), 'shippings', ['id'], unique=False)
    op.create_unique_constraint('uq_shipping_order', 'shippings', ['order_id'])

    # payments
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(), nullable=False, server_default='stripe'),
        sa.Column('stripe_session_id', sa.String(), nullable=True),
        sa.Column('stripe_payment_intent', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='Pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_unique_constraint('uq_payments_order', 'payments', ['order_id'])


def downgrade() -> None:
    op.drop_constraint('uq_payments_order', 'payments', type_='unique')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')

    op.drop_constraint('uq_shipping_order', 'shippings', type_='unique')
    op.drop_index(op.f('ix_shippings_id'), table_name='shippings')
    op.drop_table('shippings')

    op.drop_index(op.f('ix_order_items_id'), table_name='order_items')
    op.drop_table('order_items')

    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
