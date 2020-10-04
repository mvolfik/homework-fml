"""Add password reset token

Revision ID: 13a36d65cdb3
Revises: 198f5ee0ec3f
Create Date: 2020-10-04 16:01:30.699154

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "13a36d65cdb3"
down_revision = "198f5ee0ec3f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "password_reset_tokens",
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("expires", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(("user_id",), ("users.id",)),
        sa.PrimaryKeyConstraint("token"),
    )


def downgrade():
    op.drop_table("password_reset_tokens")
