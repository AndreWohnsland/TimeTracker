"""Add the OvertimeAdjustment table.

Revision ID: 74beea3304bb
Revises: 813a2379f36d
Create Date: 2026-08-22 12:36:50.844829

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "74beea3304bb"
down_revision: str | Sequence[str] | None = "813a2379f36d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # create_all may already have created the table (fresh installs, tests)
    inspector = sa.inspect(op.get_bind())
    if "OvertimeAdjustment" in inspector.get_table_names():
        return
    op.create_table(
        "OvertimeAdjustment",
        sa.Column("ID", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("Date", sa.Date(), nullable=False, unique=True),
        sa.Column("Hours", sa.Float(), nullable=False),
    )
    op.create_index("idx_date_adjustment", "OvertimeAdjustment", ["Date"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("OvertimeAdjustment")
