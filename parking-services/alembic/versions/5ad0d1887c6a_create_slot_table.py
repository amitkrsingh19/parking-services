"""create slot table

Revision ID: 5ad0d1887c6a
Revises: f37949df36eb
Create Date: 2025-08-28 12:38:56.975000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ad0d1887c6a'
down_revision: Union[str, Sequence[str], None] = 'f37949df36eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('station_id', sa.Integer(), sa.ForeignKey('station.id', ondelete="CASCADE"), nullable=False),
        sa.Column('slot_number', sa.String(), nullable=False, unique=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('slot_type', sa.String(), nullable=False),
        sa.Column('price_per_hour', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('slots')