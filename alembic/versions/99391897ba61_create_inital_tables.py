"""create inital tables

Revision ID: 99391897ba61
Revises: 
Create Date: 2022-02-07 05:24:04.391255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99391897ba61'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.String(), nullable=True))
    op.drop_column('users', 'hashed_password')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('users', 'password')
    # ### end Alembic commands ###