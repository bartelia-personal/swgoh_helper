"""Account-wide squad recommendations with concrete memberships and action plans."""

from collections import defaultdict
import re

from .mod_recommender import ModRecommender
from .constants import MOD_AUDIT_MODE_WEIGHTS

SUPPORTED_SQUAD_MODES = (
    "pve",
    "gac_offense",
    "gac_defense",
    "raid",
    "raid_order66",
    "proving_grounds",
)
MAX_SQUAD_SIZE = 5


class SquadPlanAdvisor:
    """Build account-level squad recommendations from mod audit data."""

    def __init__(self, recommender: ModRecommender | None = None):
        self.recommender = recommender or ModRecommender()

    def recommend_for_account(
        self,
        player,
        top_squads: int = 5,
        plan_steps: int = 10,
        eligibility: str = "best_effort",
    ) -> str:
        reports = self._build_mode_reports(player, eligibility)
        if not reports:
            return "No squad data available."

        aggregate = self._aggregate_scores(reports)
        ranked_squads = self._rank_squads(aggregate, top_squads)

        lines = [
            f"Squad Plan for {player.data.name}",
            f"Ally Code: {player.data.ally_code}",
            f"Modes analyzed: {', '.join(SUPPORTED_SQUAD_MODES)}",
            "",
            "Recommended squads and exact memberships",
        ]
        lines.extend(self._squad_membership_lines(ranked_squads, aggregate))
        lines.extend(self._action_plan_lines(ranked_squads, aggregate, plan_steps))
        return "\n".join(lines)

    def _build_mode_reports(self, player, eligibility: str) -> list:
        reports = []
        for mode in SUPPORTED_SQUAD_MODES:
            reports.append(
                self.recommender.analyze(
                    player,
                    goal_mode=mode,
                    focus="squads",
                    eligibility=eligibility,
                )
            )
        return reports

    def _aggregate_scores(self, reports: list) -> dict:
        squad_scores: defaultdict[str, int] = defaultdict(int)
        unit_scores: defaultdict[str, int] = defaultdict(int)
        unit_names: dict[str, str] = {}
        unit_squads: dict[str, str] = {}
        findings: defaultdict[str, list[str]] = defaultdict(list)
        for report in reports:
            for unit in report.audited_units:
                squad_scores[unit.squad] += unit.priority_score
                unit_scores[unit.base_id] += unit.priority_score
                unit_names[unit.base_id] = unit.unit_name
                unit_squads[unit.base_id] = unit.squad
                findings[unit.base_id].extend([f.message for f in unit.findings])
        unit_completion = {
            base_id: self._completion_from_findings(messages)
            for base_id, messages in findings.items()
        }
        return {
            "squad_scores": squad_scores,
            "unit_scores": unit_scores,
            "unit_names": unit_names,
            "unit_squads": unit_squads,
            "findings": findings,
            "unit_completion": unit_completion,
        }

    def _rank_squads(self, aggregate: dict, top_squads: int) -> list[dict]:
        members = self._owned_members_by_squad(aggregate)
        rankings: list[dict] = []
        for squad, members_with_score in members.items():
            ordered = sorted(
                members_with_score,
                key=lambda item: (
                    -aggregate["unit_completion"].get(item[0], 0),
                    -item[1],
                ),
            )
            primary_ids = [base_id for base_id, _ in ordered[:MAX_SQUAD_SIZE]]
            owned_count = len(ordered)
            if not primary_ids:
                continue
            average_completion = sum(
                aggregate["unit_completion"].get(base_id, 0)
                for base_id in primary_ids
            ) / len(primary_ids)
            ownership_factor = min(1.0, owned_count / MAX_SQUAD_SIZE)
            completion = round(average_completion * ownership_factor, 1)
            potential = self._squad_potential(squad)
            rank_score = round(completion * potential, 1)
            rankings.append(
                {
                    "squad": squad,
                    "rank_score": rank_score,
                    "completion": completion,
                    "potential": potential,
                    "owned_count": owned_count,
                }
            )
        rankings.sort(key=lambda item: (-item["rank_score"], -item["completion"], item["squad"]))
        return rankings[:top_squads]

    def _squad_membership_lines(self, ranked_squads: list[dict], aggregate: dict) -> list[str]:
        lines: list[str] = []
        profile_counts = self._profile_counts_by_squad()
        members = self._owned_members_by_squad(aggregate)
        for index, ranking in enumerate(ranked_squads, 1):
            squad = ranking["squad"]
            squad_members = members.get(squad, [])
            ordered = sorted(
                squad_members,
                key=lambda item: (
                    -aggregate["unit_completion"].get(item[0], 0),
                    -item[1],
                ),
            )
            primary = ordered[:MAX_SQUAD_SIZE]
            alternates = ordered[MAX_SQUAD_SIZE:]
            primary_text = "; ".join(
                aggregate["unit_names"].get(base_id, base_id)
                for base_id, _ in primary
            )
            if not primary_text:
                primary_text = "none"
            owned = ranking["owned_count"]
            total = profile_counts.get(squad, owned)
            lines.append(f"{index}. {squad} (rank {ranking['rank_score']})")
            lines.append(f"   Primary 5: {primary_text}")
            if alternates:
                alt_text = "; ".join(
                    aggregate["unit_names"].get(base_id, base_id)
                    for base_id, _ in alternates
                )
                lines.append(f"   Alternates: {alt_text}")
            lines.append(f"   Owned profiled members: {owned}/{total}")
            lines.append(f"   Completion: {ranking['completion']}%")
            lines.append(f"   Potential: {ranking['potential']}")
        lines.append("")
        return lines

    def _profile_counts_by_squad(self) -> dict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int)
        for profile in self.recommender.profiles.values():
            counts[profile.squad] += 1
        return dict(counts)

    def _owned_members_by_squad(self, aggregate: dict) -> dict[str, list[tuple[str, int]]]:
        by_squad: defaultdict[str, list[tuple[str, int]]] = defaultdict(list)
        for base_id in aggregate["unit_names"]:
            squad = aggregate["unit_squads"][base_id]
            score = aggregate["unit_scores"][base_id]
            by_squad[squad].append((base_id, score))
        return dict(by_squad)

    def _action_plan_lines(
        self,
        ranked_squads: list[dict],
        aggregate: dict,
        plan_steps: int,
    ) -> list[str]:
        top_squads = {entry["squad"] for entry in ranked_squads}
        candidates = self._ranked_unit_ids_for_top_squads(top_squads, aggregate)
        actions: list[str] = []
        seen: set[str] = set()
        for base_id in candidates:
            unit_name = aggregate["unit_names"][base_id]
            for message in aggregate["findings"][base_id]:
                action = self._finding_to_action(unit_name, message)
                if action and action not in seen:
                    seen.add(action)
                    actions.append(action)
                    break
            if len(actions) >= plan_steps:
                break
        lines = ["Account improvement plan (Do 1-N)"]
        for index, action in enumerate(actions, 1):
            lines.append(f"Do {index}: {action}")
        if not actions:
            lines.append("Do 1: Continue improving speed and complete missing sets on core squads.")
        return lines

    def _ranked_unit_ids_for_top_squads(self, top_squads: set[str], aggregate: dict) -> list[str]:
        ranked = [
            (base_id, score)
            for base_id, score in aggregate["unit_scores"].items()
            if aggregate["unit_squads"].get(base_id) in top_squads
        ]
        return [base_id for base_id, _ in sorted(ranked, key=lambda item: -item[1])]

    def _finding_to_action(self, unit_name: str, message: str) -> str | None:
        speed = re.match(r"Speed\s+(\d+)\s+is below the\s+(\d+)\s+target\.", message)
        if speed:
            return f"Raise {unit_name} speed from {speed.group(1)} to at least {speed.group(2)}."
        missing = re.match(r"Missing\s+(\d+)\s+equipped mods\.", message)
        if missing:
            return f"Equip {missing.group(1)} missing mods on {unit_name}."
        missing_set = re.match(r"Missing recommended\s+(.+)\s+set\.", message)
        if missing_set:
            return f"Complete a {missing_set.group(1)} set on {unit_name}."
        wrong_primary = re.match(r"(.+) has (.+) primary; target is (.+)\.", message)
        if wrong_primary:
            return f"Swap {wrong_primary.group(1)} primary on {unit_name} to {wrong_primary.group(3)}."
        missing_primary = re.match(r"(.+) is missing; target primary is (.+)\.", message)
        if missing_primary:
            return f"Equip {missing_primary.group(1)} on {unit_name} with {missing_primary.group(2)} primary."
        return None

    def _completion_from_findings(self, findings: list[str]) -> float:
        gap_score = 0
        for message in set(findings):
            missing_mods = re.match(r"Missing\s+(\d+)\s+equipped mods\.", message)
            if missing_mods:
                gap_score += int(missing_mods.group(1)) * 12
                continue
            missing_set = re.match(r"Missing recommended\s+(.+)\s+set\.", message)
            if missing_set:
                gap_score += 8
                continue
            wrong_primary = re.match(r"(.+) has (.+) primary; target is (.+)\.", message)
            if wrong_primary:
                gap_score += 6
                continue
            missing_primary = re.match(r"(.+) is missing; target primary is (.+)\.", message)
            if missing_primary:
                gap_score += 6
                continue
            speed = re.match(r"Speed\s+(\d+)\s+is below the\s+(\d+)\s+target\.", message)
            if speed:
                current = int(speed.group(1))
                target = int(speed.group(2))
                shortfall = max(0, target - current)
                gap_score += min(25, max(8, shortfall // 4))
        return max(0.0, round(100 - min(100, gap_score), 1))

    def _squad_potential(self, squad: str) -> float:
        potential = 0.0
        for mode in SUPPORTED_SQUAD_MODES:
            mode_config = MOD_AUDIT_MODE_WEIGHTS.get(mode, {})
            potential += mode_config.get("squads", {}).get(squad, 0.0)
        # Fallback keeps custom or ad-hoc squads rankable in tests and local profiles.
        if potential == 0.0:
            return 1.0
        return round(potential, 2)
