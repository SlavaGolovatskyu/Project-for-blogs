"""empty message

Revision ID: 208c7e2b9a7f
Revises: 229e1079cc5e
Create Date: 2021-06-20 11:44:20.263051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '208c7e2b9a7f'
down_revision = '229e1079cc5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=True))
        batch_op.drop_column('role')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_column('role_id')

    # ### end Alembic commands ###
