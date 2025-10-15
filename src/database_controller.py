"""Database controller using SQLAlchemy ORM for type-safe database operations.

This module provides the main database interface for the TimeTracker application.
It uses SQLAlchemy ORM to provide type-safe database operations with proper Python
type hints and better developer experience.

The DatabaseController class provides high-level methods for:
- Event tracking (start/stop events)
- Pause time management
- Vacation day management
- Data retrieval for daily and monthly reports
"""

import datetime
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.filepath import DATABASE_PATH
from src.models import Event, Pause, Vacation, create_session_factory

logger = logging.getLogger(__name__)


class DatabaseController:
    """Controller Class to execute all DB queries and return results as Values / Lists / Dictionaries."""

    def __init__(self, db_url: str | None = None) -> None:
        """Abstract Access to the database."""
        self.handler = DatabaseHandler(db_url)

    def add_event(self, event: str, entry_datetime: datetime.datetime) -> None:
        datetime_string = entry_datetime.isoformat()
        logger.info("Add Event: %s, timestamp: %s", event, datetime_string)
        session = self.handler.get_session()
        try:
            new_event = Event(Date=entry_datetime, Action=event)
            session.add(new_event)
            session.commit()
        finally:
            session.close()

    def add_pause(self, pause_time: int, entry_date: datetime.date) -> None:
        date_string = entry_date.isoformat()
        if self.day_exists(date_string):
            self.update_pause(pause_time, date_string)
        else:
            self.insert_pause(pause_time, date_string)

    def update_pause(self, pause_time: int, date_string: str) -> None:
        logger.info("Updating pause time by %s at %s", pause_time, date_string)
        session = self.handler.get_session()
        try:
            stmt = update(Pause).where(Pause.Date == date_string).values(Time=Pause.Time + pause_time)
            session.execute(stmt)
            session.commit()
        finally:
            session.close()

    def insert_pause(self, pause_time: int, date_string: str) -> None:
        logger.info("Inserting pause time by %s at %s", pause_time, date_string)
        session = self.handler.get_session()
        try:
            new_pause = Pause(Date=date_string, Time=pause_time)
            session.add(new_pause)
            session.commit()
        finally:
            session.close()

    def day_exists(self, date_str: str) -> int:
        session = self.handler.get_session()
        try:
            stmt = select(Pause).where(Pause.Date == date_str)
            result = session.execute(stmt).scalar_one_or_none()
            return 1 if result else 0
        finally:
            session.close()

    def get_month_data(self, search_date: datetime.date) -> tuple[list[tuple[str, str]], list[tuple[str, int]]]:
        start = datetime.date(search_date.year, search_date.month, 1)
        end = start + relativedelta(months=+1)
        work = self.get_period_work(start, end)
        pause = self.get_period_pause(start, end)
        return work, pause

    def get_day_data(self, day: datetime.date) -> tuple[list[tuple[str, str]], list[tuple[str, int]]]:
        start = day
        end = start + relativedelta(days=+1)
        work = self.get_period_work(start, end)
        pause = self.get_period_pause(start, start)
        return work, pause

    def get_period_work(self, start: datetime.date, end: datetime.date) -> list[tuple[str, str]]:
        session = self.handler.get_session()
        try:
            start_dt = datetime.datetime.combine(start, datetime.time.min)
            end_dt = datetime.datetime.combine(end, datetime.time.max)
            stmt = select(Event).where(Event.Date >= start_dt, Event.Date <= end_dt).order_by(Event.Date)
            results = session.execute(stmt).scalars().all()
            return [(event.Date.isoformat(), event.Action) for event in results]
        finally:
            session.close()

    def get_period_pause(self, start: datetime.date, end: datetime.date) -> list[tuple[str, int]]:
        session = self.handler.get_session()
        try:
            start_str = start.isoformat()
            end_str = end.isoformat()
            stmt = select(Pause).where(Pause.Date >= start_str, Pause.Date <= end_str).order_by(Pause.Date)
            results = session.execute(stmt).scalars().all()
            return [(pause.Date, pause.Time) for pause in results]
        finally:
            session.close()

    def delete_event(self, delete_datetime: str) -> None:
        session = self.handler.get_session()
        try:
            delete_dt = datetime.datetime.fromisoformat(delete_datetime)
            stmt = delete(Event).where(Event.Date == delete_dt)
            session.execute(stmt)
            session.commit()
        finally:
            session.close()

    def add_vacation(self, vacation_date: datetime.date) -> None:
        date_string = vacation_date.isoformat()
        logger.info("Adding Vacation on %s", date_string)
        session = self.handler.get_session()
        try:
            # only enter if the date does not exist
            existing = session.execute(select(Vacation).where(Vacation.Date == date_string)).scalar_one_or_none()
            if not existing:
                new_vacation = Vacation(Date=date_string)
                session.add(new_vacation)
                session.commit()
        finally:
            session.close()

    def get_vacation_days(self, year: int) -> list[datetime.date]:
        session = self.handler.get_session()
        try:
            # Filter by year at database level using LIKE pattern (YYYY-MM-DD format)
            year_pattern = f"{year}-%"
            stmt = select(Vacation).where(Vacation.Date.like(year_pattern))
            results = session.execute(stmt).scalars().all()
            return [datetime.date.fromisoformat(vacation.Date) for vacation in results]
        finally:
            session.close()

    def remove_vacation(self, vacation_date: datetime.date) -> None:
        date_string = vacation_date.isoformat()
        logger.info("Removing Vacation on %s", date_string)
        session = self.handler.get_session()
        try:
            stmt = delete(Vacation).where(Vacation.Date == date_string)
            session.execute(stmt)
            session.commit()
        finally:
            session.close()


class DatabaseHandler:
    """Handler Class for Connecting and querying Databases.

    Uses a session factory to create new sessions per operation,
    ensuring thread safety and proper resource management.
    """

    database_path = DATABASE_PATH

    def __init__(self, db_url: str | None = None) -> None:
        """Class to connect and query the database."""
        # check if the old database exists and move it to the new location
        if db_url is None:
            # Ensure parent directory exists
            DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{DATABASE_PATH}"
        elif not db_url.startswith("sqlite://"):
            # Handle :memory: case and other direct paths
            db_url = f"sqlite:///{db_url}"
        self.db_url = db_url
        if not self.database_path.exists():
            logger.debug("No database detected, creating Database at %s", self.database_path)
        self.session_factory = create_session_factory(self.db_url)

    def get_session(self) -> Session:
        """Get a new database session.

        Returns a new session for each call to ensure thread safety
        and proper resource management. The caller is responsible for
        closing the session after use.
        """
        return self.session_factory()


DB_CONTROLLER = DatabaseController()
