from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui, QtWidgets
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
        self.initialize_optional_elements()

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
        self.action_savefolder.triggered.connect(lambda: self.button_controler.get_save_folder())
        self.action_update.triggered.connect(lambda: self.button_controler.get_updates())
        self.action_past_entry.triggered.connect(lambda: self.add_ui_elements())
        self.action_about.triggered.connect(lambda: self.button_controler.display_about())

    def initialize_optional_elements(self):
        self.back_button = None
        self.past_datetime_edit = None

    def add_ui_elements(self):
        if self.past_datetime_edit != None:
            return
        self.button_controler.past_time = True
        self.generate_datetime_edit()
        self.generate_back_button()
        self.resize_mainwindow(0, 80)

    def generate_datetime_edit(self):
        self.past_datetime_edit = QtWidgets.QDateTimeEdit(self)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.past_datetime_edit.setFont(font)
        self.past_datetime_edit.setCurrentSection(QtWidgets.QDateTimeEdit.DaySection)
        self.past_datetime_edit.setCalendarPopup(True)
        self.past_datetime_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.past_datetime_edit.setMinimumSize(QtCore.QSize(0, 50))
        self.past_datetime_edit.setMaximumSize(QtCore.QSize(200, 100))
        self.past_datetime_edit.setObjectName("past_datetime_edit")
        self.verticalLayout.addWidget(self.past_datetime_edit)

    def generate_back_button(self):
        self.back_button = QtWidgets.QPushButton(self)
        self.back_button.setMinimumSize(QtCore.QSize(0, 50))
        self.back_button.setMaximumSize(QtCore.QSize(200, 100))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.back_button.setFont(font)
        self.back_button.setObjectName("back_button")
        self.back_button.setText("Back")
        self.back_button.clicked.connect(lambda: self.remove_ui_elements())
        self.verticalLayout_2.addWidget(self.back_button)

    def remove_ui_elements(self):
        if self.past_datetime_edit == None:
            return
        self.button_controler.past_time = False
        self.verticalLayout.removeWidget(self.past_datetime_edit)
        self.past_datetime_edit.deleteLater()
        self.past_datetime_edit = None

        self.verticalLayout_2.removeWidget(self.back_button)
        self.back_button.deleteLater()
        self.back_button = None
        self.resize_mainwindow(0, -80)

    def resize_mainwindow(self, width, heigt):
        h = self.geometry().height()
        w = self.geometry().width()
        self.resize(w + width, h + heigt)
