from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *

from ui.datawidget import Ui_DataWidget


class DataWindow(QWidget, Ui_DataWidget):
    def __init__(self, main_window, button_controler):
        """ Init. Many of the button and List connects are in pass_setup. """
        super(DataWindow, self).__init__()
        self.main_window = main_window
        self.setupUi(self)
        self.button_controler = button_controler
        self.connect_buttons()
        self.main_window.set_icon(self)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.delete_button = None

    def connect_buttons(self):
        self.date_edit.dateChanged.connect(lambda: self.button_controler.on_date_change())
        self.export_button.clicked.connect(lambda: self.button_controler.export_data())
        self.switch_button.clicked.connect(lambda: self.button_controler.switch_dataview())
