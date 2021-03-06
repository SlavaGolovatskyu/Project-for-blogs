"""empty message

Revision ID: 695f7cbd85c0
Revises: 29cd7fb7de76
Create Date: 2021-04-12 19:21:51.211345

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '695f7cbd85c0'
down_revision = '29cd7fb7de76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_which_viewed_post', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_which_viewed_post', sa.Column('name', sa.VARCHAR(length=50), nullable=False))
    # ### end Alembic commands ###
