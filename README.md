# SWGOH Helper

Tools for analyzing Star Wars Galaxy of Heroes data via the SWGOH.gg API.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- SWGOH.gg API key

## Setup

1. Install uv (if not already installed):
   ```powershell
   pip install uv
   ```

2. Sync dependencies:
   ```powershell
   uv sync
   ```

3. Create a `.env` file with your API key:
   ```
   SWGOH_API_KEY=your_api_key_here
   ```
NOTE:
You can obtain an API key by 
1. Creating an account with https://swgoh.gg/
1. Under your profile, select manage api applications
1. Add a new application for this helper. 
   - This process will take a few days for SWGOH to approve

## Usage

### Kyrotech Analysis

Analyze a player's roster for Kyrotech gear requirements (current gear → G13):

```powershell
uv run kyrotech <ally_code>
```

Example:
```powershell
uv run kyrotech 123-456-789
```

### ROTE Platoon Analysis

Analyze guild coverage for Rise of the Empire Territory Battle platoon requirements:

```powershell
uv run rote-platoon <ally_code>
```

By default, this now prints only the `gaps` view.

Choose a specific output format:

```powershell
uv run rote-platoon 123-456-789 --output-format gaps
uv run rote-platoon 123-456-789 --output-format coverage
uv run rote-platoon 123-456-789 --output-format owners
uv run rote-platoon 123-456-789 --output-format mine
uv run rote-platoon 123-456-789 --output-format planets --planets DS1,N1,LS1
uv run rote-platoon 123-456-789 --output-format limited
uv run rote-platoon 123-456-789 --output-format all
```

Optionally limit analysis to a specific phase:
```powershell
uv run rote-platoon 123-456-789 --max-phase 4
```

Show every qualifying owner for each platoon requirement, grouped by territory:
```powershell
uv run rote-platoon 123-456-789 --max-phase 4 --output-format owners
```

Valid phases: `1`, `2`, `3`, `3b`, `4`, `4b`, `5`, `5b`, `6`

**Output formats:**
- `gaps` (default): critical gaps + limited availability units
- `coverage`: territory coverage summary
- `owners`: qualifying owners for each requirement, grouped by territory
- `mine`: planet-centric list of requirements you can cover, with limited-availability callouts
- `planets`: aggregate required units across selected planet IDs, showing `need` vs `guild has` at required tier
- `limited`: per-member count of unique limited-availability character requirements
- `all`: coverage + gaps

**Optional flags:**
- `--ignore-players` excludes players from analysis by name or ally code (supports `123456789` or `123-456-789`)
- `--planets` filters by up to 3 identifiers like `DS1`, `LS1`, `N1`

Farming recommendations have moved to `rote-farm`.

### Limited Availability Member List

List all guild members with counts of unique limited-availability ROTE platoon characters:

```powershell
uv run rote-limited <ally_code>
```

Options:

```powershell
uv run rote-limited 123-456-789 --max-phase 4
uv run rote-limited 123-456-789 --refresh
uv run rote-limited 123-456-789 --ignore-players "Name One,Name Two"
```

### Bonus Zone Readiness Analysis

Compare guild readiness for Zeffo vs Mandalore bonus zones in Rise of the Empire TB:

```powershell
uv run pytest test/test_bonus_zone_readiness.py -v -s
```

**What it analyzes:**
- Current qualifying player count vs unlock threshold (Zeffo: 30/30, Mandalore: 25/25)
- "Distance" to qualify for each near-qualifying player using the same weighted farming model:
   - relic upgrade cost weights from `data/relic_costs.json`
   - `+2.0` per gear level needed to reach G13
   - `+5.0` per missing star
- Total guild farming effort to fill the gap
- Quick wins (players within distance < 5)

**Mandalore unlock chain (factored into distance calculations):**
- Bo-Katan (Mand'alor) requires R7: Kelleran Beq, Paz Vizsla, IG-12 & Grogu, Beskar Mando
- Beskar Mando requires 7★ G12: Mando, Greef Karga, Cara Dune, IG-11, Kuiil

**Output includes:**
- Officer briefing with priority player lists
- Comparison summary (which zone is closer to unlock)
- Quick wins for each zone

See [Bonus Zone Analysis](docs/bonus_zone_analysis.md) for the latest results.

### Personal Farm Recommendations

Get personalized farming recommendations based on your guild's platoon gaps:

```powershell
uv run rote-farm <ally_code>
```

Options:
```powershell
uv run rote-farm 123-456-789 --max-phase 4
uv run rote-farm 123-456-789 --max-recommendations 10
uv run rote-farm 123-456-789 --include-unowned
```

### Journey Guide Path Advisor

Rank the best Journey Guide unlock paths for your roster:

```powershell
uv run journey-guide <ally_code>
```

Options:
```powershell
uv run journey-guide 123-456-789 --top 5
uv run journey-guide 123-456-789 --target "Jedi Master Kenobi"
uv run journey-guide 123-456-789 --owned-only
```

Notes:
- Journey Guide requirements are loaded from `data/journey_guide_requirements.json`.
- Update that file any time requirements change in-game.

### Mod Audit

Audit equipped mods on your highest-priority squads and rank the biggest gaps:

```powershell
uv run mod-audit <ally_code>
```

Options:
```powershell
uv run mod-audit 123-456-789 --top 8
uv run mod-audit 123-456-789 --mode gac_offense --focus squads
uv run mod-audit 123-456-789 --mode proving_grounds --focus fleets
uv run mod-audit 123-456-789 --mode raid_order66 --focus both
uv run mod-audit 123-456-789 --mode raid_order66 --focus both --eligibility best_effort
uv run mod-audit 123-456-789 --mode raid --focus both --eligibility off
```

Recommended command recipes:
```powershell
# Daily balanced check
uv run mod-audit 123-456-789 --mode pve --focus both --top 10

# GAC lock-in pass
uv run mod-audit 123-456-789 --mode gac_offense --focus squads --top 12
uv run mod-audit 123-456-789 --mode gac_defense --focus squads --top 12

# Fleet cleanup pass
uv run mod-audit 123-456-789 --mode gac_offense --focus fleets --top 10

# Proving Grounds prep (squad-only event logic)
uv run mod-audit 123-456-789 --mode proving_grounds --focus squads --eligibility best_effort --top 10

# Order 66 raid prep
uv run mod-audit 123-456-789 --mode order66 --focus squads --eligibility best_effort --top 10

# Generic raid exploration when event rules are unclear
uv run mod-audit 123-456-789 --mode raid --focus both --eligibility best_effort --top 10
```

Focus values:
- `squads`
- `fleets`
- `both` (default)

Eligibility values:
- `best_effort` (default)
- `off`

Eligibility behavior:
- `best_effort`: applies known or estimated event restrictions and reports confidence
- `off`: disables eligibility filtering and only uses mod-gap scoring
- If eligibility confidence is `unknown`, the report explicitly states best estimates are being used without hard exclusions

Goal modes:
- `pve` (default)
- `gac_offense`
- `gac_defense`
- `raid`
- `raid_order66` (alias: `order66`)
- `proving_grounds`

The audit is organized around prioritized squads and fleet pilot cores already covered by this repo's progression advice:
- Phoenix / Captain Rex
- Bounty Hunters
- Empire
- First Order
- Imperial Troopers

When `--eligibility best_effort` is enabled, the report includes:
- an eligibility confidence (`known`, `estimated`, or `unknown`)
- a note when the mode cannot be fully verified and best estimates are used
- count of excluded units filtered as ineligible

It reports:
- missing equipped mods
- missing recommended set combinations
- mismatched primaries on key slots
- speed shortfalls for units that need to move first

If the player API/cache returns sparse mod data, the report flags the result as a partial audit.

### Squad Plan

Build account-wide squad recommendations with exact owned memberships and a numbered improvement plan:

```powershell
uv run squad-plan <ally_code>
```

Options:
```powershell
uv run squad-plan 123-456-789 --top-squads 5
uv run squad-plan 123-456-789 --steps 12
uv run squad-plan 123-456-789 --eligibility off
```

What it does:
- analyzes squad priorities across `pve`, `gac_offense`, `gac_defense`, `raid`, `raid_order66`, and `proving_grounds`
- outputs ranked squads with exact member lists from your owned roster
- shows owned profile coverage per squad (for example `4/5` members owned)
- generates an account-wide `Do 1-N` improvement plan from top mod gaps

### Target Farm Focus

Build account-aware campaign spending advice for one character or ship target:

```powershell
uv run farm-focus <ally_code> --target "TARGET_NAME"
```

Options:
```powershell
uv run farm-focus 123-456-789 --target "Grand Moff Tarkin" --top 8
uv run farm-focus 123-456-789 --target "Executor" --top 10
```

What it does:
- resolves a target by name (character or ship)
- ranks campaign nodes for shard/blueprint progress
- boosts nodes that overlap with other unmaxed farms in your account
- highlights Signal Data support when target relic progression still matters
- includes a mod-farming note from mod-audit profile data and calls out when mod battle routing is estimated

## Discord Bot

The project includes an optional Discord bot that exposes all commands as slash commands.

### Discord Setup

1. Sync dependencies with the discord extra:
   ```powershell
   uv sync --extra discord
   ```

2. Add your Discord bot token to `.env`:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

3. Run the bot:
   ```powershell
   uv run --extra discord swgoh-discord
   ```

### Slash Commands

| Command | Description |
|---------|-------------|
| `/kyrotech` | Analyze a player's roster for kyrotech requirements |
| `/rote-platoon` | Analyze guild for RotE platoon requirements |
| `/rote-farm` | Personal farm recommendations based on guild needs |
| `/rote-bonus-readiness` | Analyze guild readiness for RotE bonus zones |

Slash commands generally mirror CLI parameters (ally code, max-phase, etc.).
`/rote-platoon` does not expose the `limited` output format; use the CLI `uv run rote-limited <ally_code>` for that report.

## Caching

API responses are cached in `data/` for 1 hour. Delete the folder to force a refresh.
- Player ally codes must be synced with SWGOH.gg
