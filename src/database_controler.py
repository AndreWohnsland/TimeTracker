import sqlite3
import os
from pathlib import Path
import datetime

from dateutil.relativedelta import relativedelta


class DatabaseControler:
    """ Controler Class to execute all DB querries and return results as Values / Lists / Dictionaries"""

    def __init__(self):
        self.handler = DatabaseHandler()

    def add_event(self, event, entry_datetime):
        datetime_string = entry_datetime.isoformat()
        print(f"Add Event: {event}, timestamp: {datetime_string}")
        query = "INSERT INTO Events(Date, Action) VALUES(?, ?)"
        self.handler.query_database(query, (datetime_string, event,))

    def add_pause(self, pausetime, entry_date):
        date_string = entry_date.isoformat()
        if self.day_exists(date_string):
            self.update_pause(pausetime, date_string)
        else:
            self.insert_pause(pausetime, date_string)

    def update_pause(self, pausetime, date_string):
        print(f"Updating pause time by {pausetime} at {date_string}")
        query = "UPDATE OR IGNORE Pause SET Time = Time + ? WHERE Date = ?"
        self.handler.query_database(query, (pausetime, date_string,))

    def insert_pause(self, pausetime, date_string):
        print(f"Inserting pause time by {pausetime} at {date_string}")
        query = "INSERT INTO Pause(Date, Time) VALUES(?, ?)"
        self.handler.query_database(query, (date_string, pausetime,))

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
        return self.handler.query_database(query, (start.isoformat(), end.isoformat(),))

    def get_period_pause(self, start, end):
        query = "SELECT Date, Time FROM Pause WHERE Date BETWEEN ? AND ? ORDER BY Date"
        return self.handler.query_database(query, (start.isoformat(), end.isoformat(),))


class DatabaseHandler:
    """Handler Class for Connecting and querring Databases"""

    dirpath = os.path.dirname(__file__)
    data_folder = "data"
    database_name = "timedata"
    database_path = os.path.join(dirpath, "..", data_folder, f"{database_name}.db")

    def __init__(self):
        self.database_path = DatabaseHandler.database_path
        if not Path(self.database_path).exists():
            print("creating Database")
            self.create_tables()

    def connect_database(self):
        self.database = sqlite3.connect(self.database_path)
        self.cursor = self.database.cursor()

    def query_database(self, sql, serachtuple=()):
        self.connect_database()
        self.cursor.execute(sql, serachtuple)

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
