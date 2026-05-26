"""Tests for account-wide squad plan advisor."""

from types import SimpleNamespace

from swgoh_helper.squad_plan_advisor import SquadPlanAdvisor


class _FakeRecommender:
    def __init__(self):
        self.profiles = {
            "A": SimpleNamespace(squad="Alpha"),
            "B": SimpleNamespace(squad="Alpha"),
            "C": SimpleNamespace(squad="Bravo"),
        }

    def analyze(self, player, goal_mode="pve", focus="squads", eligibility="best_effort"):
        alpha_unit = SimpleNamespace(
            base_id="A",
            unit_name="Unit A",
            squad="Alpha",
            priority_score=100,
            findings=[SimpleNamespace(message="Missing 2 equipped mods.")],
        )
        bravo_unit = SimpleNamespace(
            base_id="C",
            unit_name="Unit C",
            squad="Bravo",
            priority_score=50,
            findings=[SimpleNamespace(message="Speed 150 is below the 200 target.")],
        )
        return SimpleNamespace(audited_units=[alpha_unit, bravo_unit])


def _player():
    units = [
        SimpleNamespace(data=SimpleNamespace(base_id="A", name="Unit A")),
        SimpleNamespace(data=SimpleNamespace(base_id="C", name="Unit C")),
    ]
    data = SimpleNamespace(name="Tester", ally_code=123456789)
    return SimpleNamespace(data=data, units=units, mods=[])


def test_recommend_for_account_includes_memberships_and_actions():
    advisor = SquadPlanAdvisor(recommender=_FakeRecommender())

    output = advisor.recommend_for_account(_player(), top_squads=2, plan_steps=3)

    assert "Recommended squads and exact memberships" in output
    assert "1. Alpha" in output
    assert "Membership: Unit A" in output
    assert "Account improvement plan (Do 1-N)" in output
    assert "Do 1:" in output
