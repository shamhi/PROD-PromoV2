"""Add promo target

Revision ID: 94b44b933d5f
Revises: d9626b6f5dc3
Create Date: 2025-01-22 21:12:44.776841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94b44b933d5f'
down_revision: Union[str, None] = 'd9626b6f5dc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('promo_targets',
    sa.Column('promo_id', sa.UUID(), nullable=False),
    sa.Column('age_from', sa.Integer(), nullable=True),
    sa.Column('age_until', sa.Integer(), nullable=True),
    sa.Column('country', sa.String(length=2), nullable=True),
    sa.Column('categories', sa.ARRAY(sa.String()), nullable=True),
    sa.ForeignKeyConstraint(['promo_id'], ['promos.id'], ),
    sa.PrimaryKeyConstraint('promo_id')
    )
    op.create_unique_constraint(None, 'business_companies', ['id'])
    op.create_unique_constraint(None, 'comments', ['id'])
    op.create_unique_constraint(None, 'promos', ['id'])
    op.drop_column('promos', 'country')
    op.create_unique_constraint(None, 'user_promo_activations', ['id'])
    op.create_unique_constraint(None, 'users', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'user_promo_activations', type_='unique')
    op.add_column('promos', sa.Column('country', sa.VARCHAR(length=2), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'promos', type_='unique')
    op.drop_constraint(None, 'comments', type_='unique')
    op.drop_constraint(None, 'business_companies', type_='unique')
    op.drop_table('promo_targets')
    # ### end Alembic commands ###
