from __future__ import annotations
import datetime
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QListWidgetItem, QLabel, QSizePolicy
from PyQt5.QtCore import Qt

from ui import Ui_VacationWindow
from src.icons import get_app_icon, get_preset_icons
from src.database_controller import DB_CONTROLLER
from src.ui_controller import UI_CONTROLLER

if TYPE_CHECKING:
    from src.ui_mainwindow import MainWindow


class VacationWindow(QWidget, Ui_VacationWindow):
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window
        self.setupUi(self)
        self.setWindowIcon(get_app_icon())
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)  # type: ignore
        self.setAttribute(Qt.WA_DeleteOnClose)  # type: ignore

        # setting dates to today
        today = datetime.date.today()
        self.year_select.setValue(today.year)
        self.date_edit.setDate(today)

        # update values, then connect signals
        self._generate_vacation_list()
        self.save_button.clicked.connect(self._add_vacation)
        self.year_select.valueChanged.connect(self._generate_vacation_list)

    def _generate_vacation_list(self):
        """Read all the database entries and generate the list of vacation days"""
        self.list_widget_dates.clear()
        dates = DB_CONTROLLER.get_vacation_days(self.year)
        self.label_list_view.setText(f"Vacation Days in {self.year}:")
        # sort the dates, so the newest is on top
        dates.sort(reverse=True)
        for date in dates:
            self.add_date_item(date)

    def add_date_item(self, date: datetime.date):
        # choose the correct suffix for the day
        if 4 <= date.day <= 20 or 24 <= date.day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][date.day % 10 - 1]
        item = QListWidgetItem()
        item_widget = QWidget()
        line_text = QLabel(f"{date.strftime('%m-%d | %B')} {date.day}{suffix}")
        line_text.setStyleSheet("font-size: 16px;")
        delete_button = QPushButton("")
        delete_button.clicked.connect(lambda: self.delete_date_item(item, date))
        delete_button.setIcon(get_preset_icons().delete_inverted)
        # set red border and add a padding top bottom of 5px
        delete_button.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 5px; background-color: red;")
        # always shrink the button to the minimum size
        delete_button.setMaximumWidth(30)
        delete_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)  # type: ignore
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        item_layout.addWidget(line_text)
        item_layout.addWidget(delete_button)
        item_widget.setLayout(item_layout)
        item.setSizeHint(item_widget.sizeHint())
        self.list_widget_dates.addItem(item)
        self.list_widget_dates.setItemWidget(item, item_widget)

    def delete_date_item(self, item: QListWidgetItem, date: datetime.date):
        if not UI_CONTROLLER.user_okay(f"Do you want to remove the vacation on {date}?"):
            return
        DB_CONTROLLER.remove_vacation(date)
        row = self.list_widget_dates.row(item)
        self.list_widget_dates.takeItem(row)

    def _remove_vacation_entry(self, date: datetime.date, container: QHBoxLayout):
        """Remove the vacation entry from the list and the database"""
        DB_CONTROLLER.remove_vacation(date)
        UI_CONTROLLER.delete_items_of_layout(container)
        container.deleteLater()

    def _add_vacation(self):
        """Adds the current date as vacation day"""
        selected_date = self.date_edit.date().toPyDate()
        DB_CONTROLLER.add_vacation(selected_date)
        self._generate_vacation_list()

    @property
    def year(self) -> int:
        return self.year_select.value()
