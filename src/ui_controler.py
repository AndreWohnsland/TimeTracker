from PyQt5.QtWidgets import QMessageBox, QInputDialog, QWidget, QTableWidgetItem, QFileDialog, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime
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
        overtime_button = msgBox.addButton("Overtime", QMessageBox.YesRole)
        time_button = msgBox.addButton("Time", QMessageBox.NoRole)
        cancelBtn = msgBox.addButton("Cancel", QMessageBox.RejectRole)

        msgBox.exec_()

        if msgBox.clickedButton() == overtime_button:
            return True
        elif msgBox.clickedButton() == time_button:
            return False
        elif msgBox.clickedButton() == cancelBtn:
            return None

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
