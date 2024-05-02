from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
import calendar

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
import pandas as pd

from src.config_handler import CONFIG_HANDLER
from src.filepath import REPORTS_PATH
from src.ui_controller import UI_CONTROLLER
from ui import Ui_PlotWindow
from src.datastore import store

if TYPE_CHECKING:
    from src.ui_mainwindow import MainWindow


class GraphWindow(QWidget, Ui_PlotWindow):
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.setWindowIcon(self.main_window.clock_icon)
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint  # type: ignore
        )
        plt.rcParams["date.autoformatter.day"] = "%d"
        # plt.rcParams["date.autoformatter.month"] = "%b"
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        # a figure instance to plot on
        self.figure = plt.figure(figsize=(13, 8), dpi=128, tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.container.addWidget(self.canvas)

        self.save_button.clicked.connect(self.save_plot)
        self.radio_month.toggled.connect(self.plot)
        self.radio_year.toggled.connect(self.plot)
        self.date_edit.dateChanged.connect(self.update_date)

        # workaround to prevent the date change to trigger the plot
        self.programmatic_change = False
        self.date_edit.setDate(store.current_date)

    def update_date(self):
        """Update the date and plot the new data."""
        if self.programmatic_change:
            return
        store.current_date = self.date_edit.date().toPyDate()
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
        plot_df.plot.bar(stacked=True, ax=ax, width=0.8, color=["#2693ff", "#ff4e26", "#25cf5e"])
        ax.legend(fancybox=True, framealpha=0.7)

        ax.axhline(needed_hours, color="k", ls="--", lw=1)
        ax.xaxis.get_label().set_visible(False)

        if self.radio_month.isChecked():
            tick_labels = [day.strftime("%d") for day in df.index]
            # shift the xticks to the middle of the bars
            ax.set_xticks([x + 0.3 for x in range(len(tick_labels))], tick_labels, rotation="vertical")
        else:
            tick_labels = [month.strftime("%b") for month in df.index]
            ax.set_xticklabels(tick_labels, rotation="horizontal")

        # hide the x ticks
        ax.tick_params(axis="x", which="both", bottom=False, top=False)
        if self.radio_month.isChecked():
            ax.set_title(f"Working time for {store.current_date.strftime('%B %Y')}")
        else:
            ax.set_title(f"Working time for {store.current_date.year}")
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
            data = {"work_time": [0] * day_in_month, "pause": [0] * day_in_month}
            return pd.DataFrame(data, index=days)
        months = pd.date_range(start=date.replace(month=1, day=1), periods=12, freq="M")
        data = {"work_time": [0] * 12, "pause": [0] * 12}
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

        self.figure.savefig(save_file_name)
        UI_CONTROLLER.show_message(f"Plot saved to {save_file_name}")
