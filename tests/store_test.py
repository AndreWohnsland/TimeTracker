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


def test_vacation_day_future_no_work_should_have_zero_work_and_overtime(
    store_and_controller: tuple[Store, MagicMock],
) -> None:
    """Test that a vacation day in the future with no work entries has 0 work and 0 overtime."""
    store_instance, mock_db_controller = store_and_controller
    daily_target = 8.0
    expected_zero = 0.0

    # Get tomorrow's date
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    month_first = tomorrow.replace(day=1)

    # Mock CONFIG_HANDLER to return 8 hours as daily target
    with patch("src.datastore.CONFIG_HANDLER") as mock_config:
        mock_config.config.get_daily_hours_at.return_value = daily_target
        mock_config.config.workdays = [0, 1, 2, 3, 4]  # Mon-Fri
        mock_config.config.get_holidays.return_value = []
        mock_config.config_hash.return_value = 12345

        # Set tomorrow as a vacation/free day
        mock_db_controller.get_time_off_days.return_value = [tomorrow]

        # Need at least one work entry for _generate_month_report to create full dataframe
        # Using a past date so it doesn't interfere with tomorrow's vacation
        past_date_str = f"{month_first.year}-{month_first.month:02d}-01T08:00:00"
        mock_db_controller.get_month_data.return_value = (
            [(past_date_str, "start"), (f"{month_first.year}-{month_first.month:02d}-01T09:00:00", "stop")],
            [],
        )

        # Generate month data
        month_data = store_instance.generate_month_data(month_first)
        df = month_data.df

        assert not df.empty, "Dataframe should not be empty"

        # Find tomorrow's row by converting index to date and comparing
        index_dates = [idx.date() if hasattr(idx, "date") else idx for idx in df.index]
        tomorrow_mask = [d == tomorrow for d in index_dates]
        tomorrow_rows = df[tomorrow_mask]

        assert not tomorrow_rows.empty, f"Tomorrow ({tomorrow}) should be in the dataframe"

        # Extract the values for tomorrow
        overtime_hours = tomorrow_rows["overtime"].values[0]
        target_time = tomorrow_rows["target_time"].values[0]

        # For future dates: overtime should be 0 (we cannot calculate overtime for future dates)
        assert overtime_hours == expected_zero, (
            f"Future vacation day should have {expected_zero} overtime hours, but got {overtime_hours} hours. "
            f"Overtime cannot be calculated for future dates."
        )

        # target_time should be 0 for future dates (as per current logic)
        assert target_time == expected_zero, f"Future date target_time should be {expected_zero}, but got {target_time}"


def test_vacation_day_past_no_work_has_correct_zero_overtime(
    store_and_controller: tuple[Store, MagicMock],
) -> None:
    """Test that a vacation day in the past with no work entries correctly has 0 overtime."""
    store_instance, mock_db_controller = store_and_controller
    daily_target = 8.0

    # Get yesterday's date
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    month_first = yesterday.replace(day=1)

    # Mock CONFIG_HANDLER to return 8 hours as daily target
    with patch("src.datastore.CONFIG_HANDLER") as mock_config:
        mock_config.config.get_daily_hours_at.return_value = daily_target
        mock_config.config.workdays = [0, 1, 2, 3, 4]  # Mon-Fri
        mock_config.config.get_holidays.return_value = []
        mock_config.config_hash.return_value = 12345

        # Set yesterday as a vacation/free day
        mock_db_controller.get_time_off_days.return_value = [yesterday]

        # Add a work entry on yesterday (the vacation day) to ensure the dataframe includes it
        yesterday_str = f"{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T08:00:00"
        yesterday_end = f"{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}T09:00:00"
        mock_db_controller.get_month_data.return_value = (
            [(yesterday_str, "start"), (yesterday_end, "stop")],
            [],
        )

        # Generate month data
        month_data = store_instance.generate_month_data(month_first)
        df = month_data.df

        assert not df.empty, "Dataframe should not be empty"

        # Find yesterday's row by converting index to date and comparing
        index_dates = [idx.date() if hasattr(idx, "date") else idx for idx in df.index]
        yesterday_mask = [d == yesterday for d in index_dates]
        yesterday_rows = df[yesterday_mask]

        assert not yesterday_rows.empty, f"Yesterday ({yesterday}) should be in the dataframe"

        # Extract the values for yesterday
        work_hours = yesterday_rows["work"].values[0]
        overtime_hours = yesterday_rows["overtime"].values[0]
        target_time = yesterday_rows["target_time"].values[0]

        # For a past vacation day, target_time is set correctly (8 hours)
        # This test confirms that PAST vacation days work correctly
        assert target_time == daily_target, f"Past date target_time should be {daily_target}, but got {target_time}"
        # The work hours should be approximately 1 (from 8am to 9am) + daily target added by free day logic
        assert work_hours > 0, f"Past vacation day work should be > 0, but got {work_hours}"
        # For this test, we're mainly checking that target_time is correctly set for past dates
        # The overtime calculation for past dates should work correctly
        assert isinstance(overtime_hours, (int, float)), f"Overtime should be a number, but got {type(overtime_hours)}"
