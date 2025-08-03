from __future__ import annotations

import calendar
import datetime
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FuncFormatter
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


@dataclass
class PlotColors:
    red: str
    green: str
    blue: str


class DataWindow(QWidget, Ui_DataWindow):
    def __init__(self, main_window: MainWindow) -> None:
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
        self.plot_colors = PlotColors(
            red="#ff4e26",
            green="#25cf5e",
            blue="#2693ff",
        )

    @property
    def view_day(self) -> bool:
        return self.switch_button.isChecked()

    @property
    def selected_date(self) -> datetime.date:
        return self.date_edit.date().toPyDate()

    @property
    def plot_month(self) -> bool:
        return self.radio_month.isChecked()

    def set_plot_parameters(self) -> None:
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
        plt.set_loglevel("WARNING")

    def update_date(self) -> None:
        """Update the date and plot the new data."""
        prev_date = self.prev_date
        self.prev_date = self.date_edit.date()
        if self.programmatic_change:
            return
        store.current_date = self.selected_date
        self.update_table_data()
        # do not change plot on day change
        month_changed = prev_date.month() != self.date_edit.date().month()
        year_changed = prev_date.year() != self.date_edit.date().year()
        if (month_changed and self.plot_month) or year_changed:
            self.plot()

    def _only_change_date(self, set_date: QDate | datetime.date) -> None:
        """Change date while suppressing the on change event of the date edit."""
        self.programmatic_change = True
        self.date_edit.setDate(set_date)
        self.programmatic_change = False

    def plot(self) -> None:
        # clears the old values and then adds a subplot to insert all the data
        self.figure.clear()
        # Top: small plot with only the overtime
        # Bottom: main plot with the data
        gs = GridSpec(2, 1, height_ratios=[1, 4])
        ax1 = self.figure.add_subplot(gs[1])
        ax2 = self.figure.add_subplot(gs[0], sharex=ax1)

        # update the store before plotting
        store.update_data(self.selected_date)
        # get the store date -> this is needed to show the correct month in the dropdown
        # if the user did not change it there before
        self._only_change_date(store.current_date)

        df = store.df.copy() if self.plot_month else store.get_year_data(store.current_date.year)
        plot_df = self.adjust_df_for_plot(df)
        self._plot_work_time(ax1, plot_df)
        self._plot_overtime(ax2, plot_df)

        if self.plot_month:
            title = f"Working time for {store.current_date.strftime('%B %Y')}"
        else:
            title = f"Working time for {store.current_date.year}"
        sum_overtime = plot_df.overtime.sum()
        sum_work = plot_df.work.sum()
        title += f" | Work: {sum_work:.0f} h | Overtime: {sum_overtime:.0f} h"
        self.figure.suptitle(title, weight="bold", fontsize=15)
        # self.figure.autofmt_xdate(rotation=90)
        self.canvas.draw()

    def _plot_work_time(self, ax: Axes, df: pd.DataFrame) -> None:
        sns.barplot(
            data=df,
            x=df.index,
            y="work",
            color=self.plot_colors.blue,
            ax=ax,
            zorder=2,
            width=0.8,
        )

        ax.yaxis.grid(True, lw=1, ls=":", color=self.text_color, alpha=0.2, zorder=1)
        ax.xaxis.get_label().set_visible(False)

        if self.plot_month:
            tick_labels = [day.strftime("%a %d") for day in df.index]
            rotation = "vertical"
        else:
            tick_labels = [month.strftime("%b") for month in df.index]
            rotation = "horizontal"
        ax.set_xticks(range(len(tick_labels)))
        ax.set_xticklabels(tick_labels, rotation=rotation)
        ax.tick_params(axis="x", which="both", bottom=False, top=False)
        ax.set_ylabel("Work Time (h)")

        # Add numbers above the bars
        max_value = df.work.max()
        for i, (_, row) in enumerate(df.iterrows()):
            total_time = row["work"]
            if total_time <= 0.0:
                continue
            position = (i, total_time + max_value * 0.012)
            ax.annotate(
                f"{total_time:.1f}",
                position,
                ha="center",
                va="bottom",
                fontsize=8,
                weight="bold",
                bbox={
                    "boxstyle": "round,pad=0.0",
                    "fc": self.background_color,
                    "ec": self.background_color,
                    "alpha": 0.8,
                },
                zorder=5,
            )
            target = row["target_time"]
            bar_width = 0.9
            x_start = i - bar_width / 2
            x_end = i + bar_width / 2
            ax.hlines(target, x_start, x_end, color=self.text_color, lw=1, ls="--", zorder=3)

    def _plot_overtime(self, ax: Axes, df: pd.DataFrame) -> None:
        sns.barplot(
            data=df,
            x=df.index,
            y="overtime",
            hue="color",
            palette={"positive": self.plot_colors.green, "negative": self.plot_colors.red},
            ax=ax,
            zorder=2,
            legend=False,
        )

        add_max = df.overtime.max() * 0.01
        # Min value needs more shift because of other va behavior
        add_min = df.overtime.min() * 0.05
        for i, (_, row) in enumerate(df.iterrows()):
            overtime = row["overtime"]
            if overtime == 0.0:
                continue
            add_value = add_max if overtime > 0 else add_min
            va = "bottom" if overtime >= 0 else "top"
            position = (i, overtime + add_value)
            ax.annotate(f"{abs(overtime):.1f}", position, ha="center", va=va, fontsize=6, weight="bold", zorder=5)

        ax.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)
        ax.xaxis.get_label().set_visible(False)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x)}"))
        ax.spines["bottom"].set_position(("data", 0))
        ax.set_ylabel("Overtime (h)")

    def adjust_df_for_plot(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adjust the dataframe for plotting."""
        if df.empty:
            df = self._create_dummy_df()
        df["color"] = df["overtime"].apply(lambda x: "positive" if x >= 0 else "negative")
        to_keep = ["work", "overtime", "color", "target_time"]
        return df[to_keep]

    def _create_dummy_df(self) -> pd.DataFrame:
        """Create a dummy dataframe if no data is available."""
        date = store.current_date
        if self.plot_month:
            data_points = calendar.monthrange(date.year, date.month)[1]
            index = pd.date_range(start=date.replace(day=1), periods=data_points, freq="D")
        else:
            data_points = 12
            index = pd.date_range(start=date.replace(month=1, day=1), periods=data_points, freq="ME")
        zeros = [0] * data_points
        data = {"work": zeros, "pause": zeros, "overtime": zeros, "target_time": zeros}
        return pd.DataFrame(data, index=index)

    def save_plot(self) -> None:
        """Save the plot as png."""
        folder = Path(REPORTS_PATH)
        # only use the save path if it is set
        if CONFIG_HANDLER.config.save_path:
            folder = Path(CONFIG_HANDLER.config.save_path)
        # Generate Month or Year name for the file
        if self.plot_month:
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

        self.figure.savefig(save_file_name, transparent=False, dpi=300)
        UIC.show_message(f"Plot saved to {save_file_name}")

    # Data Things
    def update_table_data(self) -> None:
        UIC.clear_table(self.tableWidget)
        store.update_data(self.selected_date)
        if self.view_day:
            self.fill_daily_data()
        else:
            self.fill_monthly_data()
        prefix = "+" if store.total_overtime >= 0 else ""
        current_year = self.selected_date.year
        overtime_year = store.overtime_by_year.get(current_year, 0)
        prefix_year = "+" if overtime_year >= 0 else ""
        self.label_overtime.setText(
            f"Overtime: {prefix}{store.total_overtime:.0f} h ({current_year}: {prefix_year}{overtime_year:.0f} h) "
        )

    def export_data(self) -> None:
        overtime_report = UIC.report_choice()
        if overtime_report is None:
            return
        message = EXPORTER.export_data(store.df, self.selected_date, overtime_report)
        UIC.show_message(message)

    def switch_data_view(self) -> None:
        if self.view_day:
            self.fill_daily_data()
            self.switch_button.setText("Day")
            self.delete_event_button.show()
            return
        self.fill_monthly_data()
        self.switch_button.setText("Month")
        self.delete_event_button.hide()

    def fill_monthly_data(self) -> None:
        UIC.clear_table(self.tableWidget)
        UIC.set_header_names(self.tableWidget, "Date", "Time (h)")
        for index, entry in store.df.iterrows():
            needed_data = [index.strftime("%d/%m/%Y"), str(round(entry["work"], 1))]  # type: ignore
            UIC.fill_table(self.tableWidget, needed_data)

    def fill_daily_data(self) -> None:
        UIC.clear_table(self.tableWidget)
        UIC.set_header_names(self.tableWidget, "Date / Type", "Event / Pause (min)")
        for entry in store.daily_data:
            UIC.fill_table(self.tableWidget, entry)

    def delete_selected_event(self) -> None:
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

    def change_month(self, delta: int) -> None:
        """Change the month to the given month."""
        current_date = self.date_edit.date()
        new_date = current_date.addMonths(delta)
        self.date_edit.setDate(new_date)

    def on_item_click(self, item: QTableWidgetItem) -> None:
        """Set the date to the selected date in the table."""
        # only continue if this is not the day view
        if self.view_day:
            return
        row = item.row()
        date_item = self.tableWidget.item(row, 0)
        date = date_item.text()
        date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        self.date_edit.setDate(date)
