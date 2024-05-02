import datetime
from dataclasses import dataclass, field
from dateutil.relativedelta import relativedelta

import holidays
from holidays import HolidayBase
import pandas as pd

from src.database_controller import DB_CONTROLLER
from src.config_handler import CONFIG_HANDLER


@dataclass
class Store:
    holidays: HolidayBase
    df: pd.DataFrame = pd.DataFrame()
    daily_data: list[tuple[str, str]] = field(default_factory=list)
    current_date: datetime.date = datetime.date.today()
    # dict with key: (year, month) and value: (hash(raw_data), pd.DataFrame)
    all_data: dict[(tuple[int, int]), tuple[int, pd.DataFrame]] = field(default_factory=dict)

    def __post_init__(self):
        self.generate_all_data()

    def update_data(self, selected_date: datetime.date | None):
        if selected_date is None:
            selected_date = self.current_date
        self.current_date = selected_date
        self.generate_daily_data(selected_date)
        _, df = self.generate_month_data(selected_date)
        self.df = df

    def generate_all_data(self):
        for year in range(2023, datetime.date.today().year + 1):
            for month in range(1, 13):
                self.all_data[(year, month)] = self.generate_month_data(datetime.date(year, month, 1))

    def get_year_data(self, year: int):
        year_data = []
        for month in range(1, 13):
            selected_date = datetime.datetime(year, month, 1).date()
            _, df = self.generate_month_data(selected_date)
            year_data.append(df)
        # concat df, aggregate by month (index) and sum the values
        year_data = pd.concat(year_data).resample("ME").sum()
        year_data.index = year_data.index.to_period("M")  # type: ignore
        return year_data

    def generate_daily_data(self, selected_date: datetime.date):
        day_work, day_pause = DB_CONTROLLER.get_day_data(selected_date)
        if day_pause:
            day_work.append(("Pause", str(day_pause[0][1])))
        self.daily_data = day_work

    def generate_month_data(self, selected_date: datetime.date):
        work_data, pause_data = DB_CONTROLLER.get_month_data(selected_date)
        data_hash = hash((tuple(work_data), tuple(pause_data)))
        # check if data is already in store, compare hash
        if (selected_date.year, selected_date.month) in self.all_data:
            last_hash, df = self.all_data[(selected_date.year, selected_date.month)]
            if last_hash == data_hash:
                return (data_hash, df)
        if not work_data:
            return (data_hash, pd.DataFrame([]))
        work_df = self._create_work_df(work_data)
        day_list = self._get_days_of_month(selected_date)
        daily_time_list = self._generate_monthly_time(work_df, day_list)
        return (data_hash, self._generate_report_df(day_list, daily_time_list, pause_data))

    def _create_work_df(self, data: list[tuple[str, str]]):
        df_data = pd.DataFrame(data, columns=["datetime", "event"])
        df_data["datetime"] = df_data["datetime"].apply(pd.to_datetime)
        df_data["time"] = df_data["datetime"].dt.time
        df_data["date"] = df_data["datetime"].dt.date
        return df_data

    def _get_days_of_month(self, selected_date: datetime.date) -> pd.DatetimeIndex:
        start = datetime.date(selected_date.year, selected_date.month, 1)
        end = start + relativedelta(months=+1)
        return pd.date_range(start, end - datetime.timedelta(days=1), freq="d")

    def _generate_monthly_time(self, df: pd.DataFrame, full_month: pd.DatetimeIndex) -> list[float]:
        time_list = []
        for _day in full_month:
            days_data = df[df["date"] == _day.date()]
            calculated_time = self._calculate_day_time(days_data)
            time_list.append(calculated_time)
        return time_list

    def _calculate_day_time(self, df: pd.DataFrame):
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
    ):
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


store = Store(
    holidays=holidays.CountryHoliday(CONFIG_HANDLER.config.country, prov=CONFIG_HANDLER.config.subdiv or None),
)
