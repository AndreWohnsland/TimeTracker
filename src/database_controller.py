import sqlite3
from pathlib import Path
import datetime

from dateutil.relativedelta import relativedelta

from src.utils import get_app_dir


class DatabaseController:
    """Controller Class to execute all DB queries and return results as Values / Lists / Dictionaries"""

    def __init__(self):
        self.handler = DatabaseHandler()

    def add_event(self, event, entry_datetime):
        datetime_string = entry_datetime.isoformat()
        print(f"Add Event: {event}, timestamp: {datetime_string}")
        query = "INSERT INTO Events(Date, Action) VALUES(?, ?)"
        self.handler.query_database(
            query,
            (
                datetime_string,
                event,
            ),
        )

    def add_pause(self, pause_time, entry_date):
        date_string = entry_date.isoformat()
        if self.day_exists(date_string):
            self.update_pause(pause_time, date_string)
        else:
            self.insert_pause(pause_time, date_string)

    def update_pause(self, pause_time, date_string):
        print(f"Updating pause time by {pause_time} at {date_string}")
        query = "UPDATE OR IGNORE Pause SET Time = Time + ? WHERE Date = ?"
        self.handler.query_database(
            query,
            (
                pause_time,
                date_string,
            ),
        )

    def insert_pause(self, pause_time, date_string):
        print(f"Inserting pause time by {pause_time} at {date_string}")
        query = "INSERT INTO Pause(Date, Time) VALUES(?, ?)"
        self.handler.query_database(
            query,
            (
                date_string,
                pause_time,
            ),
        )

    def day_exists(self, day):
        query = "SELECT COUNT(*) FROM Pause WHERE Date = ?"
        amount = self.handler.query_database(query, (day,))[0][0]
        return amount

    def get_month_data(self, search_date):
        start = datetime.date(search_date.year, search_date.month, 1)
        end = start + relativedelta(months=+1)
        work = self.get_period_work(start, end)
        pause = self.get_period_pause(start, end)
        return work, pause

    def get_day_data(self, day):
        start = day
        end = start + relativedelta(days=+1)
        work = self.get_period_work(start, end)
        pause = self.get_period_pause(start, start)
        return work, pause

    def get_period_work(self, start, end):
        query = "SELECT Date, Action FROM Events WHERE Date BETWEEN ? AND ? ORDER BY Date"
        return self.handler.query_database(
            query,
            (
                start.isoformat(),
                end.isoformat(),
            ),
        )

    def get_period_pause(self, start, end):
        query = "SELECT Date, Time FROM Pause WHERE Date BETWEEN ? AND ? ORDER BY Date"
        return self.handler.query_database(
            query,
            (
                start.isoformat(),
                end.isoformat(),
            ),
        )

    def delete_event(self, delete_datetime):
        query = "DELETE FROM Events WHERE Date = ?"
        self.handler.query_database(query, (delete_datetime,))


class DatabaseHandler:
    """Handler Class for Connecting and querying Databases"""

    def __init__(self):
        # get the old database path (this if for old users, who have the database in the data folder)
        old_database_path = Path(__file__).absolute().parents[1] / "data" / "timedata.db"
        save_folder = get_app_dir()
        # need to create the folder once
        if not save_folder.exists():
            save_folder.mkdir(parents=True)
        # check if the old database exists and move it to the new location
        self.database_path = save_folder / "time_data.db"
        if old_database_path.exists():
            print(f"Old Database found at {old_database_path}, moving to new location to {self.database_path}")
            old_database_path.rename(self.database_path)
        if not Path(self.database_path).exists():
            print(f"No database detected, creating Database at {self.database_path}")
            self.create_tables()

    def connect_database(self):
        self.database = sqlite3.connect(self.database_path)
        self.cursor = self.database.cursor()

    def query_database(self, sql, search_tuple=()):
        self.connect_database()
        self.cursor.execute(sql, search_tuple)

        if sql[0:6].lower() == "select":
            result = self.cursor.fetchall()
        else:
            self.database.commit()
            result = []
        self.database.close()
        return result

    def create_tables(self):
        self.connect_database()
        # Creates each Table
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Events(
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Date DATETIME NOT NULL,
                Action TEXT NOT NULL);"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Pause(
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Date DATE NOT NULL,
                Time INTEGER NOT NULL);"""
        )
        # Creating the Unique Indexes
        self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_date ON Pause(Date)")
        self.database.commit()
        self.database.close()
