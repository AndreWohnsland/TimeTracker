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
from sqlalchemy import create_engine, delete, func, select, update
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from src.filepath import DATABASE_PATH
from src.models import Base, Event, Pause, TimeOff

logger = logging.getLogger(__name__)


class DatabaseController:
    """Controller Class to execute all DB queries and return results as Values / Lists / Dictionaries."""

    database_path = DATABASE_PATH

    def __init__(self, db_url: str | None = None) -> None:
        """Initialize the database controller with SQLAlchemy ORM."""
        self.call_count = 0
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
        self.call_count += 1
        # print(f"DB Call count: {self.call_count}")
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
            new_event = Event(date=entry_datetime, action=event)
            session.add(new_event)

    def add_pause(self, pause_time: int, entry_date: datetime.date) -> None:
        if self.day_exists(entry_date):
            self.update_pause(pause_time, entry_date)
        else:
            self.insert_pause(pause_time, entry_date)

    def update_pause(self, pause_time: int, date: datetime.date) -> None:
        logger.info("Updating pause time by %s at %s", pause_time, date.isoformat())
        with self.session_scope() as session:
            stmt = update(Pause).where(Pause.date == date).values(time=Pause.time + pause_time)
            session.execute(stmt)

    def insert_pause(self, pause_time: int, date: datetime.date) -> None:
        logger.info("Inserting pause time by %s at %s", pause_time, date.isoformat())
        with self.session_scope() as session:
            new_pause = Pause(date=date, time=pause_time)
            session.add(new_pause)

    def day_exists(self, date: datetime.date) -> int:
        with self.session_scope() as session:
            stmt = select(Pause).where(Pause.date == date)
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
            end_dt = datetime.datetime.combine(end, datetime.time.min)
            stmt = select(Event).where(Event.date >= start_dt, Event.date < end_dt).order_by(Event.date)
            results = session.execute(stmt).scalars().all()
            return [(event.date.isoformat(), event.action) for event in results]

    def get_period_pause(self, start: datetime.date, end: datetime.date) -> list[tuple[str, int]]:
        with self.session_scope() as session:
            stmt = select(Pause).where(Pause.date >= start, Pause.date <= end).order_by(Pause.date)
            results = session.execute(stmt).scalars().all()
            return [(pause.date.isoformat(), pause.time) for pause in results]

    def get_months_with_data(self, year: int | None = None) -> list[tuple[int, int]]:
        """Return distinct year/month combinations that have recorded events."""
        with self.session_scope() as session:
            year_col = func.strftime("%Y", Event.date)
            month_col = func.strftime("%m", Event.date)
            stmt = select(year_col, month_col).group_by(year_col, month_col).order_by(year_col, month_col)
            if year is not None:
                stmt = stmt.where(year_col == str(year))
            results = session.execute(stmt).all()
            return [(int(year), int(month)) for year, month in results]

    def delete_event(self, delete_datetime: datetime.datetime) -> None:
        with self.session_scope() as session:
            stmt = delete(Event).where(Event.date == delete_datetime)
            session.execute(stmt)

    def add_time_off(self, day: datetime.date, reason: str) -> None:
        date_string = day.isoformat()
        logger.info("Adding Time Off on %s", date_string)
        with self.session_scope() as session:
            # only enter if the date does not exist
            existing = session.execute(select(TimeOff).where(TimeOff.date == day)).scalar_one_or_none()
            if not existing:
                new_vacation = TimeOff(date=day, reason=reason)
                session.add(new_vacation)

    def get_time_off_days(self, year: int) -> list[datetime.date]:
        return [vacation.date for vacation in self.get_time_off(year)]

    def get_time_off(self, year: int) -> list[TimeOff]:
        with self.session_scope() as session:
            stmt = select(TimeOff).where(
                TimeOff.date >= datetime.date(year, 1, 1),
                TimeOff.date <= datetime.date(year, 12, 31),
            )
            results = session.execute(stmt).scalars().all()
            return list(results)

    def remove_time_off(self, vacation_date: datetime.date) -> None:
        logger.info("Removing Time Off on %s", vacation_date.isoformat())
        with self.session_scope() as session:
            stmt = delete(TimeOff).where(TimeOff.date == vacation_date)
            session.execute(stmt)

    def change_time_off_reason(self, vacation_date: datetime.date, new_reason: str) -> None:
        logger.info("Changing Time Off reason on %s to %s", vacation_date.isoformat(), new_reason)
        with self.session_scope() as session:
            stmt = update(TimeOff).where(TimeOff.date == vacation_date).values(reason=new_reason)
            session.execute(stmt)


DB_CONTROLLER = DatabaseController()
