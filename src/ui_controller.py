from PyQt6.QtWidgets import QDialog, QFileDialog, QInputDialog, QLayout, QMessageBox, QTableWidget, QTableWidgetItem

from src import __version__
from src.config_handler import CONFIG_HANDLER
from src.filepath import HOME_PATH
from src.icons import get_app_icon


class UiController:
    def __init__(self):
        """Class to abstract the UI from the main logic."""

    def show_message(self, message: str):
        """Prompt default messagebox, use a QMessageBox with OK-Button."""
        message_box = QMessageBox()
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.setText(str(message))
        message_box.setWindowIcon(get_app_icon())
        message_box.setWindowTitle("Information")
        message_box.show()
        message_box.exec()

    def report_choice(self):
        message_box = QMessageBox()
        message_box.setText(
            "Would you like the report of the overtime (0 if none or the amount) or of the regular hours?"
        )
        message_box.setWindowTitle("Report Generation")
        message_box.setWindowIcon(get_app_icon())
        overtime_button = message_box.addButton("Overtime", QMessageBox.ButtonRole.YesRole)
        time_button = message_box.addButton("Time", QMessageBox.ButtonRole.NoRole)
        message_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        message_box.exec()
        if message_box.clickedButton() == overtime_button:
            return True
        if message_box.clickedButton() == time_button:
            return False
        return None

    def user_okay(self, text: str):
        message_box = QMessageBox()
        message_box.setText(text)
        message_box.setWindowTitle("Confirmation required")
        message_box.setWindowIcon(get_app_icon())
        yes_button = message_box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        message_box.addButton("No", QMessageBox.ButtonRole.NoRole)
        message_box.exec()
        if message_box.clickedButton() == yes_button:
            return True
        return False

    def display_about(self):
        message = (
            f"Version: {__version__}. This App was made with Python and Qt by Andre Wohnsland. "
            "Check https://github.com/AndreWohnsland/TimeTracker for more information."
        )
        self.show_message(message)

    def get_text(self, attribute, parent):
        text, ok = QInputDialog.getText(parent, "Getting data for config", f"Enter your {attribute}:")
        return (text, ok)

    def get_folder(self, current_path: str, parent=None):
        if not current_path:
            current_path = str(HOME_PATH)

        dialog = QFileDialog(parent)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setDirectory(current_path)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selectedFiles()[0]
        return ""

    def fill_table(self, table: QTableWidget, entry):
        row_position = table.rowCount()
        table.insertRow(row_position)
        for i, data in enumerate(entry):
            table.setItem(row_position, i, QTableWidgetItem(data))

    def clear_table(self, table: QTableWidget):
        while table.rowCount() > 0:
            table.removeRow(0)

    def set_header_names(self, table: QTableWidget, name1: str, name2: str):
        header_1 = table.horizontalHeaderItem(0)
        if header_1 is not None:
            header_1.setText(name1)
        header_2 = table.horizontalHeaderItem(1)
        if header_2 is not None:
            header_2.setText(name2)

    def get_save_folder(self):
        user_path = CONFIG_HANDLER.config.save_path
        returned_path = self.get_folder(user_path)
        if returned_path:
            CONFIG_HANDLER.config.save_path = returned_path
        CONFIG_HANDLER.write_config_file()

    def delete_items_of_layout(self, layout: QLayout | None = None):
        """Recursively delete all items of the given layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item is None:
                    continue
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)  # type: ignore
                else:
                    self.delete_items_of_layout(item.layout())


UI_CONTROLLER = UiController()
