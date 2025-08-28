"""Create parking table

Revision ID: f37949df36eb
Revises: 
Create Date: 2025-08-27 20:22:28.881318

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f37949df36eb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('station',
                    sa.Column('id',sa.Integer(),nullable=False),
                    sa.Column('name',sa.String(),nullable=False),
                    sa.Column('location',sa.String(),nullable=False),
                    sa.Column('capacity',sa.Integer(),nullable=False),
                    sa.Column('created_at',sa.TIMESTAMP(timezone=True),server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('admin_id',sa.Integer(),nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name'),
                    sa.ForeignKey('admin_id'))
    pass

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('station')
    pass
