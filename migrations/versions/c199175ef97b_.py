"""empty message

Revision ID: c199175ef97b
Revises: 1d2428bc657f
Create Date: 2021-04-22 19:58:44.214572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c199175ef97b'
down_revision = '1d2428bc657f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comments', 'date')
    # ### end Alembic commands ###
