"""Target-focused farming advisor for characters and ships."""

import json
from pathlib import Path
from typing import Any, Optional

from .constants import MOD_AUDIT_PROFILES


class FarmFocusAdvisor:
    """Recommend campaign energy nodes for one target and current account context."""

    def __init__(self):
        data_dir = Path(__file__).resolve().parents[2] / "data"
        self.campaign_nodes = self._load_json(data_dir / "campaign_nodes.json")
        self.character_farms = self._load_json(data_dir / "character_farms.json")

    def recommend_for_target(self, player, units_data, target_query: str, top_n: int = 8) -> str:
        target_unit = self._resolve_target(target_query, units_data)
        player_by_id = {unit.data.base_id: unit.data for unit in player.units}
        target_player_unit = player_by_id.get(target_unit.base_id)
        unmaxed_names = {
            unit.data.name for unit in player.units if getattr(unit.data, "rarity", 7) < 7
        }
        candidates = self._build_node_candidates(
            target_name=target_unit.name,
            target_unit=target_player_unit,
            unmaxed_names=unmaxed_names,
            top_n=top_n,
        )
        return self._format_report(
            player_name=player.data.name,
            ally_code=player.data.ally_code,
            target_name=target_unit.name,
            target_unit=target_player_unit,
            candidates=candidates,
            target_base_id=target_unit.base_id,
            top_n=top_n,
        )

    def _load_json(self, path: Path) -> dict[str, Any]:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _resolve_target(self, target_query: str, units_data):
        query = target_query.strip().casefold()
        units = units_data.data
        exact = [unit for unit in units if unit.name.casefold() == query]
        if exact:
            return exact[0]
        partial = [unit for unit in units if query in unit.name.casefold()]
        if partial:
            return sorted(partial, key=lambda unit: len(unit.name))[0]
        raise ValueError(f"Could not find target '{target_query}'.")

    def _build_node_candidates(
        self,
        target_name: str,
        target_unit,
        unmaxed_names: set[str],
        top_n: int,
    ) -> list[dict[str, Any]]:
        sources = self.character_farms.get("characters", {}).get(target_name, {})
        nodes = sources.get("campaign_nodes", [])
        if not nodes:
            nodes = self._search_nodes_for_target(target_name)
        candidates = []
        for node in nodes:
            details = self._campaign_node(node["campaign"], node["node"])
            if details is None:
                continue
            candidates.append(self._score_node(node, details, target_name, target_unit, unmaxed_names))
        if not candidates:
            candidates = self._fallback_candidates(target_unit, unmaxed_names)
        candidates.sort(key=lambda item: (-item["score"], item["energy_cost"], item["label"]))
        return candidates[:top_n]

    def _search_nodes_for_target(self, target_name: str) -> list[dict[str, Any]]:
        results = []
        for campaign, campaign_data in self.campaign_nodes.get("campaigns", {}).items():
            for node_id, details in campaign_data.get("nodes", {}).items():
                if target_name in details.get("character_shards", []) or target_name in details.get("ship_shards", []):
                    results.append(
                        {
                            "campaign": campaign,
                            "node": node_id,
                            "energy_cost": details.get("energy_cost", 0),
                            "energy_type": details.get("energy_type", "unknown"),
                            "daily_limit": details.get("daily_limit"),
                        }
                    )
        return results

    def _fallback_candidates(self, target_unit, unmaxed_names: set[str]) -> list[dict[str, Any]]:
        candidates = []
        include_signal = self._needs_signal_data(target_unit)
        for campaign, campaign_data in self.campaign_nodes.get("campaigns", {}).items():
            for node_id, details in campaign_data.get("nodes", {}).items():
                overlap = self._overlap_targets(details, "", unmaxed_names)
                has_signal = "Signal Data" in details.get("special_drops", [])
                if not overlap and not (include_signal and has_signal):
                    continue
                node = {
                    "campaign": campaign,
                    "node": node_id,
                    "energy_cost": details.get("energy_cost", 0),
                    "energy_type": details.get("energy_type", "unknown"),
                    "daily_limit": details.get("daily_limit"),
                }
                candidate = self._score_node(node, details, "", target_unit, unmaxed_names)
                candidate["reasons"].append(
                    "Fallback pick: no direct shard/blueprint node mapping for target"
                )
                if has_signal:
                    candidate["reasons"].append("Signal data fallback for relic progression")
                candidates.append(candidate)
        return candidates

    def _campaign_node(self, campaign: str, node_id: str) -> Optional[dict[str, Any]]:
        campaigns = self.campaign_nodes.get("campaigns", {})
        campaign_data = campaigns.get(campaign, {})
        return campaign_data.get("nodes", {}).get(node_id)

    def _score_node(
        self,
        node: dict[str, Any],
        details: dict[str, Any],
        target_name: str,
        target_unit,
        unmaxed_names: set[str],
    ) -> dict[str, Any]:
        label = f"{node['campaign']} {node['node']}"
        overlap = self._overlap_targets(details, target_name, unmaxed_names)
        score = 50 + (len(overlap) * 12)
        score += min(len(details.get("gear_drops", [])), 3) * 3
        reasons = []
        if overlap:
            reasons.append(f"Overlap with account farms: {', '.join(overlap[:3])}")
        if details.get("special_drops") and self._needs_signal_data(target_unit):
            if "Signal Data" in details.get("special_drops", []):
                score += 14
                reasons.append("Signal Data support for relic progression")
        if details.get("daily_limit") == 5:
            score += 4
            reasons.append("Hard-node shard source with daily attempts")
        if details.get("gear_drops"):
            reasons.append("Includes gear drops while farming shards")
        if not reasons:
            reasons.append("Direct shard or blueprint progress for target")
        return {
            "label": label,
            "score": score,
            "energy_cost": details.get("energy_cost", node.get("energy_cost", 0)),
            "energy_type": details.get("energy_type", node.get("energy_type", "unknown")),
            "daily_limit": details.get("daily_limit"),
            "reasons": reasons,
        }

    def _needs_signal_data(self, target_unit) -> bool:
        if target_unit is None:
            return False
        relic = getattr(target_unit, "relic_tier_or_minus_one", -1)
        return relic < 9

    def _overlap_targets(
        self,
        details: dict[str, Any],
        target_name: str,
        unmaxed_names: set[str],
    ) -> list[str]:
        shard_targets = details.get("character_shards", []) + details.get("ship_shards", [])
        return [
            name
            for name in shard_targets
            if name != target_name and name in unmaxed_names
        ]

    def _format_report(
        self,
        player_name: str,
        ally_code: int,
        target_name: str,
        target_unit,
        candidates: list[dict[str, Any]],
        target_base_id: str,
        top_n: int,
    ) -> str:
        status = self._target_status(target_unit)
        lines = [
            f"Target Farm Advisor for {player_name}",
            f"Ally Code: {ally_code}",
            f"Target: {target_name}",
            f"Current progress: {status}",
            "",
            f"Best campaign energy nodes (top {top_n})",
        ]
        if self._has_fallback_candidates(candidates):
            lines.append(
                "Estimate note: no direct shard/blueprint node mapping was found for this target; showing best account-overlap fallback nodes."
            )
            lines.append("")
        if not candidates:
            lines.append("No campaign node mapping found for this target in data/character_farms.json.")
            lines.append("Fallback suggestions also found no strong account-overlap or signal-data nodes.")
        for index, candidate in enumerate(candidates, 1):
            limit = candidate["daily_limit"] if candidate["daily_limit"] is not None else "none"
            lines.append(
                f"{index}. {candidate['label']} | score {candidate['score']} | {candidate['energy_type']} energy {candidate['energy_cost']} | daily limit {limit}"
            )
            for reason in candidate["reasons"][:2]:
                lines.append(f"   - {reason}")
        lines.append("")
        lines.extend(self._mod_farming_notes(target_base_id))
        return "\n".join(lines)

    def _target_status(self, target_unit) -> str:
        if target_unit is None:
            return "Not owned"
        relic = getattr(target_unit, "relic_tier_or_minus_one", -1)
        if relic >= 0:
            return f"R{relic}, {target_unit.rarity}*"
        return f"G{target_unit.gear_level}, {target_unit.rarity}*"

    def _mod_farming_notes(self, base_id: str) -> list[str]:
        profile = MOD_AUDIT_PROFILES.get(base_id)
        if profile is None:
            return ["Mod farming note: no mod-audit profile is configured for this target yet."]
        sets = ", ".join(profile.get("target_sets", []))
        return [
            f"Mod farming note: target sets are {sets}.",
            "Campaign node data currently does not include dedicated mod-challenge nodes, so mod battle routing is estimated.",
        ]

    def _has_fallback_candidates(self, candidates: list[dict[str, Any]]) -> bool:
        for candidate in candidates:
            for reason in candidate.get("reasons", []):
                if reason.startswith("Fallback pick"):
                    return True
        return False