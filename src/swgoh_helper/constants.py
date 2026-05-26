"""
Constants used throughout the swgoh_helper application.
"""

from .models.rote import RotePath

# Kyrotech salvage IDs and display names
KYROTECH_SALVAGE_IDS = {
    "172Salvage": "Mk 7 Kyrotech Shock Prod Prototype Salvage",
    "173Salvage": "Mk 9 Kyrotech Battle Computer Prototype Salvage",
    "174Salvage": "Mk 5 Kyrotech Power Cell Prototype Salvage",
}

MAX_GEAR_TIER = 13

# Unlock thresholds
ZEFFO_THRESHOLD = 30
MANDALORE_THRESHOLD = 25

# Minimum relic tier required (R1 = 1, R5 = 5, etc.)
MIN_RELIC_TIER = 7  # Must have at least R7 to qualify

# Distance scoring weights (from farming recommendations)
RELIC_WEIGHT = 1.0  # Each relic level
GEAR_WEIGHT = 0.5  # Each gear level to G13
STAR_WEIGHT = 2.0  # Each missing star

# Star requirements for relic levels
RELIC_STAR_REQUIREMENTS = {
    0: 0,
    1: 5,
    2: 5,
    3: 5,
    4: 6,
    5: 7,
    6: 7,
    7: 7,
    8: 7,
    9: 7,
    10: 7,
}

# Farming recommendations
MAX_PLAYERS_PER_UNIT = 20  # Max players to show per unit in farming recommendations

# Journey guide path planning
JOURNEY_GUIDE_REQUIREMENTS_FILENAME = "journey_guide_requirements.json"
UNOWNED_UNIT_PENALTY = 15.0

# Limited-availability policy
LIMITED_AVAILABILITY_BASE_THRESHOLD = 3
LIMITED_AVAILABILITY_CALLOUT_THRESHOLD = 4

# ROTE path display/planet prefixes
PATH_TO_PLANET_PREFIX = {
    RotePath.DARK_SIDE: "DS",
    RotePath.LIGHT_SIDE: "LS",
    RotePath.NEUTRAL: "N",
}

# Mod audit
MOD_SET_NAMES = {
    "1": "Health",
    "2": "Offense",
    "3": "Defense",
    "4": "Speed",
    "5": "Critical Chance",
    "6": "Critical Damage",
    "7": "Potency",
    "8": "Tenacity",
}

MOD_SET_SIZES = {
    "Health": 2,
    "Offense": 4,
    "Defense": 2,
    "Speed": 4,
    "Critical Chance": 2,
    "Critical Damage": 4,
    "Potency": 2,
    "Tenacity": 2,
}

MOD_SLOT_NAMES = {
    2: "Square",
    3: "Arrow",
    4: "Diamond",
    5: "Circle",
    6: "Triangle",
    7: "Cross",
}

MOD_AUDIT_PROFILES = {
    "CAPTAINREX": {
        "squad": "Phoenix",
        "target_sets": ["Speed", "Health"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Protection", "Health", "Potency"],
        "speed_floor": 260,
    },
    "HERASYNDULLAS3": {
        "squad": "Phoenix",
        "target_sets": ["Speed", "Potency"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Protection", "Health"],
        "speed_floor": 240,
    },
    "CHOPPERS3": {
        "squad": "Phoenix",
        "target_sets": ["Speed", "Health"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Protection"},
        "priority_stats": ["Speed", "Protection", "Health", "Defense"],
        "speed_floor": 220,
    },
    "KANANJARRUSS3": {
        "squad": "Phoenix",
        "target_sets": ["Health", "Tenacity"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Tenacity"},
        "priority_stats": ["Protection", "Health", "Tenacity", "Speed"],
        "speed_floor": 200,
    },
    "SABINEWRENS3": {
        "squad": "Phoenix",
        "target_sets": ["Speed", "Critical Damage"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Offense", "Critical Chance"],
        "speed_floor": 230,
    },
    "BOSSK": {
        "squad": "Bounty Hunters",
        "target_sets": ["Health", "Health", "Tenacity"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Tenacity"},
        "priority_stats": ["Protection", "Health", "Speed", "Tenacity"],
        "speed_floor": 220,
    },
    "GREEFKARGA": {
        "squad": "Bounty Hunters",
        "target_sets": ["Speed", "Health"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Protection", "Health", "Potency"],
        "speed_floor": 260,
    },
    "THEMANDALORIAN": {
        "squad": "Bounty Hunters",
        "target_sets": ["Critical Damage", "Critical Chance"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Offense"},
        "priority_stats": ["Speed", "Offense", "Critical Chance", "Protection"],
        "speed_floor": 240,
    },
    "BOBAFETT": {
        "squad": "Bounty Hunters",
        "target_sets": ["Offense", "Critical Chance"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Offense"},
        "priority_stats": ["Speed", "Offense", "Critical Chance", "Protection"],
        "speed_floor": 220,
    },
    "CADBANE": {
        "squad": "Bounty Hunters",
        "target_sets": ["Offense", "Critical Chance"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Offense"},
        "priority_stats": ["Speed", "Offense", "Critical Chance", "Protection"],
        "speed_floor": 220,
    },
    "ZAMWESELL": {
        "squad": "Bounty Hunters",
        "target_sets": ["Speed", "Health"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Protection", "Health", "Potency"],
        "speed_floor": 280,
    },
    "EMBO": {
        "squad": "Bounty Hunters",
        "target_sets": ["Offense", "Critical Chance"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Offense"},
        "priority_stats": ["Offense", "Speed", "Critical Chance", "Protection"],
        "speed_floor": 220,
    },
    "EMPERORPALPATINE": {
        "squad": "Empire",
        "target_sets": ["Speed", "Potency"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Protection", "Health"],
        "speed_floor": 240,
    },
    "VADER": {
        "squad": "Empire",
        "target_sets": ["Offense", "Critical Chance"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Potency"},
        "priority_stats": ["Offense", "Speed", "Potency", "Critical Chance"],
        "speed_floor": 230,
    },
    "MARAJADE": {
        "squad": "Empire",
        "target_sets": ["Speed", "Potency"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Protection", "Health"],
        "speed_floor": 300,
    },
    "ROYALGUARD": {
        "squad": "Empire",
        "target_sets": ["Health", "Health", "Defense"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Health"},
        "priority_stats": ["Protection", "Health", "Defense", "Speed"],
        "speed_floor": 180,
    },
    "GRANDMOFFTARKIN": {
        "squad": "Empire",
        "target_sets": ["Speed", "Potency"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Protection", "Health"],
        "speed_floor": 250,
    },
    "GENERALHUX": {
        "squad": "First Order",
        "target_sets": ["Speed", "Health"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Protection", "Health"],
        "speed_floor": 280,
    },
    "KYLORENUNMASKED": {
        "squad": "First Order",
        "target_sets": ["Health", "Health", "Tenacity"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Tenacity"},
        "priority_stats": ["Protection", "Health", "Tenacity", "Speed"],
        "speed_floor": 200,
    },
    "KYLOREN": {
        "squad": "First Order",
        "target_sets": ["Offense", "Critical Chance"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Offense"},
        "priority_stats": ["Offense", "Speed", "Critical Chance", "Protection"],
        "speed_floor": 210,
    },
    "FOSITHTROOPER": {
        "squad": "First Order",
        "target_sets": ["Offense", "Critical Chance"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Offense"},
        "priority_stats": ["Offense", "Critical Chance", "Speed", "Protection"],
        "speed_floor": 200,
    },
    "FIRSTORDEROFFICERMALE": {
        "squad": "First Order",
        "target_sets": ["Speed", "Health"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Protection", "Health", "Potency"],
        "speed_floor": 270,
    },
    "FIRSTORDEREXECUTIONER": {
        "squad": "First Order",
        "target_sets": ["Offense", "Critical Chance"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Critical Damage", 7: "Offense"},
        "priority_stats": ["Offense", "Critical Chance", "Speed", "Protection"],
        "speed_floor": 200,
    },
    "ADMIRALPIETT": {
        "squad": "Imperial Troopers",
        "target_sets": ["Speed", "Potency"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Protection", "Health"],
        "speed_floor": 300,
    },
    "VEERS": {
        "squad": "Imperial Troopers",
        "target_sets": ["Speed", "Potency"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Protection", "Health"],
        "speed_floor": 240,
    },
    "RANGETROOPER": {
        "squad": "Imperial Troopers",
        "target_sets": ["Speed", "Health"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Protection"},
        "priority_stats": ["Speed", "Protection", "Health", "Defense"],
        "speed_floor": 220,
    },
    "COLONELSTARCK": {
        "squad": "Imperial Troopers",
        "target_sets": ["Speed", "Potency"],
        "recommended_primaries": {3: "Speed", 5: "Protection", 6: "Protection", 7: "Potency"},
        "priority_stats": ["Speed", "Potency", "Protection", "Health"],
        "speed_floor": 260,
    },
    "DARKTROOPER": {
        "squad": "Imperial Troopers",
        "target_sets": ["Offense", "Critical Chance"],
        "recommended_primaries": {3: "Offense", 5: "Protection", 6: "Critical Damage", 7: "Offense"},
        "priority_stats": ["Offense", "Critical Chance", "Protection", "Health"],
        "speed_floor": None,
    },
}

MOD_ASSIGNMENT_PRIORITY = [
    {
        "base_id": "CAPTAINREX",
        "label": "Captain Rex",
        "reason": "best speed set first; Phoenix only works cleanly when Rex moves early",
    },
    {
        "base_id": "GREEFKARGA",
        "label": "Greef Karga",
        "reason": "next-best speed set; fast mass assist and cleanse for Bounty Hunters",
    },
    {
        "base_id": "ADMIRALPIETT",
        "label": "Admiral Piett",
        "reason": "top-end speed set for Troopers turn meter chain",
    },
    {
        "base_id": "GENERALHUX",
        "label": "General Hux",
        "reason": "fast speed set for First Order control and TM denial",
    },
    {
        "base_id": "BOSSK",
        "label": "Bossk",
        "reason": "best health and protection tank set for contract consistency",
    },
    {
        "base_id": "EMPERORPALPATINE",
        "label": "Emperor Palpatine",
        "reason": "speed and potency set for faster control in Empire",
    },
    {
        "base_id": "KYLORENUNMASKED",
        "label": "Kylo Ren (Unmasked)",
        "reason": "health-heavy tank set once Phoenix and BH priorities are covered",
    },
    {
        "base_id": "MARAJADE",
        "label": "Mara Jade",
        "reason": "premium speed set after the primary turn-meter engines are handled",
    },
]

# Mod audit: pilot-focused fleet mapping for fleet-mode recommendations.
MOD_FLEET_ASSIGNMENTS = {
    "HERASYNDULLAS3": "Rebel Fleet",
    "CHOPPERS3": "Rebel Fleet",
    "SABINEWRENS3": "Rebel Fleet",
    "BOSSK": "Executor Core",
    "BOBAFETT": "Executor Core",
    "CADBANE": "Executor Core",
    "DARTHVADER": "Empire Fleet",
    "KYLORENUNMASKED": "Finalizer",
    "KYLOREN": "Finalizer",
    "FOSITHTROOPER": "Finalizer",
    "FIRSTORDEROFFICERMALE": "Finalizer",
}

# Per-mode weighting to rank squads and fleets by stated player goal.
MOD_AUDIT_MODE_WEIGHTS = {
    "pve": {
        "squads": {
            "Phoenix": 1.2,
            "Bounty Hunters": 1.1,
            "Empire": 1.0,
            "First Order": 1.0,
            "Imperial Troopers": 1.0,
        },
        "fleets": {
            "Executor Core": 1.15,
            "Finalizer": 1.1,
            "Rebel Fleet": 1.0,
            "Empire Fleet": 1.0,
        },
    },
    "gac_offense": {
        "squads": {
            "Imperial Troopers": 1.25,
            "Bounty Hunters": 1.15,
            "Empire": 1.1,
            "Phoenix": 1.0,
            "First Order": 1.05,
        },
        "fleets": {
            "Executor Core": 1.2,
            "Finalizer": 1.15,
            "Empire Fleet": 1.05,
            "Rebel Fleet": 1.0,
        },
    },
    "gac_defense": {
        "squads": {
            "First Order": 1.2,
            "Empire": 1.1,
            "Phoenix": 1.05,
            "Bounty Hunters": 1.0,
            "Imperial Troopers": 0.95,
        },
        "fleets": {
            "Finalizer": 1.2,
            "Executor Core": 1.1,
            "Empire Fleet": 1.05,
            "Rebel Fleet": 1.0,
        },
    },
    "raid": {
        "squads": {
            "Imperial Troopers": 1.15,
            "Bounty Hunters": 1.1,
            "Empire": 1.05,
            "Phoenix": 1.0,
            "First Order": 1.0,
        },
        "fleets": {
            "Executor Core": 1.0,
            "Finalizer": 1.0,
            "Rebel Fleet": 1.0,
            "Empire Fleet": 1.0,
        },
    },
    "raid_order66": {
        "squads": {
            "Empire": 1.25,
            "Imperial Troopers": 1.2,
            "Bounty Hunters": 1.1,
            "First Order": 1.0,
            "Phoenix": 0.95,
        },
        "fleets": {
            "Empire Fleet": 1.15,
            "Executor Core": 1.1,
            "Finalizer": 1.0,
            "Rebel Fleet": 0.95,
        },
    },
    "proving_grounds": {
        "squads": {
            "Empire": 1.2,
            "Bounty Hunters": 1.15,
            "First Order": 1.1,
            "Imperial Troopers": 1.05,
            "Phoenix": 1.0,
        },
        "fleets": {
            "Executor Core": 1.1,
            "Finalizer": 1.05,
            "Empire Fleet": 1.0,
            "Rebel Fleet": 1.0,
        },
    },
}

# Per-mode unit multipliers let event-defining units rise above broad squad weighting.
MOD_AUDIT_MODE_UNIT_MULTIPLIERS = {
    "raid_order66": {
        "GRANDMOFFTARKIN": 2.0,
    },
}

# Eligibility constraints for mode-specific audits.
# Confidence values:
# - known: explicit, verified ruleset is available
# - estimated: inferred from current event/community patterns
# - unknown: no reliable ruleset mapped yet; no hard filtering applied
MOD_AUDIT_ELIGIBILITY_RULES = {
    "pve": {
        "confidence": "estimated",
        "allowed_squads": [
            "Phoenix",
            "Bounty Hunters",
            "Empire",
            "First Order",
            "Imperial Troopers",
        ],
        "allowed_fleets": [
            "Executor Core",
            "Finalizer",
            "Rebel Fleet",
            "Empire Fleet",
        ],
        "note": "PvE eligibility is broad and context-dependent; using best-estimate team pools.",
    },
    "gac_offense": {
        "confidence": "estimated",
        "allowed_squads": [
            "Phoenix",
            "Bounty Hunters",
            "Empire",
            "First Order",
            "Imperial Troopers",
        ],
        "allowed_fleets": [
            "Executor Core",
            "Finalizer",
            "Rebel Fleet",
            "Empire Fleet",
        ],
        "note": "Using best-estimate offense pools from configured squads and fleets.",
    },
    "gac_defense": {
        "confidence": "estimated",
        "allowed_squads": [
            "Phoenix",
            "Bounty Hunters",
            "Empire",
            "First Order",
            "Imperial Troopers",
        ],
        "allowed_fleets": [
            "Executor Core",
            "Finalizer",
            "Rebel Fleet",
            "Empire Fleet",
        ],
        "note": "Using best-estimate defense pools from configured squads and fleets.",
    },
    "raid": {
        "confidence": "unknown",
        "allowed_squads": [],
        "allowed_fleets": [],
        "note": "Generic raid mode does not map to one verified whitelist; using best estimates without hard exclusions.",
    },
    "raid_order66": {
        "confidence": "estimated",
        "allowed_squads": [
            "Empire",
            "Imperial Troopers",
            "Bounty Hunters",
            "First Order",
        ],
        "allowed_fleets": [],
        "note": "Order 66 restrictions are currently estimated; fleet entries are treated as ineligible.",
    },
    "proving_grounds": {
        "confidence": "estimated",
        "allowed_squads": [
            "Phoenix",
            "Bounty Hunters",
            "Empire",
            "First Order",
            "Imperial Troopers",
        ],
        "allowed_fleets": [],
        "note": "Proving Grounds is treated as squad-only in best-effort eligibility.",
    },
}
