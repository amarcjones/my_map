"""empty message

Revision ID: cd2e051367c9
Revises: 30db50260672
Create Date: 2018-01-02 21:19:50.887474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd2e051367c9'
down_revision = '30db50260672'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('spots')
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('spots', sa.Column('loc_id', sa.Integer(), nullable=True))
    # op.add_column('spots', sa.Column('user_id', sa.Integer(), nullable=True))
    # op.drop_constraint('spots_id_fkey', 'spots', type_='foreignkey')
    # op.create_foreign_key(None, 'spots', 'users', ['user_id'], ['id'])
    # op.create_foreign_key(None, 'spots', 'locations', ['loc_id'], ['id'])
    # op.drop_column('spots', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('spots', sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'spots', type_='foreignkey')
    op.drop_constraint(None, 'spots', type_='foreignkey')
    op.create_foreign_key('spots_id_fkey', 'spots', 'locations', ['id'], ['id'])
    op.drop_column('spots', 'user_id')
    op.drop_column('spots', 'loc_id')
    # ### end Alembic commands ###