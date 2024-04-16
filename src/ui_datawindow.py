from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from ui.data_widget import Ui_DataWidget

if TYPE_CHECKING:
    from src.button_controller import ButtonController
    from src.ui_mainwindow import MainWindow


class DataWindow(QWidget, Ui_DataWidget):
    def __init__(self, main_window: MainWindow, button_controller: ButtonController):
        """Init. Many of the button and List connects are in pass_setup."""
        super(DataWindow, self).__init__()
        self.main_window = main_window
        self.setupUi(self)
        self.button_controller = button_controller
        self.setWindowIcon(self.main_window.clock_icon)
        self.connect_buttons()
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)  # type: ignore
        self.setWindowModality(Qt.ApplicationModal)  # type: ignore
        self.delete_button = None

    def connect_buttons(self):
        self.date_edit.dateChanged.connect(lambda: self.button_controller.on_date_change())
        self.export_button.clicked.connect(lambda: self.button_controller.export_data())
        self.switch_button.clicked.connect(lambda: self.button_controller.switch_data_view())
        self.plot_button.clicked.connect(lambda: self.button_controller.show_plot())
