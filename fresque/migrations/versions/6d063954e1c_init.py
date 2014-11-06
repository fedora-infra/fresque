"""Initial migration, does nothing but setting a revision string.

Revision ID: 6d063954e1c
Revises: None
Create Date: 2014-10-22 18:27:47.457693

"""

# revision identifiers, used by Alembic.
revision = '6d063954e1c'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Initial migration, nothing to do
    pass


def downgrade():
    # Initial migration, nothing to do
    pass
