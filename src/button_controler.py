from src.ui_controler import UiControler
from src.config_handler import ConfigHandler
from src.data_exporter import DataExporter

import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


class ButtonControler:
    def __init__(self, database_controler, ui_element):
        self.db_controler = database_controler
        self.ui_controler = UiControler(ui_element)
        self.config_handler = ConfigHandler()
        self.data_exporter = DataExporter()
        self.report_df = []
        self.daily_data = []
        self.no_data = True

    def add_event(self, event):
        self.db_controler.add_event(event)
        self.ui_controler.show_message(f"Added event {event} at {datetime.datetime.now().strftime('%d-%m-%Y - %H:%M:%S')}")

    def add_start(self):
        self.add_event("start")

    def add_stop(self):
        self.add_event("stop")

    def add_pause(self):
        pause = self.ui_controler.get_pause()
        self.db_controler.add_pause(pause)
        self.ui_controler.set_pause(0)
        self.ui_controler.show_message(f"Added pause of {pause} minutes on date {datetime.datetime.now().strftime('%d-%m-%Y')}")

    def get_user_data(self):
        all_data = self.config_handler.get_config_file_data()
        needed_keys = ["Name", "Personal Number"]
        needed_data = {k: all_data[k] for k in needed_keys}
        for data in needed_data:
            text, ok = self.ui_controler.get_text(data)
            if not ok:
                return
            if text != "":
                all_data[data] = text
        self.config_handler.write_config_file(all_data)

    def get_save_folder(self):
        all_data = self.config_handler.get_config_file_data()
        returned_path = self.ui_controler.get_folder(all_data["savepath"])
        if returned_path:
            all_data["savepath"] = returned_path
        self.config_handler.write_config_file(all_data)

    def show_events(self):
        self.ui_controler.open_event_window(self)
        self.db_controler.get_month_data(datetime.date.today())

    def on_date_change(self):
        self.ui_controler.clear_table()
        selected_date = self.ui_controler.get_event_date()
        self.generate_daily_data(selected_date)
        work_data, pause_data = self.db_controler.get_month_data(selected_date)
        if not work_data:
            self.no_data = True
            self.ui_controler.show_message("No data here, nothing to do here ...")
            self.report_df = []
            return
        self.no_data = False
        work_df = self.create_work_df(work_data)
        day_list = self.get_days_of_month(selected_date)
        daily_time_list = self.generate_montly_time(work_df, day_list)
        self.report_df = self.generate_report_df(day_list, daily_time_list, pause_data)
        if self.ui_controler.view_day():
            self.fill_daily_data()
        else:
            self.fill_montly_data()

    def fill_montly_data(self):
        self.ui_controler.clear_table()
        self.ui_controler.set_monthly_header()
        for index, entry in self.report_df.iterrows():
            needed_data = [index.strftime("%d/%m/%Y"), str(entry["final_time"])]
            self.ui_controler.fill_table(needed_data)

    def fill_daily_data(self):
        self.ui_controler.clear_table()
        self.ui_controler.set_daily_header()
        for entry in self.daily_data:
            self.ui_controler.fill_table(entry)

    def generate_daily_data(self, selected_date):
        day_work, day_pause = self.db_controler.get_day_data(selected_date)
        if day_pause:
            day_work.append(["Pause", str(day_pause[0][1])])
        self.daily_data = day_work

    def create_work_df(self, data):
        df_data = pd.DataFrame(data, columns=["datetime", "event"])
        df_data["datetime"] = df_data["datetime"].apply(pd.to_datetime)
        df_data["time"] = df_data["datetime"].dt.time
        df_data["date"] = df_data["datetime"].dt.floor("D")
        return df_data

    def get_days_of_month(self, selected_date):
        start = datetime.date(selected_date.year, selected_date.month, 1)
        end = start + relativedelta(months=+1)
        return pd.date_range(start, end - datetime.timedelta(days=1), freq="d")

    def calculate_day_time(self, df):
        total_time = datetime.timedelta()
        start_found = False
        for _, row in df.iterrows():
            if not start_found and row["event"] == "start":
                start_found = True
                start_clock = row["time"]
            if start_found and row["event"] == "stop":
                start_found = False
                start = datetime.datetime.combine(datetime.date.min, start_clock)
                stop = datetime.datetime.combine(datetime.date.min, row["time"])
                total_time += stop - start
        return round(total_time.seconds / 60, 2)

    def generate_montly_time(self, df, full_month):
        time_list = []
        for _day in full_month:
            days_data = df[df["date"] == _day]
            calculated_time = self.calculate_day_time(days_data)
            time_list.append(calculated_time)
        return time_list

    def generate_report_df(self, month_list, monthly_time, pause_time):
        work_df = pd.DataFrame({"day": month_list, "worktime": monthly_time})
        work_df.set_index("day", inplace=True)

        pause_df = pd.DataFrame(pause_time, columns=["day", "pause"])
        pause_df["day"] = pause_df["day"].apply(pd.to_datetime)
        pause_df.set_index("day", inplace=True)

        combined_df = pd.concat([work_df, pause_df], axis=1, sort=False)
        combined_df.fillna(0, inplace=True)
        combined_df["final_time"] = combined_df["worktime"] - combined_df["pause"]
        combined_df["final_time"] = combined_df["final_time"].apply(lambda x: max(x, 0))
        # recalculate the time in hours:
        combined_df["final_time"] = combined_df["final_time"].apply(lambda x: round(x / 60, 2))

        return combined_df

    def export_data(self):
        report_date = self.ui_controler.get_event_date()
        succesful, file_path = self.data_exporter.export_data(self.report_df, report_date)
        if succesful:
            self.ui_controler.show_message(f"File saved under: {file_path}")
        else:
            self.ui_controler.show_message(f"Could not open Workbook: {file_path}, is it still opened?")

    def switch_dataview(self):
        if self.no_data:
            return
        self.ui_controler.set_date_toggle()
        if self.ui_controler.view_day():
            self.fill_daily_data()
        else:
            self.fill_montly_data()
