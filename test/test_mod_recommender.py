"""Tests for the mod audit analyzer."""

from types import SimpleNamespace

from swgoh_helper.mod_recommender import ModRecommender


def _unit(base_id: str, name: str, speed: int, relic: int = 3, gear: int = 13, rarity: int = 7, mod_set_ids=None):
    data = SimpleNamespace(
        base_id=base_id,
        name=name,
        rarity=rarity,
        gear_level=gear,
        relic_tier_or_minus_one=relic,
        stats={"5": speed},
        mod_set_ids=mod_set_ids or [],
    )
    return SimpleNamespace(data=data)


def _mod(character: str, slot: int, set_id: str, primary: str):
    primary_stat = SimpleNamespace(name=primary)
    return SimpleNamespace(character=character, slot=slot, set=set_id, primary_stat=primary_stat)


def _player(units, mods):
    data = SimpleNamespace(name="Tester", ally_code=123456789)
    return SimpleNamespace(data=data, units=units, mods=mods)


def test_analyze_prioritizes_missing_mods_and_set_mismatches():
    recommender = ModRecommender(
        profiles={
            "CAPTAINREX": {
                "squad": "Phoenix",
                "target_sets": ["Speed", "Health"],
                "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
                "priority_stats": ["Speed"],
                "speed_floor": 260,
            }
        }
    )
    player = _player(units=[_unit("CAPTAINREX", "Captain Rex", speed=190)], mods=[])

    report = recommender.analyze(player)

    assert report.profiled_units_owned == 1
    result = report.audited_units[0]
    assert result.priority_score > 0
    assert result.equipped_mod_count == 0
    assert result.findings[0].message == "Missing 6 equipped mods."
    assert any("Speed 190 is below the 260 target." == finding.message for finding in result.findings)


def test_format_report_surfaces_top_findings():
    recommender = ModRecommender(
        profiles={
            "HERASYNDULLAS3": {
                "squad": "Phoenix",
                "target_sets": ["Speed", "Potency"],
                "recommended_primaries": {3: "Speed", 7: "Potency"},
                "priority_stats": ["Speed"],
                "speed_floor": 240,
            }
        }
    )
    units = [_unit("HERASYNDULLAS3", "Hera Syndulla", speed=250, mod_set_ids=["4", "4", "4", "4", "1", "1"])]
    mods = [
        _mod("HERASYNDULLAS3", 3, "4", "Speed"),
        _mod("HERASYNDULLAS3", 7, "1", "Health"),
    ]
    report = recommender.analyze(_player(units=units, mods=mods))

    output = recommender.format_report(report)

    assert "Mod Audit for Tester" in output
    assert "Best mod sets first" not in output
    assert "Hera Syndulla (Phoenix)" in output
    assert "Cross has Health primary; target is Potency." in output
    assert "Sets: current none | target Speed, Potency" in output


def test_format_report_includes_priority_assignment_summary():
    recommender = ModRecommender(
        profiles={
            "CAPTAINREX": {
                "squad": "Phoenix",
                "target_sets": ["Speed", "Health"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Speed"],
                "speed_floor": 260,
            },
            "BOSSK": {
                "squad": "Bounty Hunters",
                "target_sets": ["Health", "Health", "Tenacity"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Health"],
                "speed_floor": 220,
            },
        }
    )
    units = [
        _unit("CAPTAINREX", "Captain Rex", speed=173),
        _unit("BOSSK", "Bossk", speed=171),
    ]

    output = recommender.format_report(recommender.analyze(_player(units=units, mods=[])))

    assert "1. Captain Rex -> Speed, Health" in output
    assert "2. Bossk -> Health, Health, Tenacity" in output