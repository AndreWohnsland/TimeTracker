from src.ui_controler import UiControler
from src.config_handler import ConfigHandler
from src.data_exporter import DataExporter
from src.updater import Updater
from src.plot_window import GraphWindow

import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


class ButtonControler:
    def __init__(self, database_controler, ui_element):
        self.version = "v1.1"
        self.db_controler = database_controler
        self.ui_controler = UiControler(ui_element)
        self.config_handler = ConfigHandler()
        self.data_exporter = DataExporter()
        self.updater = Updater()
        self.report_df = pd.DataFrame([])
        self.daily_data = []
        self.no_data = True
        self.past_time = False

    def display_about(self):
        message = f"Version: {self.version}. This App was made with Python and Qt by Andre Wohnsland. Check https://github.com/AndreWohnsland/TimeTracker for more information."
        self.ui_controler.show_message(message)

    def add_event(self, event):
        entry_datetime = datetime.datetime.now()
        entry_datetime = entry_datetime.replace(microsecond=0)
        if self.past_time:
            entry_datetime = self.ui_controler.get_past_datetime()
        self.db_controler.add_event(event, entry_datetime)
        self.ui_controler.show_message(f"Added event {event} at {entry_datetime.strftime('%d-%m-%Y - %H:%M:%S')}")

    def add_start(self):
        self.add_event("start")

    def add_stop(self):
        self.add_event("stop")

    def add_pause(self):
        pause = self.ui_controler.get_pause()
        entry_date = datetime.date.today()
        if self.past_time:
            entry_date = self.ui_controler.get_past_date()
        self.db_controler.add_pause(pause, entry_date)
        self.ui_controler.set_pause(0)
        self.ui_controler.show_message(f"Added pause of {pause} minutes on date {entry_date.strftime('%d-%m-%Y')}")

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
            # self.ui_controler.show_message("No data here, nothing to do here ...")
            self.report_df = pd.DataFrame([])
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
        overtime_report = self.ui_controler.report_choice()
        if overtime_report == None:
            return
        succesful, message = self.data_exporter.export_data(self.report_df, report_date, overtime_report)
        if succesful:
            self.ui_controler.show_message(f"File saved under: {message}")
        else:
            self.ui_controler.show_message(message)

    def switch_dataview(self):
        self.ui_controler.handle_delete_button(self.delete_selected_event)
        if self.no_data:
            return
        self.ui_controler.set_date_toggle()
        if self.ui_controler.view_day():
            self.fill_daily_data()
        else:
            self.fill_montly_data()

    def get_updates(self):
        message = "Want to search and get updates? This could take a short time."
        if self.ui_controler.user_okay(message):
            print("Try to update ...")
            self.updater.update()
            print("Done!")

    def delete_selected_event(self):
        selected_datetime, event = self.ui_controler.get_selected_event()
        if selected_datetime == None:
            return
        if self.ui_controler.user_okay(f"Do you want to delete event {event} at: {selected_datetime}?"):
            print(f"Delete event {event} at: {selected_datetime}")
            self.db_controler.delete_event(selected_datetime)
            self.on_date_change()

    def show_plot(self):
        if self.report_df.empty:
            self.ui_controler.show_message(f"Please select a month with data")
            return
        self.graph_window = GraphWindow(self.report_df)
        self.graph_window.show()
