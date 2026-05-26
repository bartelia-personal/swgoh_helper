"""Tests for squad-plan app orchestration."""

from types import SimpleNamespace

from swgoh_helper.app import SquadPlanApp


class _FakeService:
    def get_player(self, _ally_code):
        data = SimpleNamespace(name="Tester", ally_code=123456789)
        return SimpleNamespace(data=data, units=[], mods=[])


class _FakeAdvisor:
    def recommend_for_account(self, player, top_squads=5, plan_steps=10, eligibility="best_effort"):
        self.player = player
        self.top_squads = top_squads
        self.plan_steps = plan_steps
        self.eligibility = eligibility
        return "squad-plan"


def test_squad_plan_app_fetches_player_and_formats_report():
    app = SquadPlanApp.__new__(SquadPlanApp)
    app.progress = SimpleNamespace(update=lambda _message: None)
    app.service = _FakeService()
    app.advisor = _FakeAdvisor()

    output = app.recommend_for_account(
        "123-456-789",
        top_squads=4,
        plan_steps=7,
        eligibility="off",
    )

    assert output == "squad-plan"
    assert app.advisor.player.data.name == "Tester"
    assert app.advisor.top_squads == 4
    assert app.advisor.plan_steps == 7
    assert app.advisor.eligibility == "off"
