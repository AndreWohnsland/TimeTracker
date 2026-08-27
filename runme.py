from src.utils import prepare_data_location_and_files, run_db_migrations, setup_logging

# Prepare the data location and files. meeds to be done before importing the main application
setup_logging()
prepare_data_location_and_files()
run_db_migrations()

import logging
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from src.ui_mainwindow import MainWindow
from src.utils import sync_theme

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        # Qt 6.8+ hides menu icons on macOS by default (Apple HIG), we want them back
        app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
        w = MainWindow()
        # still keep the app running, even if the main window is closed (we use tray for the app)
        QApplication.setQuitOnLastWindowClosed(False)
        sync_theme()
        w.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.exception(e)
        raise
