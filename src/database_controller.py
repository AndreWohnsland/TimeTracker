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
from collections.abc import Generator
from contextlib import contextmanager

from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, delete, select, update
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from src.filepath import DATABASE_PATH
from src.models import Base, Event, Pause, Vacation

logger = logging.getLogger(__name__)


class DatabaseController:
    """Controller Class to execute all DB queries and return results as Values / Lists / Dictionaries."""

    database_path = DATABASE_PATH

    def __init__(self, db_url: str | None = None) -> None:
        """Initialize the database controller with SQLAlchemy ORM."""
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
        
        self.engine = create_engine(self.db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=False))

    def __del__(self) -> None:
        """Close the session when the object is deleted."""
        self.Session.remove()
        self.engine.dispose()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_event(self, event: str, entry_datetime: datetime.datetime) -> None:
        datetime_string = entry_datetime.isoformat()
        logger.info("Add Event: %s, timestamp: %s", event, datetime_string)
        with self.session_scope() as session:
            new_event = Event(Date=datetime_string, Action=event)
            session.add(new_event)

    def add_pause(self, pause_time: int, entry_date: datetime.date) -> None:
        date_string = entry_date.isoformat()
        if self.day_exists(date_string):
            self.update_pause(pause_time, date_string)
        else:
            self.insert_pause(pause_time, date_string)

    def update_pause(self, pause_time: int, date_string: str) -> None:
        logger.info("Updating pause time by %s at %s", pause_time, date_string)
        with self.session_scope() as session:
            stmt = update(Pause).where(Pause.Date == date_string).values(Time=Pause.Time + pause_time)
            session.execute(stmt)

    def insert_pause(self, pause_time: int, date_string: str) -> None:
        logger.info("Inserting pause time by %s at %s", pause_time, date_string)
        with self.session_scope() as session:
            new_pause = Pause(Date=date_string, Time=pause_time)
            session.add(new_pause)

    def day_exists(self, date_str: str) -> int:
        with self.session_scope() as session:
            stmt = select(Pause).where(Pause.Date == date_str)
            result = session.execute(stmt).scalar_one_or_none()
            return 1 if result else 0

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
        with self.session_scope() as session:
            start_dt = datetime.datetime.combine(start, datetime.time.min)
            end_dt = datetime.datetime.combine(end, datetime.time.max)
            start_str = start_dt.isoformat()
            end_str = end_dt.isoformat()
            stmt = select(Event).where(Event.Date >= start_str, Event.Date <= end_str).order_by(Event.Date)
            results = session.execute(stmt).scalars().all()
            return [(event.Date, event.Action) for event in results]

    def get_period_pause(self, start: datetime.date, end: datetime.date) -> list[tuple[str, int]]:
        with self.session_scope() as session:
            start_str = start.isoformat()
            end_str = end.isoformat()
            stmt = select(Pause).where(Pause.Date >= start_str, Pause.Date <= end_str).order_by(Pause.Date)
            results = session.execute(stmt).scalars().all()
            return [(pause.Date, pause.Time) for pause in results]

    def delete_event(self, delete_datetime: str) -> None:
        with self.session_scope() as session:
            stmt = delete(Event).where(Event.Date == delete_datetime)
            session.execute(stmt)

    def add_vacation(self, vacation_date: datetime.date) -> None:
        date_string = vacation_date.isoformat()
        logger.info("Adding Vacation on %s", date_string)
        with self.session_scope() as session:
            # only enter if the date does not exist
            existing = session.execute(select(Vacation).where(Vacation.Date == date_string)).scalar_one_or_none()
            if not existing:
                new_vacation = Vacation(Date=date_string)
                session.add(new_vacation)

    def get_vacation_days(self, year: int) -> list[datetime.date]:
        with self.session_scope() as session:
            # Filter by year at database level using date range (ISO format YYYY-MM-DD)
            # String comparison works correctly because ISO date format (YYYY-MM-DD) is
            # lexicographically sortable (year, then month, then day)
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            stmt = select(Vacation).where(Vacation.Date >= start_date, Vacation.Date <= end_date)
            results = session.execute(stmt).scalars().all()
            return [datetime.date.fromisoformat(vacation.Date) for vacation in results]

    def remove_vacation(self, vacation_date: datetime.date) -> None:
        date_string = vacation_date.isoformat()
        logger.info("Removing Vacation on %s", date_string)
        with self.session_scope() as session:
            stmt = delete(Vacation).where(Vacation.Date == date_string)
            session.execute(stmt)


DB_CONTROLLER = DatabaseController()
