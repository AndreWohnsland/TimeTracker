from __future__ import annotations
from typing import TYPE_CHECKING
import datetime

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QDateTime

from ui.data_widget import Ui_DataWidget
from src.database_controller import DB_CONTROLLER
from src.ui_controller import UI_CONTROLLER as UIC
from src.icons import get_app_icon
from src.datastore import store
from src.data_exporter import EXPORTER

if TYPE_CHECKING:
    from src.ui_mainwindow import MainWindow


class DataWindow(QWidget, Ui_DataWidget):
    def __init__(self, main_window: MainWindow):
        """Init. Many of the button and List connects are in pass_setup."""
        super(DataWindow, self).__init__()
        self.main_window = main_window
        self.setupUi(self)
        self.setWindowIcon(get_app_icon())
        self.connect_buttons()
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)  # type: ignore
        self.delete_button = None
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.handle_delete_button()

    def connect_buttons(self):
        self.date_edit.dateChanged.connect(lambda: self.on_date_change())
        self.export_button.clicked.connect(lambda: self.export_data())
        self.switch_button.clicked.connect(lambda: self.switch_data_view())
        self.plot_button.clicked.connect(lambda: self.main_window.show_plot_window())
        self.delete_event_button.clicked.connect(self.delete_selected_event)

    def update_data(self):
        self.on_date_change()

    def on_date_change(self):
        UIC.clear_table(self.tableWidget)
        selected_date = self.get_event_date()
        store.update_data(selected_date)
        if self.view_day:
            self.fill_daily_data()
        else:
            self.fill_monthly_data()

    def export_data(self):
        report_date = self.get_event_date()
        overtime_report = UIC.report_choice()
        if overtime_report is None:
            return
        successful, message = EXPORTER.export_data(store.df, report_date, overtime_report)
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

    def get_event_date(self):
        qt_date = self.date_edit.date()
        return datetime.date(qt_date.year(), qt_date.month(), qt_date.day())
