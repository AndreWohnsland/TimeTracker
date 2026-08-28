"""Add the WorkSchedule table.

Revision ID: c5e8a1b2d3f4
Revises: 74beea3304bb
Create Date: 2026-08-27 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5e8a1b2d3f4"
down_revision: str | Sequence[str] | None = "74beea3304bb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # create_all may already have created the table (fresh installs, tests)
    inspector = sa.inspect(op.get_bind())
    if "WorkSchedule" in inspector.get_table_names():
        return
    op.create_table(
        "WorkSchedule",
        sa.Column("ID", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ValidFrom", sa.Date(), nullable=False, unique=True),
        sa.Column("WorkHours", sa.Float(), nullable=False),
        sa.Column("UseHoursPerWeek", sa.Boolean(), nullable=False),
        sa.Column("Workdays", sa.JSON(), nullable=False),
        sa.Column("DifferentWorkdays", sa.Boolean(), nullable=False),
        sa.Column("TimePerDay", sa.JSON(), nullable=False),
    )
    op.create_index("idx_valid_from", "WorkSchedule", ["ValidFrom"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("WorkSchedule")
