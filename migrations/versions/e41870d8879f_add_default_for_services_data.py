"""Add default for services_data

Revision ID: e41870d8879f
Revises: bc7b248e78c1
Create Date: 2020-10-25 19:25:16.962682

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e41870d8879f"
down_revision = "bc7b248e78c1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE users SET services_data = '{}' WHERE services_data IS NULL")
    op.alter_column("users", "services_data", nullable=False)


def downgrade():
    op.alter_column("users", "services_data", nullable=True)
