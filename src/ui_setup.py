from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
import os

from ui.mainwindow import Ui_MainWindow
from src.button_controler import ButtonControler
from src.database_controler import DatabaseControler


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        """ Init. Many of the button and List connects are in pass_setup. """
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.set_objects()
        self.connect_buttons()
        self.connect_actions()
        self.set_icon(self)

    def connect_buttons(self):
        self.start_button.clicked.connect(lambda: self.button_controler.add_start())
        self.stop_button.clicked.connect(lambda: self.button_controler.add_stop())
        self.pause_button.clicked.connect(lambda: self.button_controler.add_pause())

    def set_icon(self, window):
        dirpath = os.path.dirname(__file__)
        self.clock_picture = os.path.join(dirpath, "..", "ui", "clock.png")
        window.setWindowIcon(QIcon(self.clock_picture))

    def set_objects(self):
        self.database_controler = DatabaseControler()
        self.button_controler = ButtonControler(self.database_controler, self)

    def connect_actions(self):
        self.action_configuration.triggered.connect(lambda: self.button_controler.get_user_data())
        self.action_report.triggered.connect(lambda: self.button_controler.show_events())
        # self.action_add_events.triggered.connect()
        self.action_savefolder.triggered.connect(lambda: self.button_controler.get_save_folder())

