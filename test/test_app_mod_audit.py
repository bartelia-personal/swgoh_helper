"""Tests for mod audit app orchestration."""

from types import SimpleNamespace

from swgoh_helper.app import ModAuditApp


class _FakeService:
    def get_player(self, _ally_code):
        data = SimpleNamespace(name="Tester", ally_code=123456789)
        return SimpleNamespace(data=data, units=[], mods=[])


class _FakeRecommender:
    def analyze(self, player, goal_mode="pve", focus="both", eligibility="best_effort"):
        self.player = player
        self.goal_mode = goal_mode
        self.focus = focus
        self.eligibility = eligibility
        return "report"

    def format_report(self, report, top_n=10):
        self.report = report
        self.top_n = top_n
        return "formatted"


def test_mod_audit_app_fetches_player_and_formats_report():
    app = ModAuditApp.__new__(ModAuditApp)
    app.progress = SimpleNamespace(update=lambda _message: None)
    app.service = _FakeService()
    app.recommender = _FakeRecommender()

    output = app.analyze_player(
        "123-456-789",
        top_n=8,
        goal_mode="gac_offense",
        focus="fleets",
        eligibility="off",
    )

    assert output == "formatted"
    assert app.recommender.report == "report"
    assert app.recommender.top_n == 8
    assert app.recommender.goal_mode == "gac_offense"
    assert app.recommender.focus == "fleets"
    assert app.recommender.eligibility == "off"