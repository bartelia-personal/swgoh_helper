"""Pydantic models for mod audit analysis."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


ModAuditGoalMode = Literal[
    "pve",
    "gac_offense",
    "gac_defense",
    "raid",
    "raid_order66",
    "proving_grounds",
]
ModAuditFocus = Literal["squads", "fleets", "both"]
ModAuditEligibility = Literal["off", "best_effort"]


class ModAuditProfile(BaseModel):
    squad: str
    target_sets: list[str]
    recommended_primaries: dict[int, str]
    priority_stats: list[str]
    speed_floor: Optional[int] = None


class ModAuditFinding(BaseModel):
    message: str
    severity: int


class ModAuditUnitResult(BaseModel):
    unit_name: str
    base_id: str
    squad: str
    fleet: Optional[str] = None
    rarity: int
    gear_level: int
    relic_tier: int
    speed: Optional[int] = None
    equipped_mod_count: int = 0
    current_sets: list[str] = Field(default_factory=list)
    recommended_sets: list[str] = Field(default_factory=list)
    findings: list[ModAuditFinding] = Field(default_factory=list)
    priority_score: int = 0
    mode_weight: float = 1.0


class ModAuditReport(BaseModel):
    player_name: str
    ally_code: int
    goal_mode: ModAuditGoalMode = "pve"
    focus: ModAuditFocus = "both"
    eligibility: ModAuditEligibility = "best_effort"
    eligibility_confidence: str = "estimated"
    eligibility_note: Optional[str] = None
    excluded_ineligible_count: int = 0
    total_mods: int
    profiled_units_owned: int
    audited_units: list[ModAuditUnitResult] = Field(default_factory=list)