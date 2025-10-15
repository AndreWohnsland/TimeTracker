import datetime

from src.database_controller import DatabaseController


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
        db_controller.delete_event(future_date.isoformat())
        day_data, _ = db_controller.get_day_data(future_date.date())
        assert not any(future_date.isoformat() in item for item in day_data)

    def test_delete_pause(self, db_controller: DatabaseController) -> None:
        future_date = datetime.date(2026, 1, 4)
        db_controller.add_pause(60, future_date)
        _, pause_data = db_controller.get_day_data(future_date)
        assert any(future_date.isoformat() in item for item in pause_data)
        db_controller.update_pause(-60, future_date.isoformat())
        _, pause_data = db_controller.get_day_data(future_date)
        assert pause_data[0][1] == 0

    def test_update_pause(self, db_controller: DatabaseController) -> None:
        future_date = datetime.date(2026, 1, 5)
        db_controller.add_pause(60, future_date)
        db_controller.update_pause(30, future_date.isoformat())
        _, pause_data = db_controller.get_day_data(future_date)
        expected_time = 60 + 30
        assert any(str(expected_time) in str(item) for item in pause_data)

    def test_add_get_remove_vacation(self, db_controller: DatabaseController) -> None:
        vacation_date = datetime.date(2026, 2, 1)
        db_controller.add_vacation(vacation_date)
        vacation_days = db_controller.get_vacation_days(2026)
        assert vacation_date in vacation_days
        db_controller.remove_vacation(vacation_date)
        vacation_days = db_controller.get_vacation_days(2026)
        assert vacation_date not in vacation_days
