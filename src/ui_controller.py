from PyQt5.QtWidgets import QMessageBox, QInputDialog, QTableWidgetItem, QFileDialog, QDialog, QTableWidget

from src.filepath import HOME_PATH
from src.icons import get_app_icon
from src import __version__
from src.config_handler import CONFIG_HANDLER, CONFIG_NAMES


class UiController:
    def __init__(self):
        pass

    def show_message(self, message: str):
        """The default messagebox. Uses a QMessageBox with OK-Button"""
        msgBox = QMessageBox()
        msgBox.setStandardButtons(QMessageBox.Ok)  # type: ignore
        msgBox.setText(str(message))
        msgBox.setWindowIcon(get_app_icon())
        msgBox.setWindowTitle("Information")
        msgBox.show()
        msgBox.exec_()

    def report_choice(self):
        msgBox = QMessageBox()
        msgBox.setText("Would you like the report of the overtime (0 if none or the amount) or of the regular hours?")
        msgBox.setWindowTitle("Report Generation")
        msgBox.setWindowIcon(get_app_icon())
        overtime_button = msgBox.addButton("Overtime", QMessageBox.YesRole)  # type: ignore
        time_button = msgBox.addButton("Time", QMessageBox.NoRole)  # type: ignore
        msgBox.addButton("Cancel", QMessageBox.RejectRole)  # type: ignore

        msgBox.exec_()
        if msgBox.clickedButton() == overtime_button:
            return True
        elif msgBox.clickedButton() == time_button:
            return False
        return None

    def user_okay(self, text: str):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setWindowTitle("Confirmation required")
        msgBox.setWindowIcon(get_app_icon())
        yes_button = msgBox.addButton("Yes", QMessageBox.YesRole)  # type: ignore
        msgBox.addButton("No", QMessageBox.NoRole)  # type: ignore
        msgBox.exec_()
        if msgBox.clickedButton() == yes_button:
            return True
        return False

    def display_about(self):
        message = f"Version: {__version__}. This App was made with Python and Qt by Andre Wohnsland. Check https://github.com/AndreWohnsland/TimeTracker for more information."
        self.show_message(message)

    def get_text(self, attribute, parent):
        text, ok = QInputDialog.getText(parent, "Getting data for config", f"Enter your {attribute}:")
        return (text, ok)

    def get_folder(self, current_path: str, parent=None):
        if not current_path:
            current_path = str(HOME_PATH)

        dialog = QFileDialog(parent)
        dialog.setFileMode(QFileDialog.DirectoryOnly)  # type: ignore
        dialog.setDirectory(current_path)

        if dialog.exec_() == QDialog.Accepted:  # type: ignore
            path = dialog.selectedFiles()[0]  # returns a list
            return path
        else:
            return ""

    def fill_table(self, table: QTableWidget, entry):
        rowPosition = table.rowCount()
        table.insertRow(rowPosition)
        for i, data in enumerate(entry):
            table.setItem(rowPosition, i, QTableWidgetItem(data))

    def clear_table(self, table: QTableWidget):
        while table.rowCount() > 0:
            table.removeRow(0)

    def set_header_names(self, table: QTableWidget, name1: str, name2: str):
        table.horizontalHeaderItem(0).setText(name1)
        table.horizontalHeaderItem(1).setText(name2)

    def get_user_data(self, parent):
        needed_keys: list[CONFIG_NAMES] = ["name"]
        # todo adjust to new class logic
        for data in needed_keys:
            text, ok = self.get_text(data, parent)
            if not ok:
                return
            if text != "":
                CONFIG_HANDLER.set_config_value(data, text, write=False)
        CONFIG_HANDLER.write_config_file()

    def get_save_folder(self):
        user_path = CONFIG_HANDLER.config.save_path
        returned_path = self.get_folder(user_path)
        if returned_path:
            CONFIG_HANDLER.config.save_path = returned_path
        CONFIG_HANDLER.write_config_file()


UI_CONTROLLER = UiController()
