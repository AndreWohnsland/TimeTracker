from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
import holidays

from ui import Ui_ConfigWindow
from src.icons import get_app_icon
from src.config_handler import CONFIG_HANDLER

if TYPE_CHECKING:
    from src.ui_mainwindow import MainWindow


class ConfigWindow(QWidget, Ui_ConfigWindow):
    def __init__(self, main_window: MainWindow):
        """Init. Many of the button and List connects are in pass_setup."""
        super().__init__()
        self.main_window = main_window
        self.setupUi(self)
        self.setWindowIcon(get_app_icon())
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)  # type: ignore
        self.setAttribute(Qt.WA_DeleteOnClose)  # type: ignore
        self.country_list = holidays.list_supported_countries()
        self._update_country_list()

    def _update_country_list(self, country=None):
        # first choose which country to use, if selection, use this,
        # otherwise use the config country
        if country is None and self.input_country.currentText() != "":
            country = self.input_country.currentText()
        elif country is None:
            country = CONFIG_HANDLER.config.country
        subdiv_list = self.country_list.get(country, [])
        country_list = list(self.country_list.keys())
        # if there is a filter, apply it
        country_filter = self.filter_country.text()
        if country_filter:
            country_list = [c for c in country_list if country_filter.lower() in c.lower()]
        self.input_country.clear()
        self.input_country.addItems(country_list)
        self.input_country.setCurrentText(country)

        # clear filter, choose new subdiv
        self.filter_country.clear()
        self.input_subdiv.clear()
        self.input_subdiv.addItems(subdiv_list)
        self.input_subdiv.setCurrentText(CONFIG_HANDLER.config.subdiv or "")
        self.filter_subdiv.clear()
