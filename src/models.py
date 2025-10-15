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

from sqlalchemy import DateTime, Index, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Event(Base):
    """Event model representing start/stop events."""

    __tablename__ = "Events"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    Action: Mapped[str] = mapped_column(String, nullable=False)


class Pause(Base):
    """Pause model representing daily pause times.

    Date is stored as ISO format string (YYYY-MM-DD) to maintain
    compatibility with the existing SQLite database schema.
    """

    __tablename__ = "Pause"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Date: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    Time: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (Index("idx_date", "Date", unique=True),)


class Vacation(Base):
    """Vacation model representing vacation days.

    Date is stored as ISO format string (YYYY-MM-DD) to maintain
    compatibility with the existing SQLite database schema.
    """

    __tablename__ = "Vacation"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Date: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    __table_args__ = (Index("idx_date_vacation", "Date", unique=True),)


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
