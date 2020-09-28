"""Add password hash and email verifiaction token

Revision ID: 198f5ee0ec3f
Revises: 24cac34be491
Create Date: 2020-09-15 20:49:53.930888

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "198f5ee0ec3f"
down_revision = "4855191efa70"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("hash", sa.String(), nullable=False))
    op.add_column(
        "users",
        sa.Column("email_verification_token", sa.String(), nullable=True, unique=True),
    )


def downgrade():
    op.drop_column("users", "hash")
    op.drop_column("users", "email_verification_token")
