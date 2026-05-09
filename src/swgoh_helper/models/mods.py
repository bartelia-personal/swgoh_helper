"""Pydantic models for mod audit analysis."""

from typing import Optional

from pydantic import BaseModel, Field


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
    rarity: int
    gear_level: int
    relic_tier: int
    speed: Optional[int] = None
    equipped_mod_count: int = 0
    current_sets: list[str] = Field(default_factory=list)
    recommended_sets: list[str] = Field(default_factory=list)
    findings: list[ModAuditFinding] = Field(default_factory=list)
    priority_score: int = 0


class ModAuditReport(BaseModel):
    player_name: str
    ally_code: int
    total_mods: int
    profiled_units_owned: int
    audited_units: list[ModAuditUnitResult] = Field(default_factory=list)