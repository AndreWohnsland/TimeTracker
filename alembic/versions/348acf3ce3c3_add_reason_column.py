"""Add the reason column to the Vacation table.

Also, rename the table to TimeOff and add an index to the Events table.

Revision ID: 348acf3ce3c3
Revises:
Create Date: 2025-10-16 16:42:05.483608

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "348acf3ce3c3"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index("idx_datetime", "Events", ["Date"])
    op.rename_table("Vacation", "TimeOff")
    op.add_column(
        "TimeOff", sa.Column("Reason", sa.String(), nullable=False, default="Vacation", server_default="Vacation")
    )
    op.execute("UPDATE TimeOff SET Reason='Vacation'")


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table("TimeOff", "Vacation")
    op.drop_index("idx_datetime", "Events")
