"""empty message

Revision ID: 4f8ea7ed0a56
Revises: b8c06f3fbd7e
Create Date: 2020-12-05 12:27:59.126047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f8ea7ed0a56'
down_revision = 'b8c06f3fbd7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_active')
    # ### end Alembic commands ###
