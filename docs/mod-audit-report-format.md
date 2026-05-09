# Mod Audit Report Format

Use this structure when saving a player-facing mod audit report.

## Header

- Player: <player name>
- Ally Code: <ally code>
- Generated: <YYYY-MM-DD>
- Source: <cache or live API source>

## Summary

- Profiled units owned: <count>
- Equipped mods returned by API/cache: <count>
- Caveat: <partial-audit or full-audit note>

## Best Mod Sets First

1. <unit> -> <set list>
   Why: <short reason tied to squad function>
2. <unit> -> <set list>
   Why: <short reason tied to squad function>
3. <unit> -> <set list>
   Why: <short reason tied to squad function>
4. <unit> -> <set list>
   Why: <short reason tied to squad function>
5. <unit> -> <set list>
   Why: <short reason tied to squad function>
6. <unit> -> <set list>
   Why: <short reason tied to squad function>

## Top Upgrade Targets

1. <unit>
   Status: <R# or G#/stars>, Speed <value>, Mods <count>/6
   Sets: current <current sets> | target <target sets>
   Findings:
   - <highest-signal gap>
   - <speed or primary mismatch>
   - <missing set>
   - <missing set or slot>

2. <repeat unit block as needed>

Guidelines:

- Keep the best-mod-sets-first section limited to six assignments.
- Keep each "Why" line tied to squad function, not generic stat advice.
- Call out partial data explicitly when equipped mod coverage from the API/cache is sparse.
- Preserve the top-upgrade section as a raw audit, even if the summary priority order differs.