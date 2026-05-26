"""Account-wide squad recommendations with concrete memberships and action plans."""

from collections import defaultdict
import re

from .mod_recommender import ModRecommender

SUPPORTED_SQUAD_MODES = (
    "pve",
    "gac_offense",
    "gac_defense",
    "raid",
    "raid_order66",
    "proving_grounds",
)


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
        ranked_squads = sorted(
            aggregate["squad_scores"].items(), key=lambda item: -item[1]
        )[:top_squads]

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
        return {
            "squad_scores": squad_scores,
            "unit_scores": unit_scores,
            "unit_names": unit_names,
            "unit_squads": unit_squads,
            "findings": findings,
        }

    def _squad_membership_lines(self, ranked_squads: list, aggregate: dict) -> list[str]:
        lines: list[str] = []
        profile_counts = self._profile_counts_by_squad()
        members = self._owned_members_by_squad(aggregate)
        for index, (squad, score) in enumerate(ranked_squads, 1):
            squad_members = members.get(squad, [])
            member_text = ", ".join(squad_members) if squad_members else "none"
            owned = len(squad_members)
            total = profile_counts.get(squad, owned)
            lines.append(f"{index}. {squad} (priority {score})")
            lines.append(f"   Membership: {member_text}")
            lines.append(f"   Owned profiled members: {owned}/{total}")
        lines.append("")
        return lines

    def _profile_counts_by_squad(self) -> dict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int)
        for profile in self.recommender.profiles.values():
            counts[profile.squad] += 1
        return dict(counts)

    def _owned_members_by_squad(self, aggregate: dict) -> dict[str, list[str]]:
        by_squad: defaultdict[str, list[tuple[str, int]]] = defaultdict(list)
        for base_id, name in aggregate["unit_names"].items():
            squad = aggregate["unit_squads"][base_id]
            score = aggregate["unit_scores"][base_id]
            by_squad[squad].append((name, score))
        output: dict[str, list[str]] = {}
        for squad, members in by_squad.items():
            ordered = sorted(members, key=lambda item: (-item[1], item[0]))
            output[squad] = [name for name, _ in ordered]
        return output

    def _action_plan_lines(
        self,
        ranked_squads: list,
        aggregate: dict,
        plan_steps: int,
    ) -> list[str]:
        top_squads = {name for name, _ in ranked_squads}
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
