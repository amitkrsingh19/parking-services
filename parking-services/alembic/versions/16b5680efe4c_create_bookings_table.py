"""create bookings table

Revision ID: 16b5680efe4c
Revises: 5ad0d1887c6a
Create Date: 2025-08-28 12:57:52.618853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16b5680efe4c'
down_revision: Union[str, Sequence[str], None] = '5ad0d1887c6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('bookings',
                    sa.Column('id',sa.Integer(),nullable=False),
                    sa.Column('user_id',sa.Integer(),nullable=False),
                    sa.Column('slot_id',sa.Integer(),nullable=False),
                    sa.Column('start_time',sa.DateTime(timezone=True),server_default=sa.text('now()'),nullable=False),
                    sa.Column('end_time',sa.DateTime(timezone=True),nullable=False),
                    sa.Column('status', sa.String(),nullable=False),
                    sa.Column('price',sa.DECIMAL(),nullable=False),
                    sa.Column('booked_at',sa.DateTime(timezone=True),default=sa.text('now()'),nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['slot_id'], ['slots.id'], ondelete="CASCADE"))
    pass


def downgrade() -> None:
    op.drop_table('bookings')
    pass
