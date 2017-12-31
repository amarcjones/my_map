"""empty message

Revision ID: b0b268b9dc08
Revises: 
Create Date: 2017-12-30 17:47:23.558683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0b268b9dc08'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('addr', sa.Text(), nullable=True),
    sa.Column('icon', sa.Text(), nullable=True),
    sa.Column('ph_domestic', sa.Text(), nullable=True),
    sa.Column('ph_intl', sa.Text(), nullable=True),
    sa.Column('website', sa.Text(), nullable=True),
    sa.Column('lat', sa.Numeric(precision=12, scale=7), nullable=True),
    sa.Column('lng', sa.Numeric(precision=12, scale=7), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.Text(), nullable=True),
    sa.Column('password', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('locations')
    # ### end Alembic commands ###