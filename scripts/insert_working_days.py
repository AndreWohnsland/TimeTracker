import datetime
import random
import sys
from pathlib import Path

import holidays

parent_path = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(parent_path))

from src.config_handler import CONFIG_HANDLER  # noqa: E402
from src.database_controller import DB_CONTROLLER  # noqa: E402


# Helper to check if a date is a working day (not weekend, not holiday, not vacation)
def is_working_day(date: datetime.date, holidays: set, vacations: set, workdays: set) -> bool:
    return date.weekday() in workdays and date not in holidays and date not in vacations


def main() -> None:
    # Define the date range
    start_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2025, 6, 30)

    # Get holidays and vacations for 2025
    country = CONFIG_HANDLER.config.country
    subdiv = CONFIG_HANDLER.config.subdiv or None
    holidays_set = set(holidays.CountryHoliday(country, prov=subdiv, years=2025).keys())
    vacations_set = set(DB_CONTROLLER.get_vacation_days(2025))
    workdays_set = set(CONFIG_HANDLER.config.workdays)

    current = start_date
    while current <= end_date:
        if is_working_day(current, holidays_set, vacations_set, workdays_set):
            # Random start between 6:00 and 7:00
            start_hour = random.randint(6, 6)
            start_minute = random.randint(0, 59)
            start_dt = datetime.datetime.combine(current, datetime.time(start_hour, start_minute))
            # Random end between 15:00 and 16:00
            end_hour = random.randint(15, 15)
            end_minute = random.randint(0, 59)
            end_dt = datetime.datetime.combine(current, datetime.time(end_hour, end_minute))
            # Insert start event
            DB_CONTROLLER.add_event("start", start_dt)
            # 40% chance for a break from 12:00 to 13:00
            pause_chance = 0.8
            if random.random() < pause_chance:
                pause_start = datetime.datetime.combine(current, datetime.time(12, 0))
                pause_end = datetime.datetime.combine(current, datetime.time(13, 0))
                DB_CONTROLLER.add_event("stop", pause_start)
                DB_CONTROLLER.add_event("start", pause_end)
                # Add pause (60 minutes)
            # Insert end event
            DB_CONTROLLER.add_event("stop", end_dt)
        current += datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
