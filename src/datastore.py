import datetime
from dataclasses import dataclass, field

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.config_handler import CONFIG_HANDLER
from src.database_controller import DB_CONTROLLER


@dataclass
class MonthData:
    df: pd.DataFrame
    data_hash: int
    config_hash: int = field(default_factory=CONFIG_HANDLER.config_hash)

    def is_same_data(self, data_hash: int) -> bool:
        """Compare the data hash of the current month with the stored hash."""
        return self.data_hash == data_hash and self.config_hash == CONFIG_HANDLER.config_hash()


@dataclass
class Store:
    """Data store for time tracking.

    The data frame contains total_time, start_time, end_time, pause, work, break_time, and overtime for days.
    """

    df: pd.DataFrame = field(default_factory=pd.DataFrame)
    daily_data: list[tuple[str, str]] = field(default_factory=list)
    current_date: datetime.date = field(default_factory=datetime.date.today)
    # dict with key: (year, month) and value: MonthData, which contains the needed hashes for data and config)
    all_data: dict[(tuple[int, int]), MonthData] = field(default_factory=dict)
    total_overtime: float = field(default=0.0)
    overtime_by_year: dict[int, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.generate_all_data()

    def update_data(self, selected_date: datetime.date | None) -> None:
        if selected_date is None:
            selected_date = self.current_date
        self.current_date = selected_date
        self.generate_daily_data(selected_date)
        month_data = self.generate_month_data(selected_date)
        self.df = month_data.df
        self.calculate_overtime_totals()

    def get_free_days(self, year: int) -> list[datetime.date]:
        vacation_days = DB_CONTROLLER.get_vacation_days(year)
        holiday_list = CONFIG_HANDLER.config.get_holidays(year)
        unique_days = list(set(vacation_days + holiday_list))
        return [day for day in unique_days if day.weekday() in CONFIG_HANDLER.config.workdays]

    def generate_all_data(self) -> None:
        for year in range(2023, datetime.date.today().year + 1):
            for month in range(1, 13):
                self.all_data[(year, month)] = self.generate_month_data(datetime.date(year, month, 1))

    def get_year_data(self, year: int) -> pd.DataFrame:
        year_data = []
        for month in range(1, 13):
            selected_date = datetime.datetime(year, month, 1).date()
            month_data = self.generate_month_data(selected_date)
            year_data.append(month_data.df)
        year_data_df = pd.concat(year_data)

        if year_data_df.empty:
            return year_data_df

        # Only sum numeric columns, exclude time-based columns
        numeric_columns = ["total_time", "pause", "work", "break_time", "overtime", "target_time"]
        columns_to_sum = [col for col in numeric_columns if col in year_data_df.columns]

        year_data_df = year_data_df[columns_to_sum].resample("ME").sum()
        year_data_df.index = year_data_df.index.to_period("M")  # type: ignore
        return year_data_df

    def generate_daily_data(self, selected_date: datetime.date) -> None:
        day_work, day_pause = DB_CONTROLLER.get_day_data(selected_date)
        if day_pause:
            day_work.append(("Pause", str(day_pause[0][1])))
        self.daily_data = day_work

    def generate_month_data(self, selected_date: datetime.date) -> MonthData:
        work_data, pause_data = DB_CONTROLLER.get_month_data(selected_date)
        free_days = self.get_free_days(selected_date.year)
        data_hash = hash((tuple(work_data), tuple(pause_data), tuple(free_days)))
        # check if we already have the same data computes (no config or DB data changes)
        # skip for current month, since it constantly changes
        last_data = self.all_data.get((selected_date.year, selected_date.month))
        if last_data and last_data.is_same_data(data_hash) and not self.is_current_month(selected_date):
            return last_data
        if not work_data:
            return MonthData(df=pd.DataFrame([]), data_hash=data_hash)
        return MonthData(
            df=self._generate_month_report(work_data, selected_date, free_days, pause_data),
            data_hash=data_hash,
        )

    def _generate_month_report(
        self,
        work_data: list[tuple[str, str]],
        selected_date: datetime.date,
        free_days: list[datetime.date],
        pause_data: list[tuple[str, int]],
    ) -> pd.DataFrame:
        """Generate the complete monthly report DataFrame with all columns."""
        work_df = pd.DataFrame(work_data, columns=["datetime", "event"])
        work_df["datetime"] = work_df["datetime"].apply(pd.to_datetime)
        work_df["time"] = work_df["datetime"].dt.time
        work_df["date"] = work_df["datetime"].dt.date

        start = datetime.date(selected_date.year, selected_date.month, 1)
        end = start + relativedelta(months=+1)

        report_data = []

        for day in pd.date_range(start, end - datetime.timedelta(days=1), freq="d"):
            days_data = work_df[work_df["date"] == day.date()]
            calculated_time = 0.0
            # Free days adds the daily target time to the total time (in case the user still worked to get overtime)
            if day.date() in free_days:
                calculated_time += CONFIG_HANDLER.config.get_daily_hours_at(day.weekday()) * 60

            day_work_time, start_time, end_time = self._calculate_day_time_with_times(days_data)
            calculated_time += day_work_time
            report_data.append(
                {
                    "day": day,
                    "total_time": calculated_time,
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )

        combined_df = pd.DataFrame(report_data)
        combined_df.set_index("day", inplace=True)

        if pause_data:
            pause_df = pd.DataFrame(pause_data, columns=["day", "pause"])
            pause_df["day"] = pause_df["day"].apply(pd.to_datetime)
            pause_df.set_index("day", inplace=True)
            combined_df = pd.concat([combined_df, pause_df], axis=1, sort=False)
        else:
            combined_df["pause"] = 0.0

        combined_df["pause"] = combined_df["pause"].fillna(0.0).astype(float)
        combined_df["pause"] = combined_df["pause"].apply(lambda x: round(x / 60, 2))
        combined_df["total_time"] = combined_df["total_time"].apply(lambda x: round(x / 60, 2))
        combined_df["work"] = combined_df["total_time"] - combined_df["pause"]
        combined_df["work"] = combined_df["work"].apply(lambda x: max(x, 0)).round(2)
        combined_df["break_time"] = combined_df.apply(_calculate_break_time, axis=1)
        combined_df["target_time"] = combined_df.apply(_calculate_target_time, axis=1)
        combined_df["overtime"] = combined_df.apply(lambda row: _calculate_overtime(row), axis=1)
        combined_df["overtime"] = combined_df["overtime"].round(2)

        return combined_df

    def _calculate_day_time_with_times(
        self, df: pd.DataFrame
    ) -> tuple[float, datetime.time | None, datetime.time | None]:
        """Calculate the total work time for a day, along with the start and end times.

        Args:
            df (pd.DataFrame): DataFrame containing work log entries for a specific day.

        Returns:
            tuple[float, datetime.time | None, datetime.time | None]: A tuple containing the total work time in minutes,
            the earliest start time, and the latest end time.

        """
        if df.empty:
            return 0.0, None, None

        total_time = datetime.timedelta()
        start_found = False
        earliest_start = None
        latest_end = None

        for _, row in df.iterrows():
            if not start_found and row["event"] == "start":
                start_found = True
                start_time: datetime.datetime = row["datetime"]
                if earliest_start is None:
                    earliest_start = start_time.time()
            elif start_found and row["event"] == "stop":
                start_found = False
                end_time: datetime.datetime = row["datetime"]
                latest_end = end_time.time()
                total_time += row["datetime"] - start_time

        # check if a start was found, but no stop, in this case, either the user forgot to stop the clock or the
        # day is currently ongoing (date = today)
        if not start_found:
            return round(total_time.seconds / 60, 2), earliest_start, latest_end

        # check for today.
        today = datetime.date.today()
        # check if start clock is the same day as today
        if df.iloc[0]["date"] == today:
            current_time = datetime.datetime.now()
            total_time += current_time - start_time
            latest_end = current_time.time()
        # else, use the midnight of this day as end
        else:
            next_day = start_time + datetime.timedelta(days=1)
            end_of_day = datetime.datetime.combine(next_day, datetime.time.min)  # type: ignore
            total_time += end_of_day - start_time
            latest_end = end_of_day.time()

        return round(total_time.seconds / 60, 2), earliest_start, latest_end

    def is_current_month(self, date: datetime.date) -> bool:
        now = datetime.date.today()
        return (date.year, date.month) == (now.year, now.month)

    def calculate_overtime_totals(self) -> None:
        """Calculate total overtime and overtime by year."""
        self.total_overtime = 0.0
        self.overtime_by_year = {}

        # re-calculate all data (caches might be invalid)
        self.generate_all_data()
        dfs = [month_data.df for month_data in self.all_data.values() if not month_data.df.empty]
        if not dfs:
            return
        merged_df = pd.concat(dfs)
        overtime_by_year = merged_df.groupby(merged_df.index.year)["overtime"].sum()  # type: ignore
        for year, value in overtime_by_year.items():
            self.overtime_by_year[year] = round(value, 2)
        self.total_overtime = round(merged_df["overtime"].sum(), 2)


def _calculate_break_time(row: pd.Series) -> float:
    start_time = row["start_time"]
    end_time = row["end_time"]

    if pd.isna(start_time) or pd.isna(end_time) or start_time is None or end_time is None:
        return 0.0
    if not isinstance(start_time, datetime.time) or not isinstance(end_time, datetime.time):
        return 0.0

    try:
        start_dt = datetime.datetime.combine(datetime.date.today(), start_time)
        end_dt = datetime.datetime.combine(datetime.date.today(), end_time)
        if end_dt < start_dt:
            end_dt += datetime.timedelta(days=1)

        total_minutes = (end_dt - start_dt).total_seconds() / 60
        break_minutes = total_minutes - row["total_time"] * 60
        return round(max(break_minutes / 60, 0), 2)

    except (TypeError, ValueError, AttributeError):
        return 0.0


def _calculate_target_time(row: pd.Series) -> float:
    """Calculate the target time for a given row."""
    day_date = row.name.date() if hasattr(row.name, "date") else row.name  # type: ignore
    # Make typing happy, should not happen here

    if not isinstance(day_date, datetime.date):
        return 0.0
    if day_date > datetime.date.today():
        return 0.0

    return CONFIG_HANDLER.config.get_daily_hours_at(day_date.weekday())


def _calculate_overtime(row: pd.Series) -> float:
    today = datetime.date.today()
    daily_target: float = row["target_time"]
    day_date = row.name.date() if hasattr(row.name, "date") else row.name  # type: ignore
    work_hours: float = row["work"]

    # Make typing happy, should not happen here
    if not isinstance(day_date, datetime.date):
        return 0.0
    if day_date >= today:
        return 0.0

    return work_hours - daily_target


store = Store()
