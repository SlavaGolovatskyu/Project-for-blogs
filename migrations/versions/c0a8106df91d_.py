"""empty message

Revision ID: c0a8106df91d
Revises: 331fea1f1ad2
Create Date: 2021-06-19 21:43:05.092731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0a8106df91d'
down_revision = '331fea1f1ad2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.drop_constraint('roles_users_fkey', type_='foreignkey')
        batch_op.drop_column('users')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('users', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('roles_users_fkey', 'users', ['users'], ['id'])

    # ### end Alembic commands ###
