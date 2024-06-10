from src.utils import prepare_data_location_and_files, setup_logging

setup_logging()
prepare_data_location_and_files()

import logging
import sys

from PyQt5.QtWidgets import QApplication

from src.ui_mainwindow import MainWindow
from src.utils import get_additional_run_args, sync_theme

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv + get_additional_run_args())
        w = MainWindow()
        # in case of active style change, also change theme, need to sync at start
        app.paletteChanged.connect(sync_theme)
        # still keep the app running, even if the main window is closed (we use tray for the app)
        QApplication.setQuitOnLastWindowClosed(False)
        sync_theme()
        w.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.exception(e)
        raise
