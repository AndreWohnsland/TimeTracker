import datetime
from dataclasses import dataclass, field

import holidays
import pandas as pd
from dateutil.relativedelta import relativedelta

from src.config_handler import CONFIG_HANDLER
from src.database_controller import DB_CONTROLLER


@dataclass
class Store:
    df: pd.DataFrame = field(default_factory=pd.DataFrame)
    daily_data: list[tuple[str, str]] = field(default_factory=list)
    current_date: datetime.date = field(default_factory=datetime.date.today)
    # dict with key: (year, month) and value: (hash(raw_data), pd.DataFrame)
    all_data: dict[(tuple[int, int]), tuple[int, pd.DataFrame]] = field(default_factory=dict)
    # Overtime tracking
    total_overtime: float = field(default=0.0)
    overtime_by_year: dict[int, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.generate_all_data()

    def update_data(self, selected_date: datetime.date | None) -> None:
        if selected_date is None:
            selected_date = self.current_date
        self.current_date = selected_date
        self.generate_daily_data(selected_date)
        _, df = self.generate_month_data(selected_date)
        self.df = df
        self.calculate_overtime_totals()

    def _get_holidays(self, year: int) -> list[datetime.date]:
        available_holidays = holidays.CountryHoliday(
            CONFIG_HANDLER.config.country, prov=CONFIG_HANDLER.config.subdiv or None, years=year
        )
        return list(available_holidays.keys())

    def _get_free_days(self, year: int) -> list[datetime.date]:
        vacation_days = DB_CONTROLLER.get_vacation_days(year)
        holiday_list = self._get_holidays(year)
        unique_days = list(set(vacation_days + holiday_list))
        return [day for day in unique_days if day.weekday() in CONFIG_HANDLER.config.workdays]

    def all_non_working_days(self, year: int) -> list[datetime.date]:
        """Return a set of all non-working days: holidays, vacation, and days not in config.workdays."""
        vacation_days = set(DB_CONTROLLER.get_vacation_days(year))
        holiday_days = set(self._get_holidays(year))
        all_days = set(pd.date_range(datetime.date(year, 1, 1), datetime.date(year, 12, 31), freq="d").date)
        non_workdays = {day for day in all_days if day.weekday() not in CONFIG_HANDLER.config.workdays}
        return list(vacation_days | holiday_days | non_workdays)

    def generate_all_data(self) -> None:
        for year in range(2023, datetime.date.today().year + 1):
            for month in range(1, 13):
                self.all_data[(year, month)] = self.generate_month_data(datetime.date(year, month, 1))

    def get_year_data(self, year: int) -> pd.DataFrame:
        year_data = []
        for month in range(1, 13):
            selected_date = datetime.datetime(year, month, 1).date()
            _, df = self.generate_month_data(selected_date)
            year_data.append(df)
        # concat df, aggregate by month (index) and sum the values
        year_data_df = pd.concat(year_data)
        # in case there is no data for the year, return empty df
        if year_data_df.empty:
            return year_data_df

        # Only sum numeric columns, exclude time-based columns
        numeric_columns = ["work_time", "pause", "work", "break_time"]
        columns_to_sum = [col for col in numeric_columns if col in year_data_df.columns]

        year_data_df = year_data_df[columns_to_sum].resample("ME").sum()
        year_data_df.index = year_data_df.index.to_period("M")  # type: ignore
        return year_data_df

    def generate_daily_data(self, selected_date: datetime.date) -> None:
        day_work, day_pause = DB_CONTROLLER.get_day_data(selected_date)
        if day_pause:
            day_work.append(("Pause", str(day_pause[0][1])))
        self.daily_data = day_work

    def generate_month_data(self, selected_date: datetime.date) -> tuple[int, pd.DataFrame]:
        work_data, pause_data = DB_CONTROLLER.get_month_data(selected_date)
        free_days = self._get_free_days(selected_date.year)
        data_hash = hash((tuple(work_data), tuple(pause_data), tuple(free_days)))
        # check if data is already in store, compare hash, also only use cache if not current month
        # This is due to the recomputation of open days (no stop event) and ongoing days (today)
        # increasing over the time of the day, even the data did not change.
        cache_available = (selected_date.year, selected_date.month) in self.all_data
        if cache_available and not self.is_current_month(selected_date):
            last_hash, df = self.all_data[(selected_date.year, selected_date.month)]
            if last_hash == data_hash:
                return (data_hash, df)
        if not work_data:
            return (data_hash, pd.DataFrame([]))
        return (data_hash, self._generate_month_report(work_data, selected_date, free_days, pause_data))

    def _generate_month_report(
        self,
        work_data: list[tuple[str, str]],
        selected_date: datetime.date,
        free_days: list[datetime.date],
        pause_data: list[tuple[str, int]],
    ) -> pd.DataFrame:
        """Generate the complete monthly report DataFrame with all columns."""
        daily_minutes = CONFIG_HANDLER.config.daily_hours * 60

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
            if day.date() in free_days:
                calculated_time += daily_minutes

            day_work_time, start_time, end_time = self._calculate_day_time_with_times(days_data)
            calculated_time += day_work_time
            report_data.append(
                {"day": day, "work_time": calculated_time, "start_time": start_time, "end_time": end_time}
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

        combined_df["pause"] = combined_df["pause"].fillna(0).astype(float)
        combined_df["work_time"] = combined_df["work_time"].apply(lambda x: round(x / 60, 2))
        combined_df["pause"] = combined_df["pause"].apply(lambda x: round(x / 60, 2))
        combined_df["work"] = combined_df["work_time"] - combined_df["pause"]
        combined_df["work"] = combined_df["work"].apply(lambda x: max(x, 0)).apply(lambda x: round(x, 2))
        combined_df["break_time"] = combined_df.apply(_calculate_break_time, axis=1)
        non_working_days = self.all_non_working_days(selected_date.year)
        combined_df["overtime"] = combined_df.apply(lambda row: _calculate_overtime(row, non_working_days), axis=1)
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

        # Collect all non-empty DataFrames with 'overtime' column
        dfs = [df for _, df in self.all_data.values() if not df.empty]
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
        break_minutes = total_minutes - row["work_time"] * 60
        return round(max(break_minutes / 60, 0), 2)

    except (TypeError, ValueError, AttributeError):
        return 0.0


def _calculate_overtime(row: pd.Series, free_days: list[datetime.date]) -> float:
    today = datetime.date.today()
    daily_target = CONFIG_HANDLER.config.daily_hours
    day_date = row.name.date() if hasattr(row.name, "date") else row.name  # type: ignore
    work_hours = row["work"]

    if isinstance(day_date, datetime.date) and day_date > today:
        return 0.0

    # If the day is a free day (holiday/vacation), add daily target to work_hours
    if isinstance(day_date, datetime.date) and day_date in free_days:
        work_hours += daily_target

    return work_hours - daily_target


store = Store()
