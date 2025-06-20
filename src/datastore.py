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

    def __post_init__(self) -> None:
        self.generate_all_data()

    def update_data(self, selected_date: datetime.date | None) -> None:
        if selected_date is None:
            selected_date = self.current_date
        self.current_date = selected_date
        self.generate_daily_data(selected_date)
        _, df = self.generate_month_data(selected_date)
        self.df = df

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
        year_data_df = year_data_df.resample("ME").sum()
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
        work_df = self._create_work_df(work_data)
        day_list = self._get_days_of_month(selected_date)
        daily_time_list = self._generate_monthly_time(work_df, day_list, free_days)
        return (data_hash, self._generate_report_df(day_list, daily_time_list, pause_data))

    def _create_work_df(self, data: list[tuple[str, str]]) -> pd.DataFrame:
        df_data = pd.DataFrame(data, columns=["datetime", "event"])
        df_data["datetime"] = df_data["datetime"].apply(pd.to_datetime)
        df_data["time"] = df_data["datetime"].dt.time
        df_data["date"] = df_data["datetime"].dt.date
        return df_data

    def _get_days_of_month(self, selected_date: datetime.date) -> pd.DatetimeIndex:
        start = datetime.date(selected_date.year, selected_date.month, 1)
        end = start + relativedelta(months=+1)
        return pd.date_range(start, end - datetime.timedelta(days=1), freq="d")

    def _generate_monthly_time(
        self, df: pd.DataFrame, full_month: pd.DatetimeIndex, free_days: list[datetime.date]
    ) -> list[float]:
        time_list: list[float] = []
        daily_minutes = CONFIG_HANDLER.config.daily_hours * 60
        for _day in full_month:
            days_data = df[df["date"] == _day.date()]
            calculated_time = 0.0
            # when we got a free day, we get the working time for this day
            if _day.date() in free_days:
                calculated_time += daily_minutes
            # also adds working time (in case of work in free day we get overtime)
            calculated_time += self._calculate_day_time(days_data)
            time_list.append(calculated_time)
        return time_list

    def _calculate_day_time(self, df: pd.DataFrame) -> float:
        total_time = datetime.timedelta()
        start_found = False
        for _, row in df.iterrows():
            if not start_found and row["event"] == "start":
                start_found = True
                start_time: datetime.datetime = row["datetime"]
            elif start_found and row["event"] == "stop":
                start_found = False
                total_time += row["datetime"] - start_time
        # check if a start was found, but no stop, in this case, either the user forgot to stop the clock or the
        # day is currently ongoing (date = today)
        if not start_found:
            return round(total_time.seconds / 60, 2)
        # check for today.
        today = datetime.date.today()
        # check if start clock is the same day as today
        if df.iloc[0]["date"] == today:
            total_time += datetime.datetime.now() - start_time
        # else, use the midnight of this day as end
        else:
            next_day = start_time + datetime.timedelta(days=1)
            end_of_day = datetime.datetime.combine(next_day, datetime.time.min)  # type: ignore
            total_time += end_of_day - start_time
        return round(total_time.seconds / 60, 2)

    def _generate_report_df(
        self, month_list: pd.DatetimeIndex, monthly_time: list[float], pause_time: list[tuple[str, int]]
    ) -> pd.DataFrame:
        work_df = pd.DataFrame({"day": month_list, "work_time": monthly_time})
        work_df.set_index("day", inplace=True)

        pause_df = pd.DataFrame(pause_time, columns=["day", "pause"])
        pause_df["day"] = pause_df["day"].apply(pd.to_datetime)
        pause_df.set_index("day", inplace=True)

        combined_df = pd.concat([work_df, pause_df], axis=1, sort=False)
        combined_df["pause"] = combined_df["pause"].astype(float)
        combined_df.fillna(0, inplace=True)
        combined_df["work_time"] = combined_df["work_time"].apply(lambda x: round(x / 60, 2))
        combined_df["pause"] = combined_df["pause"].apply(lambda x: round(x / 60, 2))
        combined_df["work"] = combined_df["work_time"] - combined_df["pause"]
        combined_df["work"] = combined_df["work"].apply(lambda x: max(x, 0)).apply(lambda x: round(x, 2))
        return combined_df

    def is_current_month(self, date: datetime.date) -> bool:
        now = datetime.date.today()
        return (date.year, date.month) == (now.year, now.month)


store = Store()
