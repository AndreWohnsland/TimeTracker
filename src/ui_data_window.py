from __future__ import annotations

import calendar
import datetime
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import QDate, QDateTime, Qt
from PyQt6.QtWidgets import QTableWidgetItem, QWidget

from src.config_handler import CONFIG_HANDLER
from src.data_exporter import EXPORTER
from src.database_controller import DB_CONTROLLER
from src.datastore import store
from src.filepath import REPORTS_PATH
from src.icons import get_app_icon
from src.ui_controller import UI_CONTROLLER as UIC
from src.utils import get_background_color, get_font_color
from ui import Ui_DataWindow

if TYPE_CHECKING:
    from src.ui_mainwindow import MainWindow


logger = logging.getLogger(__name__)


@dataclass
class EventData:
    event_time: str
    event: str


class DataWindow(QWidget, Ui_DataWindow):
    def __init__(self, main_window: MainWindow):
        """Init the Data Window. Connect all the signals and slots."""
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.setWindowIcon(get_app_icon())
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        # setting all the params
        self.date_edit.setDateTime(QDateTime.currentDateTime())
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
        self.button_month_prev.clicked.connect(lambda: self.change_month(-1))
        self.button_month_next.clicked.connect(lambda: self.change_month(1))

        # set the date to the selected date if click on table
        self.tableWidget.itemClicked.connect(self.on_item_click)

        self.delete_button = None
        # workaround to prevent the date change to trigger the plot
        self.programmatic_change = False

    @property
    def view_day(self):
        return self.switch_button.isChecked()

    @property
    def selected_date(self):
        return self.date_edit.date().toPyDate()

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
        plt.rcParams["font.family"] = "DejaVu Sans Mono"

    def update_date(self):
        """Update the date and plot the new data."""
        prev_date = self.prev_date
        self.prev_date = self.date_edit.date()
        month_changed = prev_date.month() != self.date_edit.date().month()
        if self.programmatic_change:
            return
        store.current_date = self.selected_date
        self.update_table_data()
        # only plot on month change (otherwise no plot will change)
        if month_changed:
            self.plot()

    def _only_change_date(self, set_date: QDate | datetime.date):
        """Change date while suppressing the on change event of the date edit."""
        self.programmatic_change = True
        self.date_edit.setDate(set_date)
        self.programmatic_change = False

    def plot(self):
        # clears the old values and then adds a subplot to insert all the data
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # update the store before plotting
        store.update_data(self.selected_date)
        # get the store date -> this is needed to show the correct month in the dropdown
        # if the user did not change it there before
        self._only_change_date(store.current_date)

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
            tick_labels = [day.strftime("%a %d") for day in df.index]
            rotation = "vertical"
            # shift the xticks to the middle of the bars
        else:
            tick_labels = [month.strftime("%b") for month in df.index]
            rotation = "horizontal"
        ax.set_xticklabels(tick_labels, rotation=rotation)

        # hide the x ticks
        ax.tick_params(axis="x", which="both", bottom=False, top=False)

        # Add numbers above the bars
        for i, (_, row) in enumerate(plot_df.iterrows()):
            total_time = sum(row)
            if total_time <= 0.0:
                continue
            # put small offset for the numbers to not overlap with the bar
            position = (i, total_time + 0.01 * needed_hours)
            # last 3% will collide with the line, in this case just put it above the line already
            line_collide = 0.97 * needed_hours <= total_time <= needed_hours
            if line_collide:
                position = (i, 1.01 * needed_hours)
            ax.annotate(f"{total_time:.1f}", position, ha="center", va="bottom", fontsize=8, weight="bold")

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
        to_keep = ["work", "overtime"]
        if CONFIG_HANDLER.config.plot_pause:
            to_keep.append("pause")
        return df[to_keep]

    def _create_dummy_df(self) -> pd.DataFrame:
        """Create a dummy dataframe if no data is available."""
        date = store.current_date
        if self.radio_month.isChecked():
            day_in_month = calendar.monthrange(date.year, date.month)[1]
            # build data for each day of the month, containing only zeros
            days = pd.date_range(start=date.replace(day=1), periods=day_in_month, freq="D")
            data = {"work": [0] * day_in_month, "pause": [0] * day_in_month}
            return pd.DataFrame(data, index=days)
        months = pd.date_range(start=date.replace(month=1, day=1), periods=12, freq="ME")
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
        UIC.show_message(f"Plot saved to {save_file_name}")

    # Data Things
    def update_table_data(self):
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
        message = EXPORTER.export_data(store.df, self.selected_date, overtime_report)
        UIC.show_message(message)

    def switch_data_view(self):
        if self.view_day:
            self.fill_daily_data()
            self.switch_button.setText("Day")
            self.delete_event_button.show()
            return
        self.fill_monthly_data()
        self.switch_button.setText("Month")
        self.delete_event_button.hide()

    def fill_monthly_data(self):
        UIC.clear_table(self.tableWidget)
        UIC.set_header_names(self.tableWidget, "Date", "Time (h)")
        for index, entry in store.df.iterrows():
            needed_data = [index.strftime("%d/%m/%Y"), str(round(entry["work"], 1))]  # type: ignore
            UIC.fill_table(self.tableWidget, needed_data)

    def fill_daily_data(self):
        UIC.clear_table(self.tableWidget)
        UIC.set_header_names(self.tableWidget, "Date / Type", "Event / Pause (min)")
        for entry in store.daily_data:
            UIC.fill_table(self.tableWidget, entry)

    def delete_selected_event(self):
        event_data = self.get_selected_event()
        if event_data is None:
            return
        if UIC.user_okay(f"Do you want to delete event {event_data.event} at: {event_data.event_time}?"):
            logger.info("Delete event %s at: %s", event_data.event, event_data.event_time)
            DB_CONTROLLER.delete_event(event_data.event_time)
            store.update_data(self.selected_date)
            self.update_table_data()
            self.plot()

    def get_selected_event(self) -> EventData | None:
        indexes = self.tableWidget.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            event_datetime = self.tableWidget.item(row, 0).text()
            event = self.tableWidget.item(row, 1).text()
            if event_datetime == "Pause":
                return None
            return EventData(event_datetime, event)
        return None

    def change_month(self, delta: int):
        """Change the month to the given month."""
        current_date = self.date_edit.date()
        new_date = current_date.addMonths(delta)
        self.date_edit.setDate(new_date)

    def on_item_click(self, item: QTableWidgetItem):
        """Set the date to the selected date in the table."""
        # only continue if this is not the day view
        if self.view_day:
            return
        row = item.row()
        date_item = self.tableWidget.item(row, 0)
        date = date_item.text()
        date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        self.date_edit.setDate(date)
