from __future__ import annotations

from typing import TYPE_CHECKING

import holidays
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDoubleSpinBox, QRadioButton, QWidget

from src.config_handler import CONFIG_HANDLER
from src.icons import get_app_icon
from ui import Ui_ConfigWindow

if TYPE_CHECKING:
    from src.ui_mainwindow import MainWindow


class ConfigWindow(QWidget, Ui_ConfigWindow):
    def __init__(self, main_window: MainWindow) -> None:
        """Init. Many of the button and List connects are in pass_setup."""
        super().__init__()
        self.main_window = main_window
        self.setupUi(self)
        self.setWindowIcon(get_app_icon())
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.country_list = holidays.list_supported_countries()
        self._update_country_list()
        self.apply_button.clicked.connect(self.apply_config)
        self.filter_subdiv.textEdited.connect(self._apply_subdiv_filter)
        self.filter_country.textEdited.connect(self._apply_country_filter)
        self.input_country.currentTextChanged.connect(self._adjust_subdiv)
        for i in range(7):
            radio: QRadioButton = getattr(self, f"radio_weekday_{i}")
            radio.toggled.connect(lambda checked, day=i: self._handle_enable_state_of_specific_day(day, checked))
        self.input_different_times.toggled.connect(self._handle_enable_state_of_times_per_day)
        self.set_config_values()

    def _handle_enable_state_of_times_per_day(self, isChecked: bool) -> None:
        """Enable or disable the input fields for each day based on the state of the 'different times' checkbox."""
        for i in range(7):
            input_box: QDoubleSpinBox = getattr(self, f"input_hours_day_{i}")
            radio: QRadioButton = getattr(self, f"radio_weekday_{i}")
            input_box.setEnabled(isChecked and radio.isChecked())

    def _handle_enable_state_of_specific_day(self, day: int, isChecked: bool) -> None:
        """Enable or disable the input field for a specific day based on the state of the corresponding radio button."""
        if not self.input_different_times.isChecked():
            return
        input_box: QDoubleSpinBox = getattr(self, f"input_hours_day_{day}")
        input_box.setEnabled(isChecked)

    def _update_country_list(self, country: str | None = None) -> None:
        """Update the country and subdiv list. If country is given, use this as the selected country."""
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

    def _adjust_subdiv(self) -> None:
        """Triggered when the country selection changes."""
        country = self.input_country.currentText()
        subdiv_list = self.country_list.get(country, [])
        self.input_subdiv.clear()
        self.input_subdiv.addItems(subdiv_list)
        if CONFIG_HANDLER.config.subdiv not in subdiv_list:
            return
        self.input_subdiv.setCurrentText(CONFIG_HANDLER.config.subdiv)

    def set_config_values(self) -> None:
        """Set config values to the input fields, other than country and subdiv."""
        self.input_name.setText(CONFIG_HANDLER.config.name)
        self.input_daily_hours.setValue(CONFIG_HANDLER.config.daily_hours)
        self.input_weekly_hours.setValue(CONFIG_HANDLER.config.weekly_hours)
        for day in CONFIG_HANDLER.config.workdays:
            radio: QRadioButton = getattr(self, f"radio_weekday_{day}")
            radio.setChecked(True)
        self.input_different_times.setChecked(CONFIG_HANDLER.config.different_workdays)
        for i, time in enumerate(CONFIG_HANDLER.config.time_per_day):
            input_box: QDoubleSpinBox = getattr(self, f"input_hours_day_{i}")
            input_box.setValue(time)
            if i not in CONFIG_HANDLER.config.workdays or not CONFIG_HANDLER.config.different_workdays:
                input_box.setEnabled(False)

    def apply_config(self) -> None:
        """Apply the config values to the config file and close the window."""
        CONFIG_HANDLER.config.country = self.input_country.currentText()
        CONFIG_HANDLER.config.subdiv = self.input_subdiv.currentText() or None
        CONFIG_HANDLER.config.name = self.input_name.text()
        CONFIG_HANDLER.config.daily_hours = self.input_daily_hours.value()
        CONFIG_HANDLER.config.weekly_hours = self.input_weekly_hours.value()
        selected_days: list[int] = []
        for day in range(7):
            radio: QRadioButton = getattr(self, f"radio_weekday_{day}")
            if radio.isChecked():
                selected_days.append(day)
        CONFIG_HANDLER.config.workdays = selected_days
        CONFIG_HANDLER.config.different_workdays = self.input_different_times.isChecked()
        if self.input_different_times.isChecked():
            CONFIG_HANDLER.config.time_per_day = tuple(getattr(self, f"input_hours_day_{i}").value() for i in range(7))

        CONFIG_HANDLER.write_config_file()
        self.main_window.update_data_window()
        self.close()

    def _apply_subdiv_filter(self) -> None:
        """Apply the filter to the subdiv list and update the list."""
        country = self.input_country.currentText()
        subdiv_list = self.country_list.get(country, [])
        filter_text = self.filter_subdiv.text()
        current_subdiv = self.input_subdiv.currentText()
        if filter_text:
            subdiv_list = [s for s in subdiv_list if filter_text.lower() in s.lower()]
        self.input_subdiv.clear()
        self.input_subdiv.addItems(subdiv_list)
        if current_subdiv in subdiv_list:
            self.input_subdiv.setCurrentText(current_subdiv)

    def _apply_country_filter(self) -> None:
        """Apply the filter to the country list and update the list."""
        country_list = list(self.country_list.keys())
        filter_text = self.filter_country.text()
        current_country = self.input_country.currentText()
        if filter_text:
            country_list = [c for c in country_list if filter_text.lower() in c.lower()]
        self.input_country.clear()
        self.input_country.addItems(country_list)
        if current_country in country_list:
            self.input_country.setCurrentText(current_country)
        self._adjust_subdiv()
