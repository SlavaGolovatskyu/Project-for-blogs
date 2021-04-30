"""empty message

Revision ID: a75cb0bdb227
Revises: 25ba0dbeaca3
Create Date: 2021-03-29 23:45:38.598604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a75cb0bdb227'
down_revision = '25ba0dbeaca3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('author_name', sa.String(length=50), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('articles', 'author_name')
    # ### end Alembic commands ###
