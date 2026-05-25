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
    assert "Hera Syndulla (Phoenix | Fleet: Rebel Fleet)" in output
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


def test_analyze_fleet_focus_only_includes_fleet_profiles():
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
        _unit("CAPTAINREX", "Captain Rex", speed=200),
        _unit("BOSSK", "Bossk", speed=180),
    ]

    report = recommender.analyze(
        _player(units=units, mods=[]),
        goal_mode="proving_grounds",
        focus="fleets",
        eligibility="off",
    )

    assert report.focus == "fleets"
    assert report.goal_mode == "proving_grounds"
    assert len(report.audited_units) == 1
    assert report.audited_units[0].base_id == "BOSSK"
    assert report.audited_units[0].fleet == "Executor Core"


def test_format_report_shows_mode_and_group_summaries():
    recommender = ModRecommender(
        profiles={
            "BOSSK": {
                "squad": "Bounty Hunters",
                "target_sets": ["Health", "Health", "Tenacity"],
                "recommended_primaries": {3: "Speed", 7: "Tenacity"},
                "priority_stats": ["Health"],
                "speed_floor": 220,
            }
        }
    )
    units = [_unit("BOSSK", "Bossk", speed=170)]
    report = recommender.analyze(
        _player(units=units, mods=[]),
        goal_mode="gac_defense",
        focus="both",
    )

    output = recommender.format_report(report, top_n=1)

    assert "Mode: gac_defense" in output
    assert "Focus: both" in output
    assert "Top squads by need" in output
    assert "Top fleets by need" in output


def test_analyze_supports_order66_raid_mode():
    recommender = ModRecommender(
        profiles={
            "EMPERORPALPATINE": {
                "squad": "Empire",
                "target_sets": ["Speed", "Potency"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Speed"],
                "speed_floor": 240,
            }
        }
    )
    units = [_unit("EMPERORPALPATINE", "Emperor Palpatine", speed=150)]

    report = recommender.analyze(
        _player(units=units, mods=[]),
        goal_mode="raid_order66",
        focus="squads",
    )

    assert report.goal_mode == "raid_order66"
    assert report.audited_units
    assert report.audited_units[0].mode_weight >= 1.2


def test_order66_best_effort_excludes_ineligible_squads_and_fleets():
    recommender = ModRecommender(
        profiles={
            "EMPERORPALPATINE": {
                "squad": "Empire",
                "target_sets": ["Speed", "Potency"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Speed"],
                "speed_floor": 240,
            },
            "HERASYNDULLAS3": {
                "squad": "Phoenix",
                "target_sets": ["Speed", "Potency"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Speed"],
                "speed_floor": 240,
            },
        }
    )
    units = [
        _unit("EMPERORPALPATINE", "Emperor Palpatine", speed=150),
        _unit("HERASYNDULLAS3", "Hera Syndulla", speed=250),
    ]

    report = recommender.analyze(
        _player(units=units, mods=[]),
        goal_mode="raid_order66",
        focus="both",
        eligibility="best_effort",
    )

    assert len(report.audited_units) == 1
    assert report.audited_units[0].base_id == "EMPERORPALPATINE"
    assert report.excluded_ineligible_count == 1


def test_report_calls_out_unknown_eligibility_modes():
    recommender = ModRecommender(
        profiles={
            "EMPERORPALPATINE": {
                "squad": "Empire",
                "target_sets": ["Speed", "Potency"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Speed"],
                "speed_floor": 240,
            }
        }
    )
    units = [_unit("EMPERORPALPATINE", "Emperor Palpatine", speed=150)]
    report = recommender.analyze(
        _player(units=units, mods=[]),
        goal_mode="raid",
        focus="squads",
        eligibility="best_effort",
    )

    output = recommender.format_report(report, top_n=1)

    assert "Eligibility: best_effort (unknown)" in output
    assert "Eligibility note:" in output


def test_order66_prioritizes_tarkin_with_unit_multiplier():
    recommender = ModRecommender(
        profiles={
            "GRANDMOFFTARKIN": {
                "squad": "Empire",
                "target_sets": ["Speed", "Potency"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Speed"],
                "speed_floor": 250,
            },
            "EMPERORPALPATINE": {
                "squad": "Empire",
                "target_sets": ["Speed", "Potency"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Speed"],
                "speed_floor": 250,
            },
        }
    )
    units = [
        _unit("GRANDMOFFTARKIN", "Grand Moff Tarkin", speed=120),
        _unit("EMPERORPALPATINE", "Emperor Palpatine", speed=120),
    ]

    report = recommender.analyze(
        _player(units=units, mods=[]),
        goal_mode="raid_order66",
        focus="squads",
        eligibility="best_effort",
    )

    assert report.audited_units[0].base_id == "GRANDMOFFTARKIN"
    assert report.audited_units[0].mode_weight > report.audited_units[1].mode_weight


def test_order66_report_includes_key_mode_anchor_section():
    recommender = ModRecommender(
        profiles={
            "GRANDMOFFTARKIN": {
                "squad": "Empire",
                "target_sets": ["Speed", "Potency"],
                "recommended_primaries": {3: "Speed"},
                "priority_stats": ["Speed"],
                "speed_floor": 250,
            }
        }
    )
    units = [_unit("GRANDMOFFTARKIN", "Grand Moff Tarkin", speed=120)]
    report = recommender.analyze(
        _player(units=units, mods=[]),
        goal_mode="raid_order66",
        focus="squads",
        eligibility="best_effort",
    )

    output = recommender.format_report(report, top_n=1)

    assert "Key mode anchors" in output
    assert "Grand Moff Tarkin" in output