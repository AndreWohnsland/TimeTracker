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

    def update_data(self, selected_date: datetime.date | None):
        if selected_date is None:
            selected_date = self.current_date
        self.current_date = selected_date
        self.generate_daily_data(selected_date)
        self.generate_month_data(selected_date)

    def generate_daily_data(self, selected_date: datetime.date):
        day_work, day_pause = DB_CONTROLLER.get_day_data(selected_date)
        if day_pause:
            day_work.append(("Pause", str(day_pause[0][1])))
        self.daily_data = day_work

    def generate_month_data(self, selected_date: datetime.date):
        work_data, pause_data = DB_CONTROLLER.get_month_data(selected_date)
        if not work_data:
            # self.ui_controller.show_message("No data here, nothing to do here ...")
            store.df = pd.DataFrame([])
            return
        work_df = self._create_work_df(work_data)
        day_list = self._get_days_of_month(selected_date)
        daily_time_list = self._generate_monthly_time(work_df, day_list)
        self.df = self._generate_report_df(day_list, daily_time_list, pause_data)

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
        combined_df.fillna(0, inplace=True)
        combined_df["final_time"] = combined_df["work_time"] - combined_df["pause"]
        combined_df["final_time"] = (
            combined_df["final_time"].apply(lambda x: max(x, 0)).apply(lambda x: round(x / 60, 2))
        )
        return combined_df


store = Store(
    holidays=holidays.CountryHoliday(CONFIG_HANDLER.config.country, prov=CONFIG_HANDLER.config.subdiv or None),
)
