"""add_user_roles

Revision ID: 845fec99da2d
Revises: 44c1963362b9
Create Date: 2025-08-25 21:43:18.466176

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "845fec99da2d"
down_revision: str | Sequence[str] | None = "44c1963362b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type first
    userrole_enum = sa.Enum("ADMIN", "USER", name="userrole")
    userrole_enum.create(op.get_bind())

    # Add the column with a default value first (nullable)
    op.add_column("users", sa.Column("role", userrole_enum, nullable=True))

    # Update existing users to have default role
    op.execute("UPDATE users SET role = 'USER' WHERE role IS NULL")

    # Make the column not nullable
    op.alter_column("users", "role", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the column
    op.drop_column("users", "role")

    # Drop the enum type
    userrole_enum = sa.Enum("ADMIN", "USER", name="userrole")
    userrole_enum.drop(op.get_bind())
