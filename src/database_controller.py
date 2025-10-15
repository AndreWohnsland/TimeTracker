import datetime
import logging
import sqlite3

from dateutil.relativedelta import relativedelta

from src.filepath import DATABASE_PATH

logger = logging.getLogger(__name__)


class DatabaseController:
    """Controller Class to execute all DB queries and return results as Values / Lists / Dictionaries."""

    def __init__(self, db_url: str | None = None) -> None:
        """Abstract Access to the database."""
        self.handler = DatabaseHandler(db_url)

    def add_event(self, event: str, entry_datetime: datetime.datetime) -> None:
        datetime_string = entry_datetime.isoformat()
        logger.info("Add Event: %s, timestamp: %s", event, datetime_string)
        query = "INSERT INTO Events(Date, Action) VALUES(?, ?)"
        self.handler.query_database(
            query,
            (
                datetime_string,
                event,
            ),
        )

    def add_pause(self, pause_time: int, entry_date: datetime.date) -> None:
        date_string = entry_date.isoformat()
        if self.day_exists(date_string):
            self.update_pause(pause_time, date_string)
        else:
            self.insert_pause(pause_time, date_string)

    def update_pause(self, pause_time: int, date_string: str) -> None:
        logger.info("Updating pause time by %s at %s", pause_time, date_string)
        query = "UPDATE OR IGNORE Pause SET Time = Time + ? WHERE Date = ?"
        self.handler.query_database(
            query,
            (
                pause_time,
                date_string,
            ),
        )

    def insert_pause(self, pause_time: int, date_string: str) -> None:
        logger.info("Inserting pause time by %s at %s", pause_time, date_string)
        query = "INSERT INTO Pause(Date, Time) VALUES(?, ?)"
        self.handler.query_database(
            query,
            (
                date_string,
                pause_time,
            ),
        )

    def day_exists(self, date_str: str) -> int:
        query = "SELECT COUNT(*) FROM Pause WHERE Date = ?"
        return self.handler.query_database(query, (date_str,))[0][0]

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
        query = "SELECT Date, Action FROM Events WHERE Date BETWEEN ? AND ? ORDER BY Date"
        return self.handler.query_database(
            query,
            (
                start.isoformat(),
                end.isoformat(),
            ),
        )

    def get_period_pause(self, start: datetime.date, end: datetime.date) -> list[tuple[str, int]]:
        query = "SELECT Date, Time FROM Pause WHERE Date BETWEEN ? AND ? ORDER BY Date"
        return self.handler.query_database(
            query,
            (
                start.isoformat(),
                end.isoformat(),
            ),
        )

    def delete_event(self, delete_datetime: str) -> None:
        query = "DELETE FROM Events WHERE Date = ?"
        self.handler.query_database(query, (delete_datetime,))

    def add_vacation(self, vacation_date: datetime.date) -> None:
        date_string = vacation_date.isoformat()
        logger.info("Adding Vacation on %s", date_string)
        # only enter (ignore) if the date does not exist
        query = "INSERT OR IGNORE INTO Vacation(Date) VALUES(?)"
        self.handler.query_database(query, (date_string,))

    def get_vacation_days(self, year: int) -> list[datetime.date]:
        query = "SELECT Date FROM Vacation WHERE strftime('%Y', Date) = ?"
        # using str(year) is important, since strftime returns a string
        days: list[tuple[str]] = self.handler.query_database(query, (str(year),))
        # convert to a list of dates
        return [datetime.date.fromisoformat(day[0]) for day in days]

    def remove_vacation(self, vacation_date: datetime.date) -> None:
        date_string = vacation_date.isoformat()
        logger.info("Removing Vacation on %s", date_string)
        query = "DELETE FROM Vacation WHERE Date = ?"
        self.handler.query_database(query, (date_string,))


class DatabaseHandler:
    """Handler Class for Connecting and querying Databases."""

    database_path = DATABASE_PATH

    def __init__(self, db_url: str | None = None) -> None:
        """Class to connect and query the database."""
        # check if the old database exists and move it to the new location
        if db_url is None:
            db_url = str(DATABASE_PATH)
        self.db_url = db_url
        if not self.database_path.exists():
            logger.debug("No database detected, creating Database at %s", self.database_path)
        self.connection = sqlite3.connect(self.db_url)
        self.create_tables()

    def __del__(self) -> None:
        """Close the session when the object is deleted."""
        self.connection.close()

    def query_database(self, sql: str, search_tuple: tuple = ()) -> list:
        cursor = self.connection.cursor()
        cursor.execute(sql, search_tuple)

        if sql[0:6].lower() == "select":
            result = cursor.fetchall()
        else:
            self.connection.commit()
            result = []
        cursor.close()
        return result

    def create_tables(self) -> None:
        cursor = self.connection.cursor()
        # get all table names from the database
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Events(
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Date DATETIME NOT NULL,
                Action TEXT NOT NULL);"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Pause(
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Date DATE NOT NULL,
                Time INTEGER NOT NULL);"""
        )
        # create vacation table (id and date)
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Vacation(
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Date DATE NOT NULL);"""
        )
        # Creating the Unique Indexes
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_date ON Pause(Date)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_date_vacation ON Vacation(Date)")
        self.connection.commit()
        cursor.close()


DB_CONTROLLER = DatabaseController()
