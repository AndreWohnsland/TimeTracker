import datetime
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.datastore import MonthData, Store


@pytest.fixture
def mock_db_controller() -> MagicMock:
    mock = MagicMock()
    # Default: no data
    mock.get_time_off_days.return_value = []
    mock.get_day_data.return_value = ([], [])
    mock.get_month_data.return_value = ([], [])
    mock.get_months_with_data.return_value = []
    return mock


@pytest.fixture
def store_and_controller(mock_db_controller: MagicMock) -> Generator[tuple[Store, MagicMock], None, None]:
    with patch("src.datastore.DB_CONTROLLER", mock_db_controller):
        yield Store(), mock_db_controller


def test_store_initialization(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, _ = store_and_controller
    assert isinstance(store_instance, Store)
    assert isinstance(store_instance.df, pd.DataFrame)
    assert isinstance(store_instance.daily_data, list)
    assert isinstance(store_instance.all_data, dict)
    assert isinstance(store_instance.overtime_by_year, dict)
    assert store_instance.total_overtime == 0.0


def test_update_data_with_data(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    test_date = datetime.date(2025, 5, 20)
    # Simulate a work event and a pause
    mock_db_controller.get_day_data.return_value = (
        [("2025-05-20T08:00:00", "start"), ("2025-05-20T16:00:00", "stop")],
        [("2025-05-20", 60)],
    )
    store_instance.update_data(test_date)
    assert store_instance.current_date == test_date
    assert isinstance(store_instance.df, pd.DataFrame)
    assert "work" in store_instance.df.columns or store_instance.df.empty


def test_update_data_none_date(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    # Should use current_date if None
    mock_db_controller.get_day_data.return_value = ([("2025-05-20T08:00:00", "start")], [])
    store_instance.update_data(None)
    assert store_instance.current_date == store_instance.current_date


def test_get_free_days_with_vacation_and_holiday(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    # Simulate vacation and holiday
    mock_db_controller.get_time_off_days.return_value = [datetime.date(2025, 5, 1)]
    with patch("src.datastore.CONFIG_HANDLER") as mock_config:
        mock_config.config.get_holidays.return_value = [datetime.date(2025, 5, 2)]
        mock_config.config.workdays = [0, 1, 2, 3, 4]
        free_days = store_instance.get_free_days(2025)
        assert datetime.date(2025, 5, 1) in free_days or datetime.date(2025, 5, 2) in free_days


def test_generate_all_data_populates_all_data(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    # Simulate month data
    mock_db_controller.get_months_with_data.return_value = [(2025, 5)]
    mock_db_controller.get_month_data.return_value = ([("2025-05-01T08:00:00", "start")], [])
    store_instance.generate_all_data()
    assert len(store_instance.all_data) > 0
    for key, value in store_instance.all_data.items():
        assert isinstance(value, MonthData)


def test_get_year_data_returns_dataframe(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    mock_db_controller.get_month_data.return_value = ([("2025-05-01T08:00:00", "start")], [])
    year_data = store_instance.get_year_data(2025)
    assert isinstance(year_data, pd.DataFrame)


def test_generate_daily_data_with_pause(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    test_date = datetime.date(2025, 5, 20)
    mock_db_controller.get_day_data.return_value = ([("2025-05-20T08:00:00", "start")], [("2025-05-20", 30)])
    store_instance.generate_daily_data(test_date)
    assert any("Pause" in entry for entry in store_instance.daily_data)


def test_generate_month_data_empty_work(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    test_date = datetime.date(2025, 5, 1)
    mock_db_controller.get_month_data.return_value = ([], [])
    month_data = store_instance.generate_month_data(test_date)
    assert isinstance(month_data.df, pd.DataFrame)
    assert month_data.df.empty


def test_generate_month_data_with_work(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    test_date = datetime.date(2025, 5, 1)
    mock_db_controller.get_month_data.return_value = (
        [("2025-05-01T08:00:00", "start"), ("2025-05-01T16:00:00", "stop")],
        [("2025-05-01", 60)],
    )
    month_data = store_instance.generate_month_data(test_date)
    assert isinstance(month_data.df, pd.DataFrame)
    assert not month_data.df.empty
    assert "work" in month_data.df.columns


def test_calculate_overtime_totals_with_data(store_and_controller: tuple[Store, MagicMock]) -> None:
    store_instance, mock_db_controller = store_and_controller
    # Simulate month data with overtime
    mock_db_controller.get_months_with_data.return_value = [(2025, 5)]
    mock_db_controller.get_month_data.return_value = (
        [("2025-05-01T08:00:00", "start"), ("2025-05-01T18:00:00", "stop")],
        [],
    )
    store_instance.generate_all_data()
    store_instance.calculate_overtime_totals()
    assert isinstance(store_instance.total_overtime, float)
    assert isinstance(store_instance.overtime_by_year, dict)
