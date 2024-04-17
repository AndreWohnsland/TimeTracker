from typing import Callable
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QAction, QDateTimeEdit, QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QDateTime, QSize

from src.utils import get_app_icon
from ui.mainwindow import Ui_MainWindow
from src.button_controller import ButtonController
from src.database_controller import DatabaseController
from src.icons import get_preset_icons


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        """Init. Many of the button and List connects are in pass_setup."""
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)  # type: ignore
        self.clock_icon = get_app_icon()
        self.set_objects()
        self.connect_buttons()
        self.connect_actions()
        self.set_tray()
        self.set_icon()
        self.initialize_optional_elements()

    def connect_buttons(self):
        self.start_button.clicked.connect(self.button_controller.add_start)
        self.stop_button.clicked.connect(self.button_controller.add_stop)
        self.pause_button.clicked.connect(self.button_controller.add_pause)

    def set_icon(self):
        self.setWindowIcon(self.clock_icon)

    def set_tray(self):
        # Need to check if tray icon already exists
        existing_tray_icons = QApplication.instance().topLevelWidgets()  # type: ignore
        tray_icon_exists = any(isinstance(widget, QSystemTrayIcon) for widget in existing_tray_icons)
        if tray_icon_exists:
            return

        # Set the tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.clock_icon))
        self.tray_icon.setToolTip("Time Tracker")
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.handle_tray_click)
        tray_menu = QMenu(self)
        self.tray_icon.setContextMenu(tray_menu)

        icons = get_preset_icons()
        # Exit
        self.add_tray_menu_option(tray_menu, icons.exit, "Exit", self.close_app)
        # graph
        self.add_tray_menu_option(
            tray_menu,
            icons.stats,
            "Plot",
            lambda: self.button_controller.ui_controller.show_message("Not implemented yet"),
        )
        # table
        self.add_tray_menu_option(tray_menu, icons.table, "Data", self.button_controller.show_events)
        # Stop
        self.add_tray_menu_option(tray_menu, icons.stop, "Stop", self.button_controller.add_stop)
        # Start
        self.add_tray_menu_option(tray_menu, icons.start, "Start", self.button_controller.add_start)

    def add_tray_menu_option(self, tray_menu: QMenu, icon: QIcon, text: str, action: Callable[[], None]):
        start_action = QAction(icon, text, self)
        start_action.triggered.connect(action)
        tray_menu.addAction(start_action)

    def close_app(self):
        if self.button_controller.ui_controller.user_okay("Do you want to quit the application?"):
            QApplication.quit()

    def restore_window(self):
        # Show window when tray icon is clicked
        self.showNormal()
        self.activateWindow()

    def handle_tray_click(self, reason):
        if reason == QSystemTrayIcon.DoubleClick or reason == QSystemTrayIcon.Trigger:  # type: ignore
            self.restore_window()

    def set_objects(self):
        self.database_controller = DatabaseController()
        self.button_controller = ButtonController(self.database_controller, self)

    def connect_actions(self):
        self.action_configuration.triggered.connect(lambda: self.button_controller.get_user_data())
        self.action_report.triggered.connect(lambda: self.button_controller.show_events())
        self.action_save_folder.triggered.connect(lambda: self.button_controller.get_save_folder())
        self.action_update.triggered.connect(lambda: self.button_controller.get_updates())
        self.action_past_entry.triggered.connect(lambda: self.add_ui_elements())
        self.action_about.triggered.connect(lambda: self.button_controller.display_about())

    def initialize_optional_elements(self):
        self.back_button = None
        self.past_datetime_edit = None

    def add_ui_elements(self):
        if self.past_datetime_edit is not None:
            return
        self.button_controller.past_time = True
        self.generate_datetime_edit()
        self.generate_back_button()
        self.resize_mainwindow(0, 80)

    def generate_datetime_edit(self):
        self.past_datetime_edit = QDateTimeEdit(self)
        font = QFont()
        font.setPointSize(12)
        self.past_datetime_edit.setFont(font)
        self.past_datetime_edit.setCurrentSection(QDateTimeEdit.DaySection)
        self.past_datetime_edit.setCalendarPopup(True)
        self.past_datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.past_datetime_edit.setMinimumSize(QSize(0, 50))
        self.past_datetime_edit.setMaximumSize(QSize(200, 100))
        self.past_datetime_edit.setObjectName("past_datetime_edit")
        self.verticalLayout.addWidget(self.past_datetime_edit)

    def generate_back_button(self):
        self.back_button = QPushButton(self)
        self.back_button.setMinimumSize(QSize(0, 50))
        self.back_button.setMaximumSize(QSize(200, 100))
        font = QFont()
        font.setPointSize(18)
        self.back_button.setFont(font)
        self.back_button.setObjectName("back_button")
        self.back_button.setText("Back")
        self.back_button.clicked.connect(lambda: self.remove_ui_elements())
        self.verticalLayout_2.addWidget(self.back_button)

    def remove_ui_elements(self):
        if self.past_datetime_edit is None:
            return
        self.button_controller.past_time = False
        self.verticalLayout.removeWidget(self.past_datetime_edit)
        self.past_datetime_edit.deleteLater()
        self.past_datetime_edit = None

        self.verticalLayout_2.removeWidget(self.back_button)
        self.back_button.deleteLater()  # type: ignore
        self.back_button = None
        self.resize_mainwindow(0, -80)

    def resize_mainwindow(self, width: int, height: int):
        h = self.geometry().height()
        w = self.geometry().width()
        self.resize(w + width, h + height)
