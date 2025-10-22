import datetime

import pytest

from src.database_controller import DatabaseController
from src.models import Event, Pause


class TestController:
    def test_get_month_data(self, db_controller: DatabaseController) -> None:
        month_data, pause_data = db_controller.get_month_data(datetime.date(2025, 1, 1))
        assert len(month_data) > 0
        assert len(pause_data) == 0
        assert len(month_data) > 0
        assert month_data[2] == ("2025-01-02T06:00:00", "start")

    def test_get_day_data(self, db_controller: DatabaseController) -> None:
        day_data, pause_data = db_controller.get_day_data(datetime.date(2025, 1, 3))
        assert len(day_data) > 0
        assert len(pause_data) == 0
        assert day_data == [("2025-01-03T06:00:00", "start"), ("2025-01-03T14:30:00", "stop")]

    def test_get_day_data_limits_to_selected_day(self, db_controller: DatabaseController) -> None:
        selected_day = datetime.date(2025, 1, 2)
        day_data, _ = db_controller.get_day_data(selected_day)
        day_dates = {datetime.datetime.fromisoformat(ts).date() for ts, _ in day_data}
        assert day_dates == {selected_day}

    def test_insert_event(self, db_controller: DatabaseController) -> None:
        future_date = datetime.datetime(2026, 1, 1, 10, 0, 0)
        db_controller.add_event("start", future_date)
        day_data, _ = db_controller.get_day_data(future_date.date())
        assert any(future_date.isoformat() in item for item in day_data)
        assert day_data[0] == (future_date.isoformat(), "start")

    def test_insert_pause(self, db_controller: DatabaseController) -> None:
        future_date = datetime.date(2026, 1, 2)
        db_controller.add_pause(60, future_date)
        _, pause_data = db_controller.get_day_data(future_date)
        assert any(future_date.isoformat() in item for item in pause_data)
        assert pause_data[0] == (future_date.isoformat(), 60)

    def test_delete_event(self, db_controller: DatabaseController) -> None:
        future_date = datetime.datetime(2026, 1, 3, 10, 0, 0)
        db_controller.add_event("start", future_date)
        db_controller.delete_event(future_date)
        day_data, _ = db_controller.get_day_data(future_date.date())
        assert not any(future_date.isoformat() in item for item in day_data)

    def test_delete_pause(self, db_controller: DatabaseController) -> None:
        future_date = datetime.date(2026, 1, 4)
        db_controller.add_pause(60, future_date)
        _, pause_data = db_controller.get_day_data(future_date)
        assert any(future_date.isoformat() in item for item in pause_data)
        db_controller.update_pause(-60, future_date)
        _, pause_data = db_controller.get_day_data(future_date)
        assert pause_data[0][1] == 0

    def test_update_pause(self, db_controller: DatabaseController) -> None:
        future_date = datetime.date(2026, 1, 5)
        db_controller.add_pause(60, future_date)
        db_controller.update_pause(30, future_date)
        _, pause_data = db_controller.get_day_data(future_date)
        expected_time = 60 + 30
        assert any(str(expected_time) in str(item) for item in pause_data)

    def test_add_get_remove_vacation(self, db_controller: DatabaseController) -> None:
        vacation_date = datetime.date(2026, 2, 1)
        db_controller.add_time_off(vacation_date, "Vacation")
        vacation_days = db_controller.get_time_off_days(2026)
        assert vacation_date in vacation_days
        db_controller.remove_time_off(vacation_date)
        vacation_days = db_controller.get_time_off_days(2026)
        assert vacation_date not in vacation_days

    def test_reason_on_vacation(self, db_controller: DatabaseController) -> None:
        vacation_date = datetime.date(2026, 2, 2)
        reason = "Sick Leave"
        db_controller.add_time_off(vacation_date, reason)
        vacation_days = db_controller.get_time_off(2026)
        assert any(vacation.date == vacation_date and vacation.reason == reason for vacation in vacation_days)

    def test_change_time_off_reason(self, db_controller: DatabaseController) -> None:
        vacation_date = datetime.date(2026, 2, 3)
        initial_reason = "Vacation"
        new_reason = "Sick Leave"
        db_controller.add_time_off(vacation_date, initial_reason)
        db_controller.change_time_off_reason(vacation_date, new_reason)
        vacation_days = db_controller.get_time_off(2026)
        assert any(vacation.date == vacation_date and vacation.reason == new_reason for vacation in vacation_days)

    def test_get_period_work_orders_results(self, db_controller: DatabaseController) -> None:
        random_events = [
            Event(date=datetime.datetime(2030, 5, 1, 15, 45), action="stop"),
            Event(date=datetime.datetime(2030, 5, 1, 6, 15), action="start"),
            Event(date=datetime.datetime(2030, 5, 1, 12, 0), action="coffee"),
            Event(date=datetime.datetime(2030, 5, 1, 14, 0), action="resume"),
        ]

        with db_controller.session_scope() as session:
            session.add_all(random_events)

        period = db_controller.get_period_work(datetime.date(2030, 5, 1), datetime.date(2030, 5, 2))
        timestamps = [datetime.datetime.fromisoformat(ts) for ts, _ in period]

        assert timestamps == sorted(event.date for event in random_events)

    def test_get_period_pause_orders_results(self, db_controller: DatabaseController) -> None:
        random_pauses = [
            Pause(date=datetime.date(2030, 5, 3), time=45),
            Pause(date=datetime.date(2030, 5, 1), time=15),
            Pause(date=datetime.date(2030, 5, 2), time=30),
        ]

        with db_controller.session_scope() as session:
            session.add_all(random_pauses)

        period = db_controller.get_period_pause(datetime.date(2030, 5, 1), datetime.date(2030, 5, 3))
        pause_dates = [date for date, _ in period]

        assert pause_dates == sorted(pause.date.isoformat() for pause in random_pauses)

    def test_get_months_with_data(self, db_controller: DatabaseController) -> None:
        months = db_controller.get_months_with_data()
        expected_months = {(2025, m) for m in range(1, 13)}
        assert months == sorted(expected_months)

    @pytest.mark.parametrize(
        "year, has_data",
        [(2025, True), (2024, False), (2026, False), (None, True)],
    )
    def test_get_months_with_data_for_specific_year(
        self, db_controller: DatabaseController, year: int | None, has_data: bool
    ) -> None:
        result = db_controller.get_months_with_data(year)
        assert (len(result) > 0) == has_data
