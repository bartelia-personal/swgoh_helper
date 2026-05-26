"""Tests for account-wide squad plan advisor."""

from types import SimpleNamespace

from swgoh_helper.squad_plan_advisor import SquadPlanAdvisor


class _FakeRecommender:
    def __init__(self):
        self.profiles = {
            "A": SimpleNamespace(squad="Alpha"),
            "B": SimpleNamespace(squad="Alpha"),
            "D": SimpleNamespace(squad="Alpha"),
            "E": SimpleNamespace(squad="Alpha"),
            "F": SimpleNamespace(squad="Alpha"),
            "G": SimpleNamespace(squad="Alpha"),
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
        alpha_unit_b = SimpleNamespace(
            base_id="B",
            unit_name="Unit B",
            squad="Alpha",
            priority_score=99,
            findings=[SimpleNamespace(message="Missing 1 equipped mods.")],
        )
        alpha_unit_d = SimpleNamespace(
            base_id="D",
            unit_name="Unit D",
            squad="Alpha",
            priority_score=98,
            findings=[SimpleNamespace(message="Missing 1 equipped mods.")],
        )
        alpha_unit_e = SimpleNamespace(
            base_id="E",
            unit_name="Unit E",
            squad="Alpha",
            priority_score=97,
            findings=[SimpleNamespace(message="Missing 1 equipped mods.")],
        )
        alpha_unit_f = SimpleNamespace(
            base_id="F",
            unit_name="Unit F",
            squad="Alpha",
            priority_score=96,
            findings=[SimpleNamespace(message="Missing 1 equipped mods.")],
        )
        alpha_unit_g = SimpleNamespace(
            base_id="G",
            unit_name="Unit G",
            squad="Alpha",
            priority_score=95,
            findings=[SimpleNamespace(message="Missing 1 equipped mods.")],
        )
        bravo_unit = SimpleNamespace(
            base_id="C",
            unit_name="Unit C",
            squad="Bravo",
            priority_score=50,
            findings=[SimpleNamespace(message="Speed 150 is below the 200 target.")],
        )
        return SimpleNamespace(
            audited_units=[
                alpha_unit,
                alpha_unit_b,
                alpha_unit_d,
                alpha_unit_e,
                alpha_unit_f,
                alpha_unit_g,
                bravo_unit,
            ]
        )


def _player():
    units = [
        SimpleNamespace(data=SimpleNamespace(base_id="A", name="Unit A")),
        SimpleNamespace(data=SimpleNamespace(base_id="B", name="Unit B")),
        SimpleNamespace(data=SimpleNamespace(base_id="C", name="Unit C")),
        SimpleNamespace(data=SimpleNamespace(base_id="D", name="Unit D")),
        SimpleNamespace(data=SimpleNamespace(base_id="E", name="Unit E")),
        SimpleNamespace(data=SimpleNamespace(base_id="F", name="Unit F")),
        SimpleNamespace(data=SimpleNamespace(base_id="G", name="Unit G")),
    ]
    data = SimpleNamespace(name="Tester", ally_code=123456789)
    return SimpleNamespace(data=data, units=units, mods=[])


def test_recommend_for_account_includes_memberships_and_actions():
    advisor = SquadPlanAdvisor(recommender=_FakeRecommender())

    output = advisor.recommend_for_account(_player(), top_squads=2, plan_steps=3)

    assert "Recommended squads and exact memberships" in output
    assert "1. Alpha" in output
    assert "Primary 5:" in output
    assert "Alternates:" in output
    assert "Unit G" in output
    assert "Account improvement plan (Do 1-N)" in output
    assert "Do 1: [Alpha]" in output
