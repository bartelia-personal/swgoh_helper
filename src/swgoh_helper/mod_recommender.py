"""Audit equipped mods for a prioritized set of squads."""

from collections import Counter, defaultdict

from .constants import (
    MOD_ASSIGNMENT_PRIORITY,
    MOD_AUDIT_PROFILES,
    MOD_SET_NAMES,
    MOD_SET_SIZES,
    MOD_SLOT_NAMES,
)
from .models import ModAuditFinding, ModAuditProfile, ModAuditReport, ModAuditUnitResult

SPEED_STAT_ID = "5"


class ModRecommender:
    def __init__(self, profiles: dict[str, dict] | None = None):
        source = profiles or MOD_AUDIT_PROFILES
        self.profiles = {
            base_id: ModAuditProfile(**profile) for base_id, profile in source.items()
        }

    def analyze(self, player) -> ModAuditReport:
        unit_lookup = {unit.data.base_id: unit.data for unit in player.units}
        mods_by_character = self._group_mods(player.mods)
        audited_units = []
        for base_id, profile in self.profiles.items():
            unit = unit_lookup.get(base_id)
            if unit is None:
                continue
            audited_units.append(self._analyze_unit(unit, profile, mods_by_character))
        audited_units.sort(key=lambda item: (-item.priority_score, item.unit_name))
        return ModAuditReport(
            player_name=player.data.name,
            ally_code=player.data.ally_code,
            total_mods=len(player.mods),
            profiled_units_owned=len(audited_units),
            audited_units=audited_units,
        )

    def format_report(self, report: ModAuditReport, top_n: int = 10) -> str:
        lines = [
            f"Mod Audit for {report.player_name}",
            f"Ally Code: {report.ally_code}",
            f"Profiled units owned: {report.profiled_units_owned}",
            f"Equipped mods returned by API/cache: {report.total_mods}",
            "",
        ]
        if report.total_mods < report.profiled_units_owned * 4:
            lines.append("Note: equipped mod data looks incomplete, so treat this as a partial audit.")
            lines.append("")
        if not report.audited_units:
            lines.append("No profiled units found in this roster.")
            return "\n".join(lines)
        lines.extend(self._assignment_lines(report.audited_units))
        lines.append("Top upgrade targets")
        for index, result in enumerate(report.audited_units[:top_n], 1):
            lines.extend(self._format_unit_block(index, result))
        return "\n".join(lines)

    def _assignment_lines(self, audited_units: list[ModAuditUnitResult]) -> list[str]:
        assignments = self._priority_assignments(audited_units)
        if not assignments:
            return []
        lines = ["Best mod sets first"]
        for index, (config, result) in enumerate(assignments, 1):
            target_sets = ", ".join(result.recommended_sets)
            lines.append(
                f"{index}. {config['label']} -> {target_sets}"
            )
            lines.append(f"   Why: {config['reason']}")
        lines.append("")
        return lines

    def _priority_assignments(
        self, audited_units: list[ModAuditUnitResult]
    ) -> list[tuple[dict[str, str], ModAuditUnitResult]]:
        by_base_id = {result.base_id: result for result in audited_units}
        assignments = []
        for config in MOD_ASSIGNMENT_PRIORITY:
            result = by_base_id.get(config["base_id"])
            if result is None:
                continue
            assignments.append((config, result))
        return assignments[:6]

    def _group_mods(self, mods) -> dict[str, list]:
        grouped = defaultdict(list)
        for mod in mods:
            if mod.character:
                grouped[mod.character].append(mod)
        return grouped

    def _analyze_unit(self, unit, profile: ModAuditProfile, mods_by_character: dict[str, list]) -> ModAuditUnitResult:
        equipped_mods = mods_by_character.get(unit.base_id, [])
        current_sets = self._completed_sets(equipped_mods, unit.mod_set_ids)
        findings = self._collect_findings(unit, profile, equipped_mods, current_sets)
        score = sum(finding.severity for finding in findings)
        return ModAuditUnitResult(
            unit_name=unit.name,
            base_id=unit.base_id,
            squad=profile.squad,
            rarity=unit.rarity,
            gear_level=unit.gear_level,
            relic_tier=unit.relic_tier_or_minus_one,
            speed=self._speed(unit),
            equipped_mod_count=len(equipped_mods),
            current_sets=current_sets,
            recommended_sets=profile.target_sets,
            findings=findings,
            priority_score=score,
        )

    def _completed_sets(self, equipped_mods: list, fallback_set_ids: list[str]) -> list[str]:
        set_ids = [mod.set for mod in equipped_mods] if equipped_mods else fallback_set_ids
        counts = Counter(MOD_SET_NAMES.get(set_id, f"Set {set_id}") for set_id in set_ids)
        completed_sets = []
        for set_name, count in counts.items():
            set_size = MOD_SET_SIZES.get(set_name, 2)
            completed_sets.extend([set_name] * (count // set_size))
        return sorted(completed_sets)

    def _collect_findings(self, unit, profile: ModAuditProfile, equipped_mods: list, current_sets: list[str]) -> list[ModAuditFinding]:
        findings = []
        findings.extend(self._missing_mod_findings(len(equipped_mods)))
        findings.extend(self._set_findings(profile.target_sets, current_sets))
        findings.extend(self._primary_findings(profile, equipped_mods))
        speed = self._speed(unit)
        if profile.speed_floor and speed is not None and speed < profile.speed_floor:
            findings.append(ModAuditFinding(message=f"Speed {speed} is below the {profile.speed_floor} target.", severity=20))
        return sorted(findings, key=lambda item: -item.severity)

    def _missing_mod_findings(self, equipped_count: int) -> list[ModAuditFinding]:
        if equipped_count >= 6:
            return []
        missing = 6 - equipped_count
        severity = 15 + (missing * 5)
        return [ModAuditFinding(message=f"Missing {missing} equipped mods.", severity=severity)]

    def _set_findings(self, target_sets: list[str], current_sets: list[str]) -> list[ModAuditFinding]:
        findings = []
        remaining = Counter(target_sets)
        for set_name in current_sets:
            if remaining[set_name] > 0:
                remaining[set_name] -= 1
        for set_name, missing_count in remaining.items():
            for _ in range(missing_count):
                findings.append(ModAuditFinding(message=f"Missing recommended {set_name} set.", severity=12))
        return findings

    def _primary_findings(self, profile: ModAuditProfile, equipped_mods: list) -> list[ModAuditFinding]:
        by_slot = {mod.slot: mod for mod in equipped_mods}
        findings = []
        for slot, expected in profile.recommended_primaries.items():
            mod = by_slot.get(slot)
            slot_name = MOD_SLOT_NAMES.get(slot, f"Slot {slot}")
            if mod is None:
                findings.append(ModAuditFinding(message=f"{slot_name} is missing; target primary is {expected}.", severity=8))
                continue
            actual = mod.primary_stat.name
            if actual != expected:
                findings.append(ModAuditFinding(message=f"{slot_name} has {actual} primary; target is {expected}.", severity=8))
        return findings

    def _speed(self, unit) -> int | None:
        speed = unit.stats.get(SPEED_STAT_ID)
        if speed is None:
            return None
        return int(round(speed))

    def _format_unit_block(self, index: int, result: ModAuditUnitResult) -> list[str]:
        current = ", ".join(result.current_sets) if result.current_sets else "none"
        target = ", ".join(result.recommended_sets)
        status = self._unit_status(result)
        lines = [
            f"{index}. {result.unit_name} ({result.squad})",
            f"   Status: {status}, Speed {result.speed if result.speed is not None else 'unknown'}, Mods {result.equipped_mod_count}/6",
            f"   Sets: current {current} | target {target}",
        ]
        for finding in result.findings[:4]:
            lines.append(f"   - {finding.message}")
        lines.append("")
        return lines

    def _unit_status(self, result: ModAuditUnitResult) -> str:
        if result.relic_tier >= 0:
            return f"R{result.relic_tier}"
        return f"G{result.gear_level}/{result.rarity}*"