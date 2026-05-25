"""Tests for farm-focus app orchestration."""

from types import SimpleNamespace

from swgoh_helper.app import FarmFocusApp


class _FakeService:
    def get_all_units(self):
        return "units"

    def get_player(self, _ally_code):
        return "player"


class _FakeAdvisor:
    def recommend_for_target(self, player, units_data, target_query, top_n=8):
        self.player = player
        self.units_data = units_data
        self.target_query = target_query
        self.top_n = top_n
        return "focused-report"


def test_farm_focus_app_fetches_data_and_formats_report():
    app = FarmFocusApp.__new__(FarmFocusApp)
    app.progress = SimpleNamespace(update=lambda _message: None)
    app.service = _FakeService()
    app.advisor = _FakeAdvisor()

    output = app.recommend_for_target("123-456-789", "Grand Moff Tarkin", top_n=6)

    assert output == "focused-report"
    assert app.advisor.player == "player"
    assert app.advisor.units_data == "units"
    assert app.advisor.target_query == "Grand Moff Tarkin"
    assert app.advisor.top_n == 6
