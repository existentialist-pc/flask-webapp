"""add avatar_h hash

Revision ID: 863c10fdde59
Revises: e290a3bb3e02
Create Date: 2016-12-29 21:26:22.655829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '863c10fdde59'
down_revision = 'e290a3bb3e02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_hash', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_hash')
    # ### end Alembic commands ###
