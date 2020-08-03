from PyQt5.QtWidgets import QMessageBox, QInputDialog, QWidget, QTableWidgetItem, QFileDialog, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime
from PyQt5 import QtCore, QtGui, QtWidgets

import datetime
from pathlib import Path

from src.ui_datawindow import DataWindow


class UiControler:
    def __init__(self, ui_element):
        self.ui = ui_element
        self.pause_box = ui_element.pause_box

    def get_pause(self):
        return int(self.pause_box.text())

    def set_pause(self, value):
        self.pause_box.setValue(value)

    def show_message(self, message):
        """ The default messagebox. Uses a QMessageBox with OK-Button """
        msgBox = QMessageBox()
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setText(str(message))
        msgBox.setWindowIcon(QIcon(self.ui.clock_picture))
        msgBox.setWindowTitle("Information")
        msgBox.show()
        msgBox.exec_()

    def report_choice(self):
        msgBox = QMessageBox()
        msgBox.setText("Would you like the report of the overtime (0 if none or the amount) or of the regular hours?")
        msgBox.setWindowTitle("Report Generation")
        msgBox.setWindowIcon(QIcon(self.ui.clock_picture))
        overtime_button = msgBox.addButton("Overtime", QMessageBox.YesRole)
        time_button = msgBox.addButton("Time", QMessageBox.NoRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)

        msgBox.exec_()
        if msgBox.clickedButton() == overtime_button:
            return True
        elif msgBox.clickedButton() == time_button:
            return False
        return None

    def user_okay(self, text):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setWindowTitle("Confirmation required")
        msgBox.setWindowIcon(QIcon(self.ui.clock_picture))
        yes_button = msgBox.addButton("Yes", QMessageBox.YesRole)
        msgBox.addButton("No", QMessageBox.NoRole)
        msgBox.exec_()
        if msgBox.clickedButton() == yes_button:
            return True
        return False

    def get_text(self, attribute):
        text, ok = QInputDialog.getText(self.ui, "Getting data for config", f"Enter your {attribute}:")
        return (text, ok)

    def get_folder(self, current_path):
        if not current_path:
            current_path = str(Path.home())

        dialog = QFileDialog(self.ui)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setDirectory(current_path)

        if dialog.exec_() == QDialog.Accepted:
            path = dialog.selectedFiles()[0]  # returns a list
            return path
        else:
            return ""

        # fname = QFileDialog.getOpenFileName(self.ui, "Set folder to save reports", current_path)
        # return fname

    def open_event_window(self, button_controler):
        self.ui.event_window = DataWindow(self.ui, button_controler)
        self.ui.event_window.date_edit.setDateTime(QDateTime.currentDateTime())
        self.ui.event_window.show()

    def fill_table(self, entry):
        rowPosition = self.ui.event_window.tableWidget.rowCount()
        self.ui.event_window.tableWidget.insertRow(rowPosition)
        for i, data in enumerate(entry):
            self.ui.event_window.tableWidget.setItem(rowPosition, i, QTableWidgetItem(data))

    def clear_table(self):
        while self.ui.event_window.tableWidget.rowCount() > 0:
            self.ui.event_window.tableWidget.removeRow(0)

    def get_event_date(self):
        qt_date = self.ui.event_window.date_edit.date()
        return datetime.date(qt_date.year(), qt_date.month(), qt_date.day())

    def get_past_date(self):
        qt_object = self.ui.past_datetime_edit.dateTime()
        qt_date = qt_object.date()
        return datetime.date(qt_date.year(), qt_date.month(), qt_date.day())

    def get_past_datetime(self):
        qt_object = self.ui.past_datetime_edit.dateTime()
        qt_date = qt_object.date()
        qt_time = qt_object.time()
        return datetime.datetime(qt_date.year(), qt_date.month(), qt_date.day(), qt_time.hour(), qt_time.minute(), qt_time.second())

    def view_day(self):
        if self.ui.event_window.switch_button.isChecked():
            return True
        return False

    def set_date_toggle(self):
        if self.view_day():
            self.ui.event_window.switch_button.setText("View: Day")
        else:
            self.ui.event_window.switch_button.setText("View: Month")

    def set_monthly_header(self):
        self.set_header_names("Date", "Worktime (h)")

    def set_daily_header(self):
        self.set_header_names("Datetime / Type", "Event / Pausetime (min)")

    def set_header_names(self, name1, name2):
        item = self.ui.event_window.tableWidget.horizontalHeaderItem(0)
        item.setText(name1)
        item = self.ui.event_window.tableWidget.horizontalHeaderItem(1)
        item.setText(name2)

    def handle_delete_button(self, trigger_function):
        if self.view_day():
            self.create_delete_button(trigger_function)
        else:
            self.remove_delete_button()

    def create_delete_button(self, trigger_function):
        delete_button = QtWidgets.QPushButton(self.ui.event_window)
        delete_button.setMinimumSize(QtCore.QSize(0, 50))
        delete_button.setMaximumSize(QtCore.QSize(10000, 100))
        font = QtGui.QFont()
        font.setPointSize(20)
        delete_button.setFont(font)
        delete_button.setObjectName("delete_button")
        delete_button.setText("Delete")
        delete_button.clicked.connect(trigger_function)
        self.ui.event_window.delete_button = delete_button
        self.ui.event_window.verticalLayout.addWidget(self.ui.event_window.delete_button)

    def remove_delete_button(self):
        self.ui.event_window.verticalLayout.removeWidget(self.ui.event_window.delete_button)
        self.ui.event_window.delete_button.deleteLater()
        self.ui.event_window.delete_button = None

    def get_selected_event(self):
        indexes = self.ui.event_window.tableWidget.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            event_datetime = self.ui.event_window.tableWidget.item(row, 0).text()
            event = self.ui.event_window.tableWidget.item(row, 1).text()
            if event_datetime == "Pause":
                return None, None
            return event_datetime, event
        return None, None
