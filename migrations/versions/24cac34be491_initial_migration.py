"""Initial migration

Revision ID: 24cac34be491

Create Date: 2020-09-14 21:06:43.835527

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "24cac34be491"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )


def downgrade():
    op.drop_table("users")
