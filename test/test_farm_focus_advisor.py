"""Tests for target-focused farm advisor."""

from types import SimpleNamespace

from swgoh_helper.farm_focus_advisor import FarmFocusAdvisor


def _player(units):
    data = SimpleNamespace(name="Tester", ally_code=123456789)
    return SimpleNamespace(data=data, units=units, mods=[])


def _player_unit(base_id: str, name: str, rarity: int = 6, gear_level: int = 12, relic: int = -1):
    data = SimpleNamespace(
        base_id=base_id,
        name=name,
        rarity=rarity,
        gear_level=gear_level,
        relic_tier_or_minus_one=relic,
    )
    return SimpleNamespace(data=data)


def _units_data(*units):
    return SimpleNamespace(data=list(units))


def _unit(base_id: str, name: str):
    return SimpleNamespace(base_id=base_id, name=name)


def test_recommend_for_target_returns_ranked_nodes_for_known_target():
    advisor = FarmFocusAdvisor()
    player = _player(units=[_player_unit("GRANDMOFFTARKIN", "Grand Moff Tarkin", rarity=6)])
    units_data = _units_data(_unit("GRANDMOFFTARKIN", "Grand Moff Tarkin"))

    output = advisor.recommend_for_target(player, units_data, "Grand Moff Tarkin", top_n=3)

    assert "Target Farm Advisor for Tester" in output
    assert "Target: Grand Moff Tarkin" in output
    assert "Best campaign energy nodes" in output


def test_recommend_for_target_includes_mod_estimate_note():
    advisor = FarmFocusAdvisor()
    player = _player(units=[_player_unit("EMPERORPALPATINE", "Emperor Palpatine", rarity=7, relic=7)])
    units_data = _units_data(_unit("EMPERORPALPATINE", "Emperor Palpatine"))

    output = advisor.recommend_for_target(player, units_data, "Emperor Palpatine", top_n=2)

    assert "Mod farming note: target sets are" in output
    assert "mod battle routing is estimated" in output
