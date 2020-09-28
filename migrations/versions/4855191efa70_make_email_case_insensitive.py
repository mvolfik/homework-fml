"""Make email case insensitive

Revision ID: 4855191efa70
Revises: 24cac34be491
Create Date: 2020-09-24 18:14:31.508085

"""
import sqlalchemy as sa
from alembic import op
from citext import CIText

# revision identifiers, used by Alembic.

revision = "4855191efa70"
down_revision = "24cac34be491"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("users", "email", type_=CIText())


def downgrade():
    op.alter_column("users", "email", type_=sa.String())
