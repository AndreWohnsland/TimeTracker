import datetime
from collections.abc import Generator
from typing import Any

import pytest

from src.database_controller import DatabaseController


# Helper to check if a date is a working day (not weekend, not holiday, not vacation)
def _is_working_day(date: datetime.date, holidays: set, vacations: set, workdays: set) -> bool:
    return date.weekday() in workdays and date not in holidays and date not in vacations


@pytest.fixture
def db_controller() -> Generator[DatabaseController, Any, None]:
    # Define the date range
    start_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2025, 12, 30)
    vacations_set = {datetime.date(2025, 7, x) for x in range(1, 31)}  # Full vacation in July
    workdays_set = {0, 1, 2, 3, 4}

    current = start_date
    db_controller = DatabaseController(db_url=":memory:")
    while current <= end_date:
        if _is_working_day(current, set(), vacations_set, workdays_set):
            start_dt = datetime.datetime.combine(current, datetime.time(6, 0))
            end_dt = datetime.datetime.combine(current, datetime.time(14, 30))
            pause_start = datetime.datetime.combine(current, datetime.time(12, 0))
            pause_end = datetime.datetime.combine(current, datetime.time(13, 0))
            db_controller.add_event("start", start_dt)
            if current.day % 2 == 0:
                db_controller.add_event("stop", pause_start)
                db_controller.add_event("start", pause_end)
            db_controller.add_event("stop", end_dt)
        current += datetime.timedelta(days=1)

    yield db_controller
