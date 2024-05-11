from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
import calendar

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QWidget
import pandas as pd

from src.config_handler import CONFIG_HANDLER
from src.filepath import REPORTS_PATH
from src.ui_controller import UI_CONTROLLER
from src.database_controller import DB_CONTROLLER
from src.ui_controller import UI_CONTROLLER as UIC
from src.data_exporter import EXPORTER
from ui import Ui_DataWindow
from src.datastore import store
from src.icons import get_app_icon
from src.utils import get_font_color, get_background_color

if TYPE_CHECKING:
    from src.ui_mainwindow import MainWindow


class GraphWindow(QWidget, Ui_DataWindow):
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.setWindowIcon(get_app_icon())
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint  # type: ignore
        )
        # setting all the params
        self.text_color = get_font_color()
        self.background_color = get_background_color()
        self.set_plot_parameters()
        self.figure = plt.figure(figsize=(13, 8), dpi=128, tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.container.addWidget(self.canvas)

        # keep track of prev date to only update the plot on month change
        self.prev_date = self.date_edit.date()
        self.save_button.clicked.connect(self.save_plot)
        self.plot_type_group.buttonClicked.connect(self.plot)
        self.date_edit.dateChanged.connect(self.update_date)

        self.export_button.clicked.connect(self.export_data)
        self.switch_button.clicked.connect(self.switch_data_view)
        self.delete_event_button.clicked.connect(self.delete_selected_event)

        self.delete_button = None
        # workaround to prevent the date change to trigger the plot
        self.programmatic_change = False
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.handle_delete_button()

    def set_plot_parameters(self):
        plt.rcParams["date.autoformatter.day"] = "%d"
        plt.rcParams["date.autoformatter.month"] = "%b"
        plt.rcParams["figure.facecolor"] = self.background_color
        plt.rcParams["axes.facecolor"] = self.background_color
        plt.rcParams["text.color"] = self.text_color
        plt.rcParams["axes.edgecolor"] = self.text_color
        plt.rcParams["xtick.color"] = self.text_color
        plt.rcParams["ytick.color"] = self.text_color
        plt.rcParams["axes.labelcolor"] = self.text_color
        plt.rcParams["axes.titlecolor"] = self.text_color
        # Despine the plot right and top
        plt.rcParams["axes.spines.right"] = False
        plt.rcParams["axes.spines.top"] = False

    def update_date(self):
        """Update the date and plot the new data."""
        prev_date = self.prev_date
        self.prev_date = self.date_edit.date()
        if self.programmatic_change:
            return
        store.current_date = self.date_edit.date().toPyDate()
        UIC.clear_table(self.tableWidget)
        store.update_data(self.selected_date)
        if self.view_day:
            self.fill_daily_data()
        else:
            self.fill_monthly_data()
        # only plot on month change (otherwise no plot will change)
        if prev_date.month() != self.date_edit.date().month():
            self.plot()

    def plot(self):
        # clears the old values and then adds a subplot to insert all the data
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # update the store before plotting
        store.update_data(None)
        # get the store date -> this is needed to show the correct month in the dropdown
        # if the user did not change it there before
        self.programmatic_change = True
        self.date_edit.setDate(store.current_date)
        self.programmatic_change = False

        if self.radio_month.isChecked():
            df = store.df.copy()
            needed_hours = CONFIG_HANDLER.config.daily_hours
        else:
            df = store.get_year_data(store.current_date.year)
            # lets use "easy" constant monthly working hours for now
            needed_hours = CONFIG_HANDLER.config.weekly_hours * 52 / 12
        plot_df = self.adjust_df_for_plot(df, needed_hours)
        plot_df.plot.bar(stacked=True, ax=ax, width=0.8, color=["#2693ff", "#ff4e26", "#25cf5e"], zorder=2)
        ax.legend(fancybox=True, framealpha=0.9)

        ax.axhline(needed_hours, color=self.text_color, ls="--", lw=1, zorder=3)
        ax.yaxis.grid(True, lw=1, ls=":", color=self.text_color, alpha=0.2, zorder=1)
        ax.xaxis.get_label().set_visible(False)

        if self.radio_month.isChecked():
            tick_labels = [day.strftime("%d") for day in df.index]
            rotation = "vertical"
            # shift the xticks to the middle of the bars
        else:
            tick_labels = [month.strftime("%b") for month in df.index]
            rotation = "horizontal"
        ax.set_xticklabels(tick_labels, rotation=rotation)

        # hide the x ticks
        ax.tick_params(axis="x", which="both", bottom=False, top=False)
        if self.radio_month.isChecked():
            title = f"Working time for {store.current_date.strftime('%B %Y')}"
        else:
            title = f"Working time for {store.current_date.year}"
        ax.set_title(title, weight="bold", fontsize=15)
        # self.figure.autofmt_xdate(rotation=90)
        self.canvas.draw()

    def adjust_df_for_plot(self, df: pd.DataFrame, needed_hours: float) -> pd.DataFrame:
        """Adjust the dataframe for plotting."""
        # check if df got pause column, else add it with 0
        if df.empty:
            df = self._create_dummy_df()
        if "pause" not in df.columns:
            df["pause"] = 0
        df["overtime"] = df["work"] - needed_hours
        df["overtime"] = df["overtime"].clip(lower=0)
        df["work"] = df["work"].clip(upper=needed_hours, lower=0)
        return df[["work", "overtime", "pause"]]

    def _create_dummy_df(self) -> pd.DataFrame:
        """Create a dummy dataframe if no data is available."""
        date = store.current_date
        if self.radio_month.isChecked():
            day_in_month = calendar.monthrange(date.year, date.month)[1]
            # build data for each day of the month, containing only zeros
            days = pd.date_range(start=date.replace(day=1), periods=day_in_month, freq="D")
            data = {"work": [0] * day_in_month, "pause": [0] * day_in_month}
            return pd.DataFrame(data, index=days)
        months = pd.date_range(start=date.replace(month=1, day=1), periods=12, freq="M")
        data = {"work": [0] * 12, "pause": [0] * 12}
        return pd.DataFrame(data, index=months)

    def save_plot(self):
        """Save the plot as png."""
        folder = Path(REPORTS_PATH)
        # only use the save path if it is set
        if CONFIG_HANDLER.config.save_path:
            folder = Path(CONFIG_HANDLER.config.save_path)
        # Generate Month or Year name for the file
        if self.radio_month.isChecked():
            name = f"{store.current_date.strftime('%Y_%m')}_plot.png"
        else:
            name = f"{store.current_date.strftime('%Y')}_plot.png"
        file_name = folder / name

        # check if the file already exists, if so, add a suffix until the file is unique
        suffix = 1
        save_file_name = file_name
        while True:
            if not save_file_name.exists():
                break
            save_file_name = folder / f"{file_name.stem}_{suffix}{file_name.suffix}"
            suffix += 1

        self.figure.savefig(save_file_name, transparent=False)
        UI_CONTROLLER.show_message(f"Plot saved to {save_file_name}")

    # Data Things

    def update_data(self):
        self.on_date_change()

    def on_date_change(self):
        UIC.clear_table(self.tableWidget)
        store.update_data(self.selected_date)
        if self.view_day:
            self.fill_daily_data()
        else:
            self.fill_monthly_data()

    def export_data(self):
        overtime_report = UIC.report_choice()
        if overtime_report is None:
            return
        successful, message = EXPORTER.export_data(store.df, self.selected_date, overtime_report)
        if successful:
            UIC.show_message(f"File saved under: {message}")
        else:
            UIC.show_message(message)

    def switch_data_view(self):
        self.handle_delete_button()

        self.set_date_toggle()
        if self.view_day:
            self.fill_daily_data()
        else:
            self.fill_monthly_data()

    def fill_monthly_data(self):
        UIC.clear_table(self.tableWidget)
        UIC.set_header_names(self.tableWidget, "Date", "Worktime (h)")
        for index, entry in store.df.iterrows():
            needed_data = [index.strftime("%d/%m/%Y"), str(entry["work"])]  # type: ignore
            UIC.fill_table(self.tableWidget, needed_data)

    def fill_daily_data(self):
        UIC.clear_table(self.tableWidget)
        UIC.set_header_names(self.tableWidget, "Datetime / Type", "Event / Pausetime (min)")
        for entry in store.daily_data:
            UIC.fill_table(self.tableWidget, entry)

    @property
    def view_day(self):
        if self.switch_button.isChecked():
            return True
        return False

    def handle_delete_button(self):
        if self.view_day:
            self.delete_event_button.show()
        else:
            self.delete_event_button.hide()

    def set_date_toggle(self):
        if self.view_day:
            self.switch_button.setText("Day")
        else:
            self.switch_button.setText("Month")

    def delete_selected_event(self):
        selected_datetime, event = self.get_selected_event()
        if selected_datetime is None or event is None:
            return
        if UIC.user_okay(f"Do you want to delete event {event} at: {selected_datetime}?"):
            print(f"Delete event {event} at: {selected_datetime}")
            DB_CONTROLLER.delete_event(selected_datetime)
            self.on_date_change()
            self.main_window.update_plot_window()

    def get_selected_event(self) -> tuple[str, str] | tuple[None, None]:
        indexes = self.tableWidget.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            event_datetime = self.tableWidget.item(row, 0).text()
            event = self.tableWidget.item(row, 1).text()
            if event_datetime == "Pause":
                return None, None
            return event_datetime, event
        return None, None

    @property
    def selected_date(self):
        return self.date_edit.date().toPyDate()
