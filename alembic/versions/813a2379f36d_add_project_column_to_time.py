"""Add project column to time.

Revision ID: 813a2379f36d
Revises: 348acf3ce3c3
Create Date: 2025-10-25 07:49:49.562787

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "813a2379f36d"
down_revision: str | Sequence[str] | None = "348acf3ce3c3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("Events", sa.Column("Project", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("Events", "Project")
