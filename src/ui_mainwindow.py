import datetime
from typing import Callable
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.plot_window import GraphWindow
from src.ui_datawindow import DataWindow
from src.updater import UPDATER
from ui.mainwindow import Ui_MainWindow
from src.database_controller import DB_CONTROLLER
from src.ui_controller import UI_CONTROLLER as UIC
from src.icons import get_preset_icons


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        """Init. Many of the button and List connects are in pass_setup."""
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)  # type: ignore
        self.icons = get_preset_icons()
        self.clock_icon = self.icons.clock
        self.connect_buttons()
        self.connect_actions()
        self.set_tray()
        self.set_icon()
        # set manual here, since it does not recognize the hidden state at init somehow.
        # The default app shows the elements and got the additional height.
        self.past_datetime_edit.hide()
        self.past_datetime_edit.setDateTime(datetime.datetime.now())
        self.back_button.hide()
        self.resize_mainwindow(0, -80)
        self.event_window = DataWindow(self)
        self.plot_window = GraphWindow(self)

    def connect_buttons(self):
        self.start_button.clicked.connect(self.add_start)
        self.stop_button.clicked.connect(self.add_stop)
        self.pause_button.clicked.connect(self.add_pause)
        self.back_button.clicked.connect(self.hide_ui_elements)

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

        # Exit
        self.add_tray_menu_option(tray_menu, self.icons.exit, "Exit", self.close_app)
        # graph
        self.add_tray_menu_option(tray_menu, self.icons.stats, "Plot", self.show_plot_window)
        # table
        self.add_tray_menu_option(tray_menu, self.icons.table, "Data", self.show_data_window)
        # Mainwindow
        self.add_tray_menu_option(tray_menu, self.icons.setting, "Setup", self.restore_window)
        # Stop
        self.add_tray_menu_option(tray_menu, self.icons.stop, "Stop", self.add_stop)
        # Start
        self.add_tray_menu_option(tray_menu, self.icons.start, "Start", self.add_start)

    def add_tray_menu_option(self, tray_menu: QMenu, icon: QIcon, text: str, action: Callable[[], None]):
        start_action = QAction(icon, text, self)
        start_action.triggered.connect(action)
        tray_menu.addAction(start_action)

    def close_app(self):
        if UIC.user_okay("Do you want to quit the application?"):
            QApplication.quit()

    def restore_window(self):
        # Show window when tray icon is clicked
        self.showNormal()
        self.activateWindow()

    def handle_tray_click(self, reason):
        if reason == QSystemTrayIcon.DoubleClick or reason == QSystemTrayIcon.Trigger:  # type: ignore
            self.restore_window()

    def connect_actions(self):
        self.action_configuration.triggered.connect(lambda: UIC.get_user_data(self))
        self.action_report.triggered.connect(self.show_data_window)
        self.action_save_folder.triggered.connect(UIC.get_save_folder)
        self.action_update.triggered.connect(self.get_updates)
        self.action_past_entry.triggered.connect(self.show_ui_elements)
        self.action_about.triggered.connect(UIC.display_about)

    def show_ui_elements(self):
        if self.is_past_time:
            return
        self.past_datetime_edit.show()
        self.back_button.show()
        self.resize_mainwindow(0, 80)

    def hide_ui_elements(self):
        if not self.is_past_time:
            return
        self.past_datetime_edit.hide()
        self.back_button.hide()
        self.resize_mainwindow(0, -80)

    @property
    def is_past_time(self):
        return self.past_datetime_edit.isVisible() and self.back_button.isVisible()

    def resize_mainwindow(self, width: int, height: int):
        h = self.geometry().height()
        w = self.geometry().width()
        self.resize(w + width, h + height)

    def get_pause(self):
        return int(self.pause_box.text())

    def set_pause(self, value: int):
        self.pause_box.setValue(value)

    def add_pause(self):
        pause = self.get_pause()
        entry_date = datetime.date.today()
        if self.is_past_time:
            entry_date = self.get_past_date()
        DB_CONTROLLER.add_pause(pause, entry_date)
        self.set_pause(0)
        UIC.show_message(f"Added pause of {pause} minutes on date {entry_date.strftime('%d-%m-%Y')}")
        self.update_other_windows()

    def get_past_date(self):
        qt_object = self.past_datetime_edit.dateTime()  # type: ignore
        qt_date = qt_object.date()
        return datetime.date(qt_date.year(), qt_date.month(), qt_date.day())

    def get_past_datetime(self):
        qt_object = self.past_datetime_edit.dateTime()  # type: ignore
        qt_date = qt_object.date()
        qt_time = qt_object.time()
        return datetime.datetime(
            qt_date.year(), qt_date.month(), qt_date.day(), qt_time.hour(), qt_time.minute(), qt_time.second()
        )

    def add_event(self, event: str):
        entry_datetime = datetime.datetime.now()
        entry_datetime = entry_datetime.replace(microsecond=0)
        if self.is_past_time:
            entry_datetime = self.get_past_datetime()
        DB_CONTROLLER.add_event(event, entry_datetime)
        UIC.show_message(f"Added event {event} at {entry_datetime.strftime('%d-%m-%Y - %H:%M:%S')}")

    def add_start(self):
        self.add_event("start")
        self.update_other_windows()

    def add_stop(self):
        self.add_event("stop")
        self.update_other_windows()

    def get_updates(self):
        message = "Want to search and get updates? This could take a short time."
        if UIC.user_okay(message):
            print("Try to update ...")
            UPDATER.update()
            print("Done!")

    def show_data_window(self):
        self.event_window.update_data()
        self.event_window.show()

    def show_plot_window(self):
        self.plot_window.plot()
        self.plot_window.show()

    def update_other_windows(self):
        """Updates the view of the other windows if they are open."""
        self.update_data_window()
        self.update_plot_window()

    def update_plot_window(self):
        if self.plot_window.isVisible():
            self.plot_window.plot()

    def update_data_window(self):
        if self.event_window.isVisible():
            self.event_window.update_data()
