"""SQLAlchemy ORM models for the TimeTracker database.

This module defines the database models using SQLAlchemy ORM for type-safe
database operations. The models mirror the existing SQLite database schema
to maintain backward compatibility while providing better developer experience.

The ORM provides:
- Type safety with proper Python type hints
- IDE autocompletion support
- Cleaner and more maintainable code
- Support for database migrations via Alembic (future)
"""

import datetime

from sqlalchemy import Date as SqlDate
from sqlalchemy import DateTime, Index, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Event(Base):
    __tablename__ = "Events"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, name="Date")
    action: Mapped[str] = mapped_column(String, nullable=False, name="Action")
    project: Mapped[str | None] = mapped_column(String, nullable=True, name="Project")

    __table_args__ = (Index("idx_datetime", "Date"),)

    def __init__(self, date: datetime.datetime, action: str, project: str | None) -> None:  # noqa: D107
        self.date = date
        self.action = action
        self.project = project


class Pause(Base):
    __tablename__ = "Pause"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(SqlDate, nullable=False, unique=True, name="Date")
    time: Mapped[int] = mapped_column(Integer, nullable=False, name="Time")

    __table_args__ = (Index("idx_date", "Date", unique=True),)

    def __init__(self, date: datetime.date, time: int) -> None:  # noqa: D107
        self.date = date
        self.time = time


class TimeOff(Base):
    __tablename__ = "TimeOff"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(SqlDate, nullable=False, unique=True, name="Date")
    reason: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="Vacation",
        server_default="Vacation",
        name="Reason",
    )

    __table_args__ = (Index("idx_date_vacation", "Date", unique=True),)

    def __init__(self, date: datetime.date, reason: str = "Vacation") -> None:  # noqa: D107
        self.date = date
        self.reason = reason


def create_session_factory(db_url: str) -> sessionmaker:
    """Create a session factory for the given database URL.

    Args:
        db_url: SQLAlchemy database URL (e.g., 'sqlite:///path/to/db.db')

    Returns:
        A SQLAlchemy sessionmaker that can create new sessions

    """
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
