#!/usr/bin/env python3
"""
Build SWGOH campaign node and character farm data files from static wiki data.
Source: swgoh.wiki (fetched 2026-05-07)

Outputs:
  data/campaign_nodes.json   - every node with energy cost, level req, all loot
  data/character_farms.json  - character/ship -> node lookup index
  data/relic_materials.json  - per-relic-level material requirements R1-R10
"""
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

REFRESH_PLAYBOOK = {
    "intent": "Keep campaign and relic datasets current for planning.",
    "cadence": "Refresh monthly and after any in-game economy or drop-table change.",
    "process": [
        "Fetch latest swgoh.wiki pages for Cantina, LS, DS, Fleet, and Relic Amplifier data.",
        "Update constants in scripts/build_campaign_data.py from verified tables.",
        "Run uv run python scripts/build_campaign_data.py to regenerate JSON files.",
        "Diff data/campaign_nodes.json, data/character_farms.json, and data/relic_materials.json for drift.",
        "Spot-check high-impact items: R8-R10 mats, Cantina signal data notes, and key ship shard nodes.",
        "Update reports that rely on these files and record the new version date.",
    ],
    "planning_modes": {
        "base": "Node-only attempt plan that ignores store and guild-event income.",
        "manual": "Base plan plus account-specific purchases (stores, raid currency, TB/TW rewards).",
    },
}

# ── CANTINA BATTLES ───────────────────────────────────────────────────────────
# energy_type: cantina, no daily limit on battles, 8-C/8-F/8-G = Signal Data only

CANTINA_NODES = {
    "1-A": {"lvl": 8,  "energy": 8,  "chars": ["Geonosian Soldier"],                              "ships": []},
    "1-B": {"lvl": 8,  "energy": 8,  "chars": ["Luke Skywalker (Farmboy)"],                       "ships": []},
    "1-C": {"lvl": 8,  "energy": 8,  "chars": ["Obi-Wan Kenobi (Old Ben)"],                       "ships": []},
    "1-D": {"lvl": 8,  "energy": 8,  "chars": ["Hondo Ohnaka"],                                   "ships": []},
    "1-E": {"lvl": 8,  "energy": 8,  "chars": ["Lando Calrissian", "Lobot"],                      "ships": []},
    "1-F": {"lvl": 8,  "energy": 8,  "chars": ["Cal Kestis"],                                     "ships": []},
    "1-G": {"lvl": 8,  "energy": 8,  "chars": ['Garazeb "Zeb" Orrelios', "Talia"],               "ships": []},
    "2-A": {"lvl": 16, "energy": 8,  "chars": ["Stormtrooper Han", "Captain Tarpals"],            "ships": []},
    "2-B": {"lvl": 16, "energy": 8,  "chars": ["Ezra Bridger", "Kanan Jarrus"],                   "ships": []},
    "2-C": {"lvl": 16, "energy": 8,  "chars": ["Sana Starros"],                                   "ships": []},
    "2-D": {"lvl": 16, "energy": 8,  "chars": ["Tusken Warrior"],                                 "ships": []},
    "2-E": {"lvl": 16, "energy": 8,  "chars": ["Gar Saxon"],                                      "ships": []},
    "2-F": {"lvl": 16, "energy": 8,  "chars": ["Clone Wars Chewbacca"],                           "ships": []},
    "2-G": {"lvl": 16, "energy": 8,  "chars": ["First Order Executioner"],                        "ships": []},
    "3-A": {"lvl": 35, "energy": 10, "chars": ["Comeuppance"],                                    "ships": []},
    "3-B": {"lvl": 35, "energy": 10, "chars": ["Qi'ra"],                                          "ships": []},
    "3-C": {"lvl": 35, "energy": 10, "chars": ["IG-100 MagnaGuard"],                              "ships": []},
    "3-D": {"lvl": 35, "energy": 10, "chars": ["Padawan Obi-Wan"],                                "ships": []},
    "3-E": {"lvl": 35, "energy": 10, "chars": ["Finn"],                                           "ships": []},
    "3-F": {"lvl": 35, "energy": 10, "chars": ["Kylo Ren (Unmasked)"],                            "ships": ["TIE Silencer"]},
    "3-G": {"lvl": 35, "energy": 10, "chars": ["Biggs Darklighter"],                              "ships": []},
    "4-A": {"lvl": 46, "energy": 10, "chars": ["Fifth Brother"],                                  "ships": []},
    "4-B": {"lvl": 46, "energy": 10, "chars": ["TIE Fighter Pilot"],                              "ships": ["Imperial TIE Fighter"]},
    "4-C": {"lvl": 46, "energy": 10, "chars": ["Kylo Ren"],                                       "ships": []},
    "4-D": {"lvl": 46, "energy": 10, "chars": ["Geonosian Spy"],                                  "ships": []},
    "4-E": {"lvl": 46, "energy": 10, "chars": ["Moff Gideon"],                                    "ships": []},
    "4-F": {"lvl": 46, "energy": 10, "chars": ["Master Qui-Gon"],                                 "ships": []},
    "4-G": {"lvl": 46, "energy": 10, "chars": ["Plo Koon"],                                       "ships": []},
    "5-A": {"lvl": 61, "energy": 12, "chars": ["L3-37"],                                          "ships": []},
    "5-B": {"lvl": 61, "energy": 12, "chars": ["Aayla Secura"],                                   "ships": []},
    "5-C": {"lvl": 61, "energy": 12, "chars": ["Canderous Ordo"],                                 "ships": []},
    "5-D": {"lvl": 61, "energy": 12, "chars": ["Chief Chirpa"],                                   "ships": []},
    "5-E": {"lvl": 61, "energy": 12, "chars": ["Veteran Smuggler Chewbacca", "Veteran Smuggler Han Solo"], "ships": []},
    "5-F": {"lvl": 61, "energy": 12, "chars": [],                                                 "ships": ["Mark VI Interceptor"]},
    "5-G": {"lvl": 61, "energy": 12, "chars": ["ARC Trooper"],                                    "ships": []},
    "6-A": {"lvl": 69, "energy": 12, "chars": ["Kyle Katarn"],                                    "ships": []},
    "6-B": {"lvl": 69, "energy": 12, "chars": ["T3-M4"],                                          "ships": []},
    "6-C": {"lvl": 69, "energy": 12, "chars": ["Sith Assassin"],                                  "ships": ["Sith Fighter"]},
    "6-D": {"lvl": 69, "energy": 12, "chars": ["B2 Super Battle Droid"],                          "ships": []},
    "6-E": {"lvl": 69, "energy": 12, "chars": ["Sith Marauder"],                                  "ships": []},
    "6-F": {"lvl": 69, "energy": 12, "chars": ["Captain Drogan"],                                 "ships": []},
    "6-G": {"lvl": 69, "energy": 12, "chars": ["Count Dooku"],                                    "ships": []},
    "7-A": {"lvl": 77, "energy": 16, "chars": ["Krrsantan"],                                      "ships": []},
    "7-B": {"lvl": 77, "energy": 16, "chars": ["Snowtrooper"],                                    "ships": []},
    "7-C": {"lvl": 77, "energy": 16, "chars": ["Aurra Sing"],                                     "ships": []},
    "7-D": {"lvl": 77, "energy": 16, "chars": ["Captain Han Solo"],                               "ships": []},
    "7-E": {"lvl": 77, "energy": 16, "chars": ["Dash Rendar"],                                    "ships": []},
    "7-F": {"lvl": 77, "energy": 16, "chars": [],                                                 "ships": ["STAP", "Plo Koon's Jedi Starfighter"]},
    "7-G": {"lvl": 77, "energy": 16, "chars": ["Darth Talon"],                                    "ships": []},
    "8-A": {"lvl": 83, "energy": 16, "chars": ["Death Trooper"],                                  "ships": []},
    "8-B": {"lvl": 83, "energy": 16, "chars": ["Sith Empire Trooper"],                            "ships": []},
    "8-C": {"lvl": 83, "energy": 16, "chars": [],                                                 "ships": [], "special": ["Signal Data", "Omicron ability material"]},
    "8-D": {"lvl": 83, "energy": 16, "chars": ["Geonosian Brood Alpha"],                          "ships": []},
    "8-E": {"lvl": 83, "energy": 16, "chars": ["Carth Onasi"],                                    "ships": ["Ebon Hawk"]},
    "8-F": {"lvl": 83, "energy": 16, "chars": [],                                                 "ships": [], "special": ["Signal Data", "Omicron ability material"]},
    "8-G": {"lvl": 83, "energy": 16, "chars": [],                                                 "ships": [], "special": ["Signal Data", "Omicron ability material"]},
}

# ── LIGHT SIDE HARD ───────────────────────────────────────────────────────────
# 5 attempts/day, normal must be completed first, energy_type: normal

LS_HARD_NODES = {
    # Map 1 (lvl 1, 12 energy)
    "1-A": {"lvl": 1,  "energy": 12, "chars": ["Rey (Scavenger)"],                                   "ships": [],                    "gear": ["Mk 1 BAW Armor Mod", "Mk 1 TaggeCo Holo Lens", "Mk 1 Nubian Security Scanner"]},
    "1-B": {"lvl": 1,  "energy": 12, "chars": ["Ahsoka Tano (Snips)"],                              "ships": [],                    "gear": ["Mk 1 BAW Armor Mod", "Mk 1 Fabritech Data Pad", "Mk 1 CEC Fusion Furnace"]},
    "1-C": {"lvl": 1,  "energy": 12, "chars": ["Dark Trooper"],                                      "ships": [],                    "gear": ["Mk 1 Merr-Sonn Shield Generator", "Mk 1 BioTech Implant", "Mk 1 BlasTech Weapon Mod"]},
    "1-D": {"lvl": 1,  "energy": 12, "chars": ["Kylo Ren (Unmasked)"],                              "ships": [],                    "gear": ["Mk 1 BAW Armor Mod", "Mk 1 Neuro-Saav Electrobinoculars", "Mk 1 Arakyd Droid Caller"]},
    # Map 2 (lvl 1, 12 energy)
    "2-A": {"lvl": 1,  "energy": 12, "chars": ["Ewok Elder", "Ewok Scout"],                          "ships": [],                    "gear": ["Mk 1 Loronar Power Cell", "Mk 2 BAW Armor Mod Prototype", "Mk 1 A-KT Stun Gun"]},
    "2-B": {"lvl": 1,  "energy": 12, "chars": ["Sith Trooper", "First Order Stormtrooper"],         "ships": [],                    "gear": ["Mk 1 SoroSuub Keypad", "Mk 1 BAW Armor Mod", "Mk 2 Nubian Security Scanner Prototype"]},
    "2-C": {"lvl": 1,  "energy": 12, "chars": ["BT-1"],                                              "ships": [],                    "gear": ["Mk 1 Fabritech Data Pad", "Mk 1 Arakyd Droid Caller", "Mk 1 BlasTech Weapon Mod"]},
    "2-D": {"lvl": 1,  "energy": 12, "chars": ["Moff Gideon"],                                       "ships": [],                    "gear": ["Mk 2 Arakyd Droid Caller", "Mk 1 TaggeCo Holo Lens", "Mk 1 Chiewab Hypo Syringe Prototype"]},
    "2-E": {"lvl": 1,  "energy": 12, "chars": ["Mace Windu"],                                        "ships": [],                    "gear": ["Mk 1 Czerka Stun Cuffs", "Mk 1 BioTech Implant", "Mk 1 BlasTech Weapon Mod"]},
    "2-F": {"lvl": 1,  "energy": 12, "chars": ["Hera Syndulla"],                                     "ships": ["Ghost"],             "gear": ["Mk 2 Chiewab Hypo Syringe", "Mk 1 Neuro-Saav Electrobinoculars", "Mk 2 Neuro-Saav Electrobinoculars Prototype"]},
    # Map 3 (lvl 1, 12 energy)
    "3-A": {"lvl": 1,  "energy": 12, "chars": ["Cere Junda"],                                        "ships": [],                    "gear": ["Mk 4 BAW Armor Mod Salvage", "Mk 2 TaggeCo Holo Lens", "Mk 1 BlasTech Weapon Mod"]},
    "3-B": {"lvl": 1,  "energy": 12, "chars": ["Skiff Guard (Lando Calrissian)"],                   "ships": [],                    "gear": ["Mk 1 Sienar Holo Projector", "Mk 2 Fabritech Data Pad", "Mk 1 Loronar Power Cell"]},
    "3-C": {"lvl": 1,  "energy": 12, "chars": ["Stormtrooper"],                                      "ships": [],                    "gear": ["Mk 3 BlasTech Weapon Mod", "Mk 1 TaggeCo Holo Lens", "Mk 1 Arakyd Droid Caller"]},
    "3-D": {"lvl": 1,  "energy": 12, "chars": ["Ninth Sister"],                                      "ships": [],                    "gear": ["Mk 3 BioTech Implant", "Mk 1 Nubian Design Tech Prototype", "Mk 2 BlasTech Weapon Mod"]},
    "3-E": {"lvl": 1,  "energy": 12, "chars": ["Greef Karga", "IG-11"],                             "ships": [],                    "gear": ["Mk 1 Athakam Medpac Salvage", "Mk 3 Neuro-Saav Electrobinoculars", "Mk 1 BioTech Implant"]},
    "3-F": {"lvl": 1,  "energy": 12, "chars": ["Dathcha"],                                           "ships": [],                    "gear": ["Mk 3 TaggeCo Holo Lens Prototype", "Mk 1 Merr-Sonn Shield Generator", "Mk 1 Nubian Security Scanner", "Mk 1 A-KT Stun Gun"]},
    # Map 4 (lvl 18, 12 energy)
    "4-A": {"lvl": 18, "energy": 12, "chars": ["Paz Vizsla"],                                        "ships": [],                    "gear": ["Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 2 Chedak Comlink Prototype", "Mk 2 Neuro-Saav Electrobinoculars Prototype", "Mk 1 A-KT Stun Gun"]},
    "4-B": {"lvl": 18, "energy": 12, "chars": ["Saw Gerrera"],                                       "ships": [],                    "gear": ["Mk 4 Fabritech Data Pad Prototype", "Mk 4 TaggeCo Holo Lens Salvage", "Mk 1 Fabritech Data Pad", "Mk 2 Nubian Security Scanner Prototype"]},
    "4-C": {"lvl": 18, "energy": 12, "chars": ["General Veers"],                                     "ships": [],                    "gear": ["Mk 5 Loronar Power Cell Salvage", "Mk 4 BlasTech Weapon Mod Prototype", "Mk 2 BlasTech Weapon Mod", "Mk 1 Fabritech Data Pad"]},
    "4-D": {"lvl": 18, "energy": 12, "chars": ["Iden Versio"],                                       "ships": ["Vulture Droid"],     "gear": ["Mk 5 Neuro-Saav Electrobinoculars Salvage", "Mk 4 BioTech Implant Prototype", "Mk 1 BioTech Implant", "Mk 1 Chiewab Hypo Syringe Prototype"]},
    "4-E": {"lvl": 18, "energy": 12, "chars": ["Poggle the Lesser"],                                 "ships": [],                    "gear": ["Mk 5 BAW Armor Mod Salvage", "Mk 5 BlasTech Weapon Mod Prototype", "Mk 1 Neuro-Saav Electrobinoculars", "Mk 1 Arakyd Droid Caller"]},
    "4-F": {"lvl": 18, "energy": 12, "chars": ["Resistance Trooper", "Rose Tico"],                  "ships": [],                    "gear": ["Mk 3 Arakyd Droid Caller Salvage", "Mk 2 Chiewab Hypo Syringe", "Mk 3 BioTech Implant", "Mk 1 BlasTech Weapon Mod"]},
    # Map 5 (lvl 43, 16 energy)
    "5-A": {"lvl": 43, "energy": 16, "chars": ["URoRRuR'R'R"],                                      "ships": [],                    "gear": ["Mk 5 Neuro-Saav Electrobinoculars Salvage", "Mk 5 BAW Armor Mod Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 3 Neuro-Saav Electrobinoculars"]},
    "5-B": {"lvl": 43, "energy": 16, "chars": ["Hunter"],                                            "ships": [],                    "gear": ["Mk 6 Neuro-Saav Electrobinoculars Prototype Salvage", "Mk 3 TaggeCo Holo Lens Prototype", "Mk 6 BlasTech Weapon Mod Prototype", "Mk 4 A-KT Stun Gun Salvage"]},
    "5-C": {"lvl": 43, "energy": 16, "chars": ["Princess Kneesaa"],                                  "ships": [],                    "gear": ["Mk 4 SoroSuub Keypad Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 2 Arakyd Droid Caller", "Mk 2 Fabritech Data Pad"]},
    "5-D": {"lvl": 43, "energy": 16, "chars": ["Mission Vao", "Zaalbar"],                           "ships": [],                    "gear": ["Mk 8 BlasTech Weapon Mod Prototype Salvage", "Mk 5 Loronar Power Cell Salvage", "Mk 3 Neuro-Saav Electrobinoculars", "Mk 3 BlasTech Weapon Mod"]},
    "5-E": {"lvl": 43, "energy": 16, "chars": ["Mon Mothma"],                                        "ships": [],                    "gear": ["Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 7 BAW Armor Mod Prototype Salvage", "Mk 1 Sienar Holo Projector", "Mk 1 Nubian Design Tech Prototype"]},
    "5-F": {"lvl": 43, "energy": 16, "chars": ["Tech"],                                              "ships": [],                    "gear": ["Mk 5 SoroSuub Keypad Salvage", "Mk 4 TaggeCo Holo Lens Salvage", "Mk 5 Fabritech Data Pad", "Mk 1 TaggeCo Holo Lens"]},
    # Map 6 (lvl 54, 16 energy)
    "6-A": {"lvl": 54, "energy": 16, "chars": ["Gungan Boomadier"],                                  "ships": [],                    "gear": ["Mk 6 Nubian Security Scanner Prototype Salvage", "Mk 3 Sienar Holo Projector Salvage", "Mk 6 Fabritech Data Pad Salvage", "Mk 4 Chiewab Hypo Syringe Prototype Salvage"]},
    "6-B": {"lvl": 54, "energy": 16, "chars": ["Resistance Hero Poe", "Admiral Piett"],             "ships": [],                    "gear": ["Mk 5 Nubian Design Tech Prototype Salvage", "Mk 2 Zaltin Bacta Gel Prototype Salvage", "Mk 1 Athakam Medpac Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage"]},
    "6-C": {"lvl": 54, "energy": 16, "chars": ["Fennec Shand"],                                      "ships": ["B-28 Extinction-class Bomber"], "gear": ["Mk 5 Chiewab Hypo Syringe Prototype Salvage", "Mk 4 BAW Armor Mod Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 4 A-KT Stun Gun Salvage"]},
    "6-D": {"lvl": 54, "energy": 16, "chars": ["Mara Jade", "The Emperor's Hand"],                  "ships": [],                    "gear": ["Mk 4 Arakyd Droid Caller Salvage", "Mk 6 BioTech Implant Prototype Salvage", "Mk 5 BAW Armor Mod Salvage", "Mk 6 Neuro-Saav Electrobinoculars Prototype Salvage"]},
    "6-E": {"lvl": 54, "energy": 16, "chars": ["Eighth Brother"],                                    "ships": ["IG-2000"],           "gear": ["Mk 4 SoroSuub Keypad Salvage", "Mk 5 SoroSuub Keypad Salvage", "Mk 5 Neuro-Saav Electrobinoculars Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage"]},
    # Map 7 (lvl 63, 20 energy)
    "7-A": {"lvl": 63, "energy": 20, "chars": ["Threepio & Chewie"],                                 "ships": [],                    "gear": ["Mk 5 SoroSuub Keypad Salvage", "Mk 3 Sienar Holo Projector Salvage", "Mk 7 BAW Armor Mod Prototype Salvage", "Mk 4 Chiewab Hypo Syringe Prototype Salvage"]},
    "7-B": {"lvl": 63, "energy": 20, "chars": ["Poe Dameron"],                                       "ships": [],                    "gear": ["Mk 3 Czerka Stun Cuffs Salvage", "Mk 7 BioTech Implant Prototype Salvage", "Mk 4 TaggeCo Holo Lens Salvage", "Mk 4 Nubian Security Scanner Prototype Salvage"]},
    "7-C": {"lvl": 63, "energy": 20, "chars": ["Wrecker"],                                           "ships": ["BTL-B Y-wing Starfighter"], "gear": ["Mk 8 BlasTech Weapon Mod Prototype Salvage", "Mk 6 Chiewab Hypo Syringe Salvage", "Mk 3 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 6 TaggeCo Holo Lens Prototype Salvage"]},
    "7-D": {"lvl": 63, "energy": 20, "chars": ["Luke Skywalker (Farmboy)", "Echo"],                 "ships": [],                    "gear": ["Mk 4 Arakyd Droid Caller Salvage", "Mk 3 Carbanti Sensor Array Salvage", "Mk 5 Loronar Power Cell Salvage", "Mk 3 Chiewab Hypo Syringe Prototype Salvage"]},
    # Map 8 (lvl 74, 20 energy)
    "8-A": {"lvl": 74, "energy": 20, "chars": ["Mother Talzin"],                                     "ships": [],                    "gear": ["Mk 4 CEC Fusion Furnace Prototype Salvage", "Mk 8 BlasTech Weapon Mod Prototype Salvage", "Mk 1 Athakam Medpac Salvage", "Mk 6 Neuro-Saav Electrobinoculars Prototype Salvage"]},
    "8-B": {"lvl": 74, "energy": 20, "chars": ["Droideka"],                                          "ships": ["Xanadu Blood"],     "gear": ["Mk 6 Nubian Security Scanner Prototype Salvage", "Mk 2 Zaltin Bacta Gel Prototype Salvage", "Mk 4 TaggeCo Holo Lens Salvage", "Mk 4 Nubian Security Scanner Prototype Salvage"]},
    "8-C": {"lvl": 74, "energy": 20, "chars": ["Snowtrooper", "Resistance Hero Finn"],             "ships": [],                    "gear": ["Mk 3 Carbanti Sensor Array Salvage", "Mk 6 Chiewab Hypo Syringe Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage"]},
    "8-D": {"lvl": 74, "energy": 20, "chars": ["Jango Fett"],                                        "ships": ["Hound's Tooth"],    "gear": ["Mk 4 SoroSuub Keypad Salvage", "Mk 3 Czerka Stun Cuffs Salvage", "Mk 10 BlasTech Weapon Mod Salvage", "Mk 7 BlasTech Weapon Mod Prototype Salvage"]},
    # Map 9 (lvl 82, 20 energy)
    "9-A": {"lvl": 82, "energy": 20, "chars": ["Darth Sion"],                                        "ships": ["Kylo Ren's Command Shuttle"], "gear": ["Mk 7 Merr-Sonn Shield Generator Salvage", "Mk 4 SoroSuub Keypad Salvage", "Mk 10 BlasTech Weapon Mod Component", "Mk 7 BlasTech Weapon Mod Prototype Salvage"]},
    "9-B": {"lvl": 82, "energy": 20, "chars": ["Shoretrooper"],                                      "ships": ["TIE Reaper"],        "gear": ["Mk 9 Neuro-Saav Electrobinoculars Salvage", "Mk 8 BlasTech Weapon Mod Prototype Salvage", "Mk 4 Nubian Security Scanner Prototype Salvage", "Mk 8 Neuro-Saav Electrobinoculars Salvage"]},
    "9-C": {"lvl": 82, "energy": 20, "chars": ["Baze Malbus", "The Armorer"],                       "ships": [],                    "gear": ["Mk 9 Fabritech Data Pad Component", "Mk 8 BioTech Implant Salvage", "Mk 6 Nubian Security Scanner Prototype Salvage", "Mk 6 Neuro-Saav Electrobinoculars Prototype Salvage"]},
    "9-D": {"lvl": 82, "energy": 20, "chars": ["Director Krennic"],                                  "ships": ["Geonosian Soldier's Starfighter"], "gear": ["Mk 5 Athakam Medpac Salvage", "Mk 2 Zaltin Bacta Gel Prototype Salvage", "Mk 5 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage"]},
}

# ── LIGHT SIDE NORMAL (key gear farming nodes) ───────────────────────────────
# Included: nodes that drop relic-relevant scrap gear or frequently farmed gear
LS_NORMAL_NODES = {
    "1-C": {"lvl": 1,  "energy": 6,  "chars": [], "ships": [], "gear": ["Mk 1 BAW Armor Mod", "Mk 1 Neuro-Saav Electrobinoculars", "Mk 1 TaggeCo Holo Lens", "Mk 1 Nubian Security Scanner", "Mk 1 BlasTech Weapon Mod"], "relic_scrap": ["Carbonite Circuit Board"]},
    "1-F": {"lvl": 1,  "energy": 6,  "chars": [], "ships": [], "gear": ["Mk 1 Merr-Sonn Shield Generator", "Mk 1 Neuro-Saav Electrobinoculars", "Mk 1 TaggeCo Holo Lens", "Mk 1 Fabritech Data Pad", "Mk 1 BioTech Implant"], "relic_scrap": []},
    "6-E": {"lvl": 54, "energy": 8,  "chars": [], "ships": [], "gear": ["Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 2 BAW Armor Mod Prototype", "Mk 4 A-KT Stun Gun Salvage"], "relic_scrap": []},
    "7-B": {"lvl": 63, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 5 SoroSuub Keypad Salvage", "Mk 7 BAW Armor Mod Prototype Salvage", "Mk 5 Fabritech Data Pad", "Mk 7 Kyrotech Shock Prod Prototype Salvage"], "relic_scrap": ["Bronzium Wiring"]},
    "8-E": {"lvl": 74, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 6 Chiewab Hypo Syringe Salvage", "Mk 3 TaggeCo Holo Lens Prototype", "Mk 1 BAW Armor Mod", "Mk 1 Athakam Medpac Salvage"], "relic_scrap": []},
    "8-H": {"lvl": 74, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 4 SoroSuub Keypad Salvage", "Mk 10 BlasTech Weapon Mod Salvage", "Mk 1 Loronar Power Cell"], "relic_scrap": []},
    "9-A": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Armor Plating Prototype Salvage", "Mk 7 Merr-Sonn Shield Generator Salvage", "Mk 6 TaggeCo Holo Lens Prototype Salvage", "Mk 6 Fabritech Data Pad Salvage", "Mk 2 Arakyd Droid Caller"], "relic_scrap": ["Electrium Conductor", "Aurodium Heatsink"]},
    "9-B": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Tactical Data Prototype Salvage", "Mk 10 BlasTech Weapon Mod Component", "Mk 4 Chiewab Hypo Syringe Prototype Salvage", "Mk 5 Fabritech Data Pad"], "relic_scrap": ["Bronzium Wiring", "Chromium Transistor"]},
    "9-C": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Medpac Prototype Salvage", "Mk 9 Neuro-Saav Electrobinoculars Salvage", "Mk 6 Neuro-Saav Electrobinoculars Prototype Salvage", "Mk 2 Chedak Comlink Prototype"], "relic_scrap": ["Impulse Detector"]},
    "9-D": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 6 Arakyd Droid Caller Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 4 BioTech Implant Prototype", "Mk 8 Neuro-Saav Electrobinoculars Salvage"], "relic_scrap": []},
    "9-E": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 9 Fabritech Data Pad Component", "Mk 12 ArmaTek Visor Prototype Salvage", "Mk 4 SoroSuub Keypad Salvage", "Mk 3 BioTech Implant", "Mk 7 BlasTech Weapon Mod Prototype Salvage"], "relic_scrap": ["Electrium Conductor", "Chromium Transistor"]},
    "9-F": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Bayonet Prototype Salvage", "Mk 8 BioTech Implant Salvage", "Mk 3 Sienar Holo Projector Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 2 Chiewab Hypo Syringe"], "relic_scrap": ["Impulse Detector", "Aurodium Heatsink"]},
    "9-G": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 5 Athakam Medpac Salvage", "Mk 5 SoroSuub Keypad Salvage", "Mk 4 Nubian Security Scanner Prototype Salvage", "Mk 6 BlasTech Weapon Mod Prototype"], "relic_scrap": []},
    "9-H": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 8 BioTech Implant Salvage", "Mk 7 Nubian Design Tech Salvage", "Mk 4 Arakyd Droid Caller Salvage", "Mk 4 Fabritech Data Pad Prototype", "Mk 4 Nubian Security Scanner Prototype Salvage"], "relic_scrap": []},
}

# ── DARK SIDE HARD ────────────────────────────────────────────────────────────
DS_HARD_NODES = {
    # Map 1 (lvl 12, 12 energy)
    "1-A": {"lvl": 12, "energy": 12, "chars": ["Sabine Wren"],                                       "ships": ["Phantom II"],            "gear": ["Mk 2 CEC Fusion Furnace", "Mk 1 Nubian Security Scanner", "Mk 1 BlasTech Weapon Mod"]},
    "1-B": {"lvl": 12, "energy": 12, "chars": ["Jedi Knight Anakin"],                               "ships": [],                        "gear": ["Mk 2 TaggeCo Holo Lens", "Mk 3 Loronar Power Cell", "Mk 2 BlasTech Weapon Mod"]},
    "1-C": {"lvl": 12, "energy": 12, "chars": ["Princess Leia", "Zorii Bliss"],                     "ships": [],                        "gear": ["Mk 5 BioTech Implant Prototype", "Mk 3 BioTech Implant", "Mk 1 SoroSuub Keypad"]},
    "1-D": {"lvl": 12, "energy": 12, "chars": ["Chopper", "Jedi Consular"],                         "ships": [],                        "gear": ["Mk 3 BAW Armor Mod", "Mk 1 Nubian Design Tech Prototype", "Mk 2 SoroSuub Keypad Prototype"]},
    # Map 2 (lvl 12, 12 energy)
    "2-A": {"lvl": 12, "energy": 12, "chars": ["0-0-0"],                                             "ships": [],                        "gear": ["Mk 2 CEC Fusion Furnace", "Mk 2 Chedak Comlink Prototype", "Mk 1 Arakyd Droid Caller"]},
    "2-B": {"lvl": 12, "energy": 12, "chars": ["Boba Fett"],                                         "ships": [],                        "gear": ["Mk 6 Loronar Power Cell Salvage", "Mk 5 BlasTech Weapon Mod Prototype", "Mk 1 Neuro-Saav Electrobinoculars"]},
    "2-C": {"lvl": 12, "energy": 12, "chars": ["Boushh (Leia Organa)"],                             "ships": [],                        "gear": ["Mk 4 BAW Armor Mod Salvage", "Mk 4 Loronar Power Cell Prototype", "Mk 2 BlasTech Weapon Mod"]},
    "2-D": {"lvl": 12, "energy": 12, "chars": ['CT-5555 "Fives"'],                                  "ships": ["Umbaran Starfighter"],   "gear": ["Mk 4 Fabritech Data Pad Prototype", "Mk 5 Loronar Power Cell Salvage", "Mk 3 BioTech Implant"]},
    "2-E": {"lvl": 12, "energy": 12, "chars": ["Kelleran Beq"],                                      "ships": [],                        "gear": ["Mk 3 Arakyd Droid Caller Salvage", "Mk 4 BlasTech Weapon Mod Prototype", "Mk 4 BioTech Implant Prototype"]},
    "2-F": {"lvl": 12, "energy": 12, "chars": ["IG-86 Sentinel Droid"],                             "ships": [],                        "gear": ["Mk 1 Chedak Comlink Salvage", "Mk 2 Merr-Sonn Shield Generator", "Mk 2 Chiewab Hypo Syringe", "Mk 2 Nubian Security Scanner Prototype"]},
    # Map 3 (lvl 12, 12 energy)
    "3-A": {"lvl": 12, "energy": 12, "chars": ["Range Trooper"],                                     "ships": [],                        "gear": ["Mk 3 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 1 Czerka Stun Cuffs", "Mk 2 BAW Armor Mod Prototype"]},
    "3-B": {"lvl": 12, "energy": 12, "chars": ["Hoth Rebel Soldier"],                               "ships": [],                        "gear": ["Mk 6 Fabritech Data Pad Salvage", "Mk 2 SoroSuub Keypad Prototype", "Mk 2 BlasTech Weapon Mod"]},
    "3-C": {"lvl": 12, "energy": 12, "chars": ["The Mandalorian"],                                   "ships": [],                        "gear": ["Mk 4 Nubian Security Scanner Prototype Salvage", "Mk 3 BAW Armor Mod", "Mk 2 Arakyd Droid Caller"]},
    "3-D": {"lvl": 12, "energy": 12, "chars": ["Teebo"],                                             "ships": [],                        "gear": ["Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 4 Chiewab Hypo Syringe Prototype Salvage", "Mk 2 CEC Fusion Furnace"]},
    "3-E": {"lvl": 12, "energy": 12, "chars": ["50R-T"],                                             "ships": [],                        "gear": ["Mk 4 BAW Armor Mod Salvage", "Mk 5 TaggeCo Holo Lens Prototype Salvage", "Mk 2 TaggeCo Holo Lens"]},
    "3-F": {"lvl": 12, "energy": 12, "chars": ["Captain Rex"],                                       "ships": [],                        "gear": ["Mk 3 Chiewab Hypo Syringe Prototype Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 3 Loronar Power Cell", "Mk 1 Chiewab Hypo Syringe Prototype"]},
    # Map 4 (lvl 24, 12 energy)
    "4-A": {"lvl": 24, "energy": 12, "chars": ["Admiral Raddus"],                                    "ships": [],                        "gear": ["Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 1 Zaltin Bacta Gel Prototype Salvage", "Mk 2 Chiewab Hypo Syringe", "Mk 3 BioTech Implant"]},
    "4-B": {"lvl": 24, "energy": 12, "chars": ["Old Daka"],                                          "ships": [],                        "gear": ["Mk 6 TaggeCo Holo Lens Prototype Salvage", "Mk 6 Fabritech Data Pad Salvage", "Mk 2 BlasTech Weapon Mod", "Mk 2 Neuro-Saav Electrobinoculars Prototype"]},
    "4-C": {"lvl": 24, "energy": 12, "chars": ["Second Sister"],                                     "ships": [],                        "gear": ["Mk 7 BAW Armor Mod Prototype Salvage", "Mk 4 BioTech Implant Prototype", "Mk 1 TaggeCo Holo Lens", "Mk 7 BlasTech Weapon Mod Prototype Salvage"]},
    "4-D": {"lvl": 24, "energy": 12, "chars": ["Vandor Chewbacca", "Tarfful"],                      "ships": [],                        "gear": ["Mk 4 Nubian Security Scanner Prototype Salvage", "Mk 3 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 1 Merr-Sonn Shield Generator", "Mk 1 CEC Fusion Furnace"]},
    "4-E": {"lvl": 24, "energy": 12, "chars": ["Seventh Sister"],                                    "ships": [],                        "gear": ["Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 7 BAW Armor Mod Prototype Salvage", "Mk 2 Merr-Sonn Shield Generator", "Mk 1 Fabritech Data Pad"]},
    "4-F": {"lvl": 24, "energy": 12, "chars": ["Jawa"],                                              "ships": [],                        "gear": ["Mk 6 TaggeCo Holo Lens Prototype Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 1 Neuro-Saav Electrobinoculars", "Mk 1 Loronar Power Cell"]},
    # Map 5 (lvl 49, 16 energy)
    "5-A": {"lvl": 49, "energy": 16, "chars": ["Kuiil"],                                             "ships": ["Imperial TIE Bomber"],  "gear": ["Mk 5 Nubian Security Scanner Prototype Salvage", "Mk 4 Fabritech Data Pad Prototype", "Mk 4 BAW Armor Mod Salvage", "Mk 3 Chiewab Hypo Syringe Prototype Salvage"]},
    "5-B": {"lvl": 49, "energy": 16, "chars": ["Bastila Shan"],                                      "ships": [],                        "gear": ["Mk 4 CEC Fusion Furnace Prototype Salvage", "Mk 3 Arakyd Droid Caller Salvage", "Mk 5 BlasTech Weapon Mod Prototype", "Mk 7 BlasTech Weapon Mod Prototype Salvage"]},
    "5-C": {"lvl": 49, "energy": 16, "chars": ["Barriss Offee", "Ima-Gun Di"],                      "ships": [],                        "gear": ["Mk 5 Nubian Design Tech Prototype Salvage", "Mk 5 Loronar Power Cell Salvage", "Mk 3 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 6 BlasTech Weapon Mod Prototype"]},
    "5-D": {"lvl": 49, "energy": 16, "chars": ["Rey (Scavenger)"],                                   "ships": ["Rey's Millennium Falcon"], "gear": ["Mk 5 TaggeCo Holo Lens Prototype Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 2 TaggeCo Holo Lens", "Mk 2 CEC Fusion Furnace"]},
    "5-E": {"lvl": 49, "energy": 16, "chars": ["Cara Dune"],                                         "ships": [],                        "gear": ["Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 1 Zaltin Bacta Gel Prototype Salvage", "Mk 2 TaggeCo Holo Lens", "Mk 4 BlasTech Weapon Mod Prototype"]},
    "5-F": {"lvl": 49, "energy": 16, "chars": ["Royal Guard"],                                       "ships": [],                        "gear": ["Mk 4 Arakyd Droid Caller Salvage", "Mk 6 BioTech Implant Prototype Salvage", "Mk 5 BioTech Implant Prototype", "Mk 2 Chedak Comlink Prototype"]},
    # Map 6 (lvl 59, 16 energy)
    "6-A": {"lvl": 59, "energy": 16, "chars": ["Hoth Rebel Scout", "General Hux"],                  "ships": [],                        "gear": ["Mk 5 Nubian Security Scanner Prototype Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 6 TaggeCo Holo Lens Prototype Salvage", "Mk 3 Loronar Power Cell"]},
    "6-B": {"lvl": 59, "energy": 16, "chars": ["First Order TIE Pilot"],                            "ships": [],                        "gear": ["Mk 4 SoroSuub Keypad Salvage", "Mk 2 Zaltin Bacta Gel Prototype Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 6 Neuro-Saav Electrobinoculars Prototype Salvage"]},
    "6-C": {"lvl": 59, "energy": 16, "chars": ["Tusken Raider", "Tusken Chieftain"],                "ships": [],                        "gear": ["Mk 6 Fabritech Data Pad Salvage", "Mk 1 Zaltin Bacta Gel Prototype Salvage", "Mk 3 BAW Armor Mod", "Mk 4 A-KT Stun Gun Salvage"]},
    "6-D": {"lvl": 59, "energy": 16, "chars": ["Jolee Bindo", "Bo-Katan Kryze"],                   "ships": [],                        "gear": ["Mk 3 Carbanti Sensor Array Salvage", "Mk 6 Loronar Power Cell Salvage", "Mk 3 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 2 Chiewab Hypo Syringe"]},
    "6-E": {"lvl": 59, "energy": 16, "chars": ["IG-100 MagnaGuard"],                                "ships": [],                        "gear": ["Mk 5 Nubian Security Scanner Prototype Salvage", "Mk 3 Chedak Comlink Prototype Salvage", "Mk 1 Chedak Comlink Salvage", "Mk 4 Loronar Power Cell Prototype"]},
    # Map 7 (lvl 67, 20 energy)
    "7-A": {"lvl": 67, "energy": 20, "chars": ["Bastila Shan (Fallen)"],                            "ships": [],                        "gear": ["Mk 7 BioTech Implant Prototype Salvage", "Mk 4 Chedak Comlink Prototype Salvage", "Mk 5 TaggeCo Holo Lens Prototype Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage"]},
    "7-B": {"lvl": 67, "energy": 20, "chars": ["Visas Marr"],                                        "ships": [],                        "gear": ["Mk 4 CEC Fusion Furnace Prototype Salvage", "Mk 4 Carbanti Sensor Array Prototype Salvage", "Mk 3 Arakyd Droid Caller Salvage", "Mk 1 Zaltin Bacta Gel Prototype Salvage"]},
    "7-C": {"lvl": 67, "energy": 20, "chars": ["Amilyn Holdo"],                                      "ships": [],                        "gear": ["Mk 5 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 3 Chiewab Hypo Syringe Prototype Salvage", "Mk 5 A-KT Stun Gun Prototype Salvage", "Mk 7 BlasTech Weapon Mod Prototype Salvage"]},
    "7-D": {"lvl": 67, "energy": 20, "chars": [],                                                    "ships": ["Emperor's Shuttle"],    "gear": ["Mk 4 Arakyd Droid Caller Salvage", "Mk 5 Chiewab Hypo Syringe Prototype Salvage", "Mk 4 BAW Armor Mod Salvage", "Mk 1 Chedak Comlink Salvage"]},
    # Map 8 (lvl 76, 20 energy)
    "8-A": {"lvl": 76, "energy": 20, "chars": ["Wicket"],                                            "ships": [],                        "gear": ["Mk 3 Chedak Comlink Prototype Salvage", "Mk 6 Loronar Power Cell Salvage", "Mk 7 BAW Armor Mod Prototype Salvage", "Mk 5 A-KT Stun Gun Prototype Salvage"]},
    "8-B": {"lvl": 76, "energy": 20, "chars": [],                                                    "ships": ["Jedi Consular's Starfighter", "Hyena Bomber"], "gear": ["Mk 3 Czerka Stun Cuffs Salvage", "Mk 4 Chedak Comlink Prototype Salvage", "Mk 4 BAW Armor Mod Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage"]},
    "8-C": {"lvl": 76, "energy": 20, "chars": ["Night Trooper"],                                     "ships": [],                        "gear": ["Mk 4 Carbanti Sensor Array Prototype Salvage", "Mk 5 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 3 Arakyd Droid Caller Salvage", "Mk 5 Loronar Power Cell Salvage"]},
    "8-D": {"lvl": 76, "energy": 20, "chars": ["Boss Nass"],                                         "ships": [],                        "gear": ["Mk 5 Nubian Design Tech Prototype Salvage", "Mk 3 Sienar Holo Projector Salvage", "Mk 5 TaggeCo Holo Lens Prototype Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage"]},
    # Map 9 (lvl 85, 20 energy)
    "9-A": {"lvl": 85, "energy": 20, "chars": ["Darth Nihilus"],                                     "ships": [],                        "gear": ["Mk 4 Arakyd Droid Caller Salvage", "Mk 7 BAW Armor Mod Prototype Salvage", "Mk 10 BlasTech Weapon Mod Salvage", "Mk 8 Neuro-Saav Electrobinoculars Component"]},
    "9-B": {"lvl": 85, "energy": 20, "chars": ["Bossk"],                                             "ships": [],                        "gear": ["Mk 9 Fabritech Data Pad Salvage", "Mk 5 Nubian Security Scanner Prototype Salvage", "Mk 6 TaggeCo Holo Lens Prototype Salvage", "Mk 10 Neuro-Saav Electrobinoculars Salvage"]},
    "9-C": {"lvl": 85, "energy": 20, "chars": ["Talia"],                                             "ships": [],                        "gear": ["Mk 8 BioTech Implant Component", "Mk 5 Athakam Medpac Component", "Mk 4 CEC Fusion Furnace Prototype Salvage", "Mk 1 Zaltin Bacta Gel Prototype Salvage"]},
    "9-D": {"lvl": 85, "energy": 20, "chars": [],                                                    "ships": ["TIE Dagger"],            "gear": ["Mk 9 Fabritech Data Pad Salvage", "Mk 5 Nubian Design Tech Prototype Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 10 Neuro-Saav Electrobinoculars Salvage"]},
}

# ── DARK SIDE NORMAL (relic-relevant nodes only) ─────────────────────────────
DS_NORMAL_NODES = {
    "8-A": {"lvl": 76, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 3 Chedak Comlink Prototype Salvage", "Mk 6 Loronar Power Cell Salvage", "Mk 1 Nubian Design Tech Prototype", "Mk 9 Kyrotech Battle Computer Prototype Salvage"], "relic_scrap": []},
    "8-B": {"lvl": 76, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 7 BAW Armor Mod Prototype Salvage", "Mk 4 Loronar Power Cell Prototype", "Mk 5 A-KT Stun Gun Prototype Salvage"], "relic_scrap": ["Bronzium Wiring"]},
    "9-A": {"lvl": 85, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Wrist Band Prototype Salvage", "Mk 4 BAW Armor Mod Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 10 BlasTech Weapon Mod Salvage", "Mk 4 BlasTech Weapon Mod Prototype"], "relic_scrap": ["Electrium Conductor", "Bronzium Wiring"]},
    "9-B": {"lvl": 85, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 3 Arakyd Droid Caller Salvage", "Mk 5 TaggeCo Holo Lens Prototype Salvage", "Mk 4 BlasTech Weapon Mod Prototype", "Mk 8 Neuro-Saav Electrobinoculars Component"], "relic_scrap": []},
    "9-C": {"lvl": 85, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Cybernetics Prototype Salvage", "Mk 4 Zaltin Bacta Gel Salvage", "Mk 6 Loronar Power Cell Salvage", "Mk 4 BioTech Implant Prototype", "Mk 10 Neuro-Saav Electrobinoculars Salvage", "Mk 7 BlasTech Weapon Mod Prototype Salvage"], "relic_scrap": ["Electrium Conductor"]},
    "9-D": {"lvl": 85, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Multi-tool Prototype Salvage", "Mk 9 Fabritech Data Pad Salvage", "Mk 9 BioTech Implant Salvage", "Mk 1 Chedak Comlink Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 4 Loronar Power Cell Prototype"], "relic_scrap": ["Impulse Detector"]},
    "9-F": {"lvl": 85, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 5 Athakam Medpac Component", "Mk 6 Carbanti Sensor Array Salvage", "Mk 1 Zaltin Bacta Gel Prototype Salvage", "Mk 5 BlasTech Weapon Mod Prototype"], "relic_scrap": ["Aurodium Heatsink"]},
    "9-G": {"lvl": 85, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 7 Merr-Sonn Thermal Detonator Salvage", "Mk 5 BioTech Implant Prototype", "Mk 6 Neuro-Saav Electrobinoculars Prototype Salvage", "Mk 10 Neuro-Saav Electrobinoculars Salvage"], "relic_scrap": []},
    "9-H": {"lvl": 85, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 9 Fabritech Data Pad Salvage", "Mk 7 CEC Fusion Furnace Salvage", "Mk 5 TaggeCo Holo Lens Prototype Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 2 Merr-Sonn Shield Generator"], "relic_scrap": []},
}

# ── FLEET HARD ────────────────────────────────────────────────────────────────
FLEET_HARD_NODES = {
    # Map 1 (lvl 60, 16 energy)
    "1-A": {"lvl": 60, "energy": 16, "chars": [],                          "ships": ["Clone Sergeant's ARC-170"],       "gear": ["Mk 4 SoroSuub Keypad Salvage", "Mk 2 Arakyd Droid Caller"]},
    "1-B": {"lvl": 60, "energy": 16, "chars": [],                          "ships": ["Anakin's Eta-2 Starfighter"],     "gear": ["Mk 8 BlasTech Weapon Mod Prototype Salvage", "Mk 3 TaggeCo Holo Lens Prototype"]},
    "1-C": {"lvl": 60, "energy": 16, "chars": ["Merrin"],                  "ships": [],                                "gear": ["Mk 8 BlasTech Weapon Mod Prototype Salvage", "Mk 3 Neuro-Saav Electrobinoculars"]},
    "1-D": {"lvl": 60, "energy": 16, "chars": ["Young Lando Calrissian"],  "ships": ["Lando's Millennium Falcon"],     "gear": ["Mk 3 Sienar Holo Projector Salvage", "Mk 4 Loronar Power Cell Prototype", "Mk 1 Chiewab Hypo Syringe Prototype"]},
    "1-E": {"lvl": 60, "energy": 16, "chars": [],                          "ships": ["Resistance X-wing"],             "gear": ["Mk 5 Nubian Design Tech Prototype Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 2 BlasTech Weapon Mod"]},
    # Map 2 (lvl 65, 20 energy)
    "2-A": {"lvl": 65, "energy": 20, "chars": [],                          "ships": ["Sun Fac's Geonosian Starfighter"], "gear": ["Mk 2 Zaltin Bacta Gel Prototype Salvage", "Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 1 CEC Fusion Furnace"]},
    "2-B": {"lvl": 65, "energy": 20, "chars": [],                          "ships": ["Slave I"],                       "gear": ["Mk 5 Chiewab Hypo Syringe Prototype Salvage", "Mk 4 BAW Armor Mod Salvage", "Mk 2 Fabritech Data Pad"]},
    "2-C": {"lvl": 65, "energy": 20, "chars": ["IG-12 & Grogu"],           "ships": [],                                "gear": ["Mk 3 Chedak Comlink Prototype Salvage", "Mk 6 Fabritech Data Pad Salvage", "Mk 6 BlasTech Weapon Mod Prototype"]},
    "2-D": {"lvl": 65, "energy": 20, "chars": [],                          "ships": ["MG-100 StarFortress SF-17"],     "gear": ["Mk 6 Chiewab Hypo Syringe Salvage", "Mk 5 BioTech Implant Prototype", "Mk 6 Loronar Power Cell Salvage"]},
    "2-E": {"lvl": 65, "energy": 20, "chars": [],                          "ships": ["Raven's Claw"],                  "gear": ["Mk 3 Carbanti Sensor Array Salvage", "Mk 6 TaggeCo Holo Lens Prototype Salvage", "Mk 2 Chedak Comlink Prototype"]},
    # Map 3 (lvl 72, 20 energy)
    "3-A": {"lvl": 72, "energy": 20, "chars": [],                          "ships": ["Poe Dameron's X-wing"],          "gear": ["Mk 7 BioTech Implant Prototype Salvage", "Mk 4 TaggeCo Holo Lens Salvage", "Mk 2 Chiewab Hypo Syringe"]},
    "3-B": {"lvl": 72, "energy": 20, "chars": [],                          "ships": ["TIE Defender"],                  "gear": ["Mk 3 Czerka Stun Cuffs Salvage", "Mk 4 Nubian Security Scanner Prototype Salvage", "Mk 1 SoroSuub Keypad"]},
    "3-C": {"lvl": 72, "energy": 20, "chars": [],                          "ships": ["Outrider"],                      "gear": ["Mk 4 Carbanti Sensor Array Prototype Salvage", "Mk 3 Chiewab Hypo Syringe Prototype Salvage", "Mk 2 SoroSuub Keypad Prototype"]},
    "3-D": {"lvl": 72, "energy": 20, "chars": [],                          "ships": ["Scimitar"],                      "gear": ["Mk 1 Zaltin Bacta Gel Prototype Salvage", "Mk 3 BAW Armor Mod", "Mk 5 A-KT Stun Gun Prototype Salvage"]},
    "3-E": {"lvl": 72, "energy": 20, "chars": [],                          "ships": ["Marauder"],                      "gear": ["Mk 4 Chedak Comlink Prototype Salvage", "Mk 5 TaggeCo Holo Lens Prototype Salvage", "Mk 3 Loronar Power Cell"]},
    # Map 4 (lvl 78, 20 energy)
    "4-A": {"lvl": 78, "energy": 20, "chars": ["Imperial Super Commando"], "ships": ["Gauntlet Starfighter"],          "gear": ["Mk 5 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 2 Merr-Sonn Shield Generator", "Mk 7 BlasTech Weapon Mod Prototype Salvage"]},
    "4-B": {"lvl": 78, "energy": 20, "chars": [],                          "ships": ["TIE Advanced x1"],               "gear": ["Mk 9 Neuro-Saav Electrobinoculars Salvage", "Mk 6 Neuro-Saav Electrobinoculars Prototype Salvage", "Mk 3 TaggeCo Holo Lens Prototype"]},
    "4-C": {"lvl": 78, "energy": 20, "chars": ["Greef Karga"],             "ships": ["Rebel Y-wing"],                  "gear": ["Mk 7 Merr-Sonn Shield Generator Salvage", "Mk 6 TaggeCo Holo Lens Prototype Salvage", "Mk 6 Fabritech Data Pad Salvage"]},
    "4-D": {"lvl": 78, "energy": 20, "chars": [],                          "ships": ["Gungan Phalanx"],                "gear": ["Mk 10 BlasTech Weapon Mod Component", "Mk 1 Carbanti Sensor Array Prototype Salvage", "Mk 4 Chiewab Hypo Syringe Prototype Salvage"]},
    "4-E": {"lvl": 78, "energy": 20, "chars": [],                          "ships": ["TIE Echelon"],                   "gear": ["Mk 5 Loronar Power Cell Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage", "Mk 8 Neuro-Saav Electrobinoculars Salvage"]},
    # Map 5 (lvl 82, 20 energy)
    "5-A": {"lvl": 82, "energy": 20, "chars": ["Shaak Ti"],                "ships": [],                                "gear": ["Mk 10 TaggeCo Holo Lens Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 1 Zaltin Bacta Gel Prototype Salvage"]},
    "5-B": {"lvl": 82, "energy": 20, "chars": ["B1 Battle Droid"],         "ships": [],                                "gear": ["Mk 9 Fabritech Data Pad Salvage", "Mk 1 Chedak Comlink Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage"]},
    "5-C": {"lvl": 82, "energy": 20, "chars": ["Scout Trooper"],           "ships": [],                                "gear": ["Mk 8 BioTech Implant Component", "Mk 6 Fabritech Data Pad Salvage", "Mk 7 BAW Armor Mod Prototype Salvage"]},
    "5-D": {"lvl": 82, "energy": 20, "chars": ["Enfys Nest"],              "ships": [],                                "gear": ["Mk 3 Chiewab Hypo Syringe Prototype Salvage", "Mk 4 Chiewab Hypo Syringe Prototype Salvage", "Mk 10 Neuro-Saav Electrobinoculars Salvage"]},
    "5-E": {"lvl": 82, "energy": 20, "chars": ["The Mandalorian"],         "ships": [],                                "gear": ["Mk 5 Athakam Medpac Salvage", "Mk 4 Nubian Security Scanner Prototype Salvage", "Mk 4 A-KT Stun Gun Salvage"]},
    "5-F": {"lvl": 82, "energy": 20, "chars": [],                          "ships": [],                                "gear": ["Mk 9 Fabritech Data Pad Component", "Mk 2 Zaltin Bacta Gel Prototype Salvage", "Mk 4 Merr-Sonn Thermal Detonator Prototype Salvage"]},
}

# ── FLEET NORMAL (relic-relevant nodes only) ─────────────────────────────────
FLEET_NORMAL_NODES = {
    "2-E": {"lvl": 65, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Fusion Furnace Prototype Salvage", "Mk 5 Nubian Security Scanner Prototype Salvage", "Mk 4 BAW Armor Mod Salvage", "Mk 2 Fabritech Data Pad"], "relic_scrap": ["Gyrda Keypad"]},
    "3-A": {"lvl": 72, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Key Pad Prototype Salvage", "Mk 5 Chiewab Hypo Syringe Prototype Salvage", "Mk 6 TaggeCo Holo Lens Prototype Salvage", "Mk 2 Chedak Comlink Prototype"], "relic_scrap": ["Zinbiddle Card"]},
    "3-E": {"lvl": 72, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Stun Gun Prototype Salvage", "Mk 3 BAW Armor Mod"], "relic_scrap": ["Gyrda Keypad"]},
    "4-E": {"lvl": 78, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Thermal Detonator Prototype Salvage", "Mk 2 Sienar Holo Projector Prototype Salvage", "Mk 1 Zaltin Bacta Gel Prototype Salvage"], "relic_scrap": ["Zinbiddle Card"]},
    "5-A": {"lvl": 82, "energy": 10, "chars": [], "ships": [], "gear": ["Mk 12 ArmaTek Data Pad Prototype Salvage", "Mk 4 Chiewab Hypo Syringe Prototype Salvage"], "relic_scrap": ["Gyrda Keypad"]},
}

# ── RELIC MATERIAL REQUIREMENTS ──────────────────────────────────────────────
# Source: swgoh.wiki/wiki/Relic_Amplifier
RELIC_LEVELS = {
    "R1": {
        "credits": 10000,
        "carbonite_circuit_board": 40,
    },
    "R2": {
        "credits": 25000,
        "fragmented_signal_data": 15,
        "carbonite_circuit_board": 30,
        "bronzium_wiring": 40,
    },
    "R3": {
        "credits": 50000,
        "fragmented_signal_data": 20,
        "incomplete_signal_data": 15,
        "carbonite_circuit_board": 30,
        "bronzium_wiring": 40,
        "chromium_transistor": 20,
    },
    "R4": {
        "credits": 75000,
        "fragmented_signal_data": 20,
        "incomplete_signal_data": 25,
        "carbonite_circuit_board": 30,
        "bronzium_wiring": 40,
        "chromium_transistor": 40,
    },
    "R5": {
        "credits": 100000,
        "fragmented_signal_data": 20,
        "incomplete_signal_data": 25,
        "flawed_signal_data": 15,
        "carbonite_circuit_board": 30,
        "bronzium_wiring": 40,
        "chromium_transistor": 30,
        "aurodium_heatsink": 20,
    },
    "R6": {
        "credits": 250000,
        "fragmented_signal_data": 20,
        "incomplete_signal_data": 25,
        "flawed_signal_data": 25,
        "carbonite_circuit_board": 20,
        "bronzium_wiring": 30,
        "chromium_transistor": 30,
        "aurodium_heatsink": 20,
        "electrium_conductor": 20,
    },
    "R7": {
        "credits": 500000,
        "fragmented_signal_data": 20,
        "incomplete_signal_data": 25,
        "flawed_signal_data": 35,
        "carbonite_circuit_board": 20,
        "bronzium_wiring": 30,
        "chromium_transistor": 20,
        "aurodium_heatsink": 20,
        "electrium_conductor": 20,
        "zinbiddle_card": 10,
    },
    "R8": {
        "credits": 1000000,
        "fragmented_signal_data": 20,
        "incomplete_signal_data": 25,
        "flawed_signal_data": 45,
        "chromium_transistor": 20,
        "aurodium_heatsink": 20,
        "electrium_conductor": 20,
        "zinbiddle_card": 20,
        "impulse_detector": 20,
        "aeromagnifier": 20,
    },
    "R9": {
        "credits": 1500000,
        "incomplete_signal_data": 30,
        "flawed_signal_data": 55,
        "electrium_conductor": 20,
        "zinbiddle_card": 20,
        "impulse_detector": 20,
        "aeromagnifier": 20,
        "gyrda_keypad": 20,
        "droid_brain": 20,
    },
    "R10": {
        "credits": 2000000,
        "incomplete_signal_data": 25,
        "flawed_signal_data": 45,
        "corrupted_signal_data": 15,
        "impulse_detector": 20,
        "aeromagnifier": 20,
        "gyrda_keypad": 20,
        "droid_brain": 20,
        "coaxial_servomotor": 20,
    },
}

# Cumulative totals R1-R10
RELIC_CUMULATIVE = {
    "R1_to_R10": {
        "credits": 5510000,
        "fragmented_signal_data": 135,
        "incomplete_signal_data": 195,
        "flawed_signal_data": 220,
        "corrupted_signal_data": 15,
        "carbonite_circuit_board": 200,
        "bronzium_wiring": 220,
        "chromium_transistor": 180,
        "aurodium_heatsink": 100,
        "electrium_conductor": 80,
        "zinbiddle_card": 50,
        "impulse_detector": 60,
        "aeromagnifier": 60,
        "gyrda_keypad": 40,
        "droid_brain": 40,
        "coaxial_servomotor": 20,
    }
}

# Scrap material farming guide
SCRAP_FARMING = {
    "carbonite_circuit_board": {
        "best_node": "LS Normal 1-C",
        "best_gear": ["Mk 1 BlasTech Weapon Mod", "Mk 1 Nubian Security Scanner", "Mk 1 TaggeCo Holo Lens"],
        "also_from": ["Weekly Shipment (500 crystals/100)", "Gear Challenges (TAC)"],
        "relic_levels": "R1-R7",
    },
    "bronzium_wiring": {
        "best_node": "LS Normal 7-B",
        "best_gear": ["Mk 5 Fabritech Data Pad"],
        "also_from": ["Weekly Shipment (1000 crystals/50)", "Guild Store", "Squad Arena Store"],
        "relic_levels": "R2-R7",
    },
    "chromium_transistor": {
        "best_node": "Guild Store",
        "best_gear": ["Mk 7 BlasTech Weapon Mod (150 Guild Tokens x5)", "Mk 7 BAW Armor Mod", "Mk 7 Loronar Power Cell"],
        "also_from": ["Gear Challenges (AGI, TAC, STR)"],
        "relic_levels": "R3-R8",
    },
    "aurodium_heatsink": {
        "best_node": "Guild Store / Shipments",
        "best_gear": ["Mk 3 Sienar Holo Projector (craft from Salvage, 500 pts each)"],
        "also_from": ["Shipments 300 crystals/ea", "LS Normal 9-F (Salvage drops)"],
        "relic_levels": "R5-R8",
    },
    "electrium_conductor": {
        "best_node": "DS Normal 9-C",
        "best_gear": ["Mk 12 ArmaTek Cybernetics Prototype Salvage (15 pts)", "Mk 12 ArmaTek Wrist Band (DS 9-A)", "Mk 12 ArmaTek Visor (LS 9-E)"],
        "also_from": ["Territory Battles", "The Sith Triumvirate", "Weekly Shipment (1725 crystals/15)", "Guild Activity Store"],
        "relic_levels": "R6-R9",
    },
    "zinbiddle_card": {
        "best_node": "Fleet Normal 3-A",
        "best_gear": ["Mk 12 ArmaTek Key Pad Prototype Salvage (18 pts)", "Mk 12 ArmaTek Thermal Detonator Prototype Salvage (Fleet 4-E)"],
        "also_from": ["Territory Battles", "Guild Activity Store (125 Mk 3 Raid Tokens/ea)", "Championship Store"],
        "relic_levels": "R7-R10",
    },
    "impulse_detector": {
        "best_node": "LS Normal 9-F",
        "best_gear": ["Mk 12 ArmaTek Bayonet Prototype Salvage (12 pts)", "Mk 12 ArmaTek Medpac Prototype Salvage (LS 9-C)", "Mk 12 ArmaTek Multi-tool Prototype Salvage (DS 9-D)"],
        "also_from": ["Territory Battles", "Weekly Shipment (1800 crystals/10)", "Guild Events Store"],
        "relic_levels": "R8-R10",
    },
    "aeromagnifier": {
        "best_node": None,
        "best_gear": [],
        "also_from": ["Guild Events Store (GET1)", "Territory Battles", "Conquest store"],
        "relic_levels": "R8-R10",
        "notes": "No dedicated farmable battle node. Source from GET1 tokens or TB rewards.",
    },
    "gyrda_keypad": {
        "best_node": "Fleet Normal 3-E",
        "best_gear": ["Mk 12 ArmaTek Stun Gun Prototype Salvage (10 pts)", "Mk 12 ArmaTek Data Pad Prototype Salvage (Fleet 5-A)"],
        "also_from": ["Territory Battles", "Territory War", "Weekly Shipment"],
        "relic_levels": "R9-R10",
    },
    "droid_brain": {
        "best_node": None,
        "best_gear": [],
        "also_from": ["Guild Events Store (GET1)", "Territory Battles"],
        "relic_levels": "R9-R10",
        "notes": "No dedicated farmable battle node.",
    },
    "coaxial_servomotor": {
        "best_node": None,
        "best_gear": [],
        "also_from": ["Guild Events Store (GET1)", "Territory Battles"],
        "relic_levels": "R10",
        "notes": "No dedicated farmable battle node.",
    },
    "fragmented_signal_data": {
        "best_node": "Cantina Battles (all nodes)",
        "also_from": ["Cantina Battles store"],
        "relic_levels": "R2-R8",
    },
    "incomplete_signal_data": {
        "best_node": "Cantina Battles 8-C, 8-F, 8-G (highest tier)",
        "also_from": ["Cantina Battles store"],
        "relic_levels": "R3-R10",
    },
    "flawed_signal_data": {
        "best_node": "Cantina Battles 8-C, 8-F, 8-G",
        "also_from": ["Cantina Battles store"],
        "relic_levels": "R5-R10",
    },
    "corrupted_signal_data": {
        "best_node": None,
        "also_from": ["Conquest store"],
        "relic_levels": "R9-R10",
        "notes": "Only available from Conquest store, not farmable on campaign nodes.",
    },
}


# ── BUILD CAMPAIGN_NODES.JSON ─────────────────────────────────────────────────

def build_campaign_node(node_id: str, data: dict, campaign: str, daily_limit: int | None) -> dict:
    return {
        "campaign": campaign,
        "node_id": node_id,
        "level_required": data["lvl"],
        "energy_cost": data["energy"],
        "energy_type": "cantina" if campaign == "cantina" else ("ship" if "fleet" in campaign else "normal"),
        "daily_limit": daily_limit,
        "character_shards": data.get("chars", []),
        "ship_shards": data.get("ships", []),
        "gear_drops": data.get("gear", []),
        "special_drops": data.get("special", []),
        "relic_scrap_use": data.get("relic_scrap", []),
    }


def build_campaign_nodes_json() -> dict:
    campaigns = {}

    # Cantina
    campaigns["cantina"] = {
        "meta": {"energy_type": "cantina", "daily_limit": None, "notes": "No daily attempt limit. 8-C/8-F/8-G drop Omicron ability material + Signal Data only."},
        "nodes": {nid: build_campaign_node(nid, d, "cantina", None) for nid, d in CANTINA_NODES.items()},
    }

    # Light Side Hard
    campaigns["light_side_hard"] = {
        "meta": {"energy_type": "normal", "daily_limit": 5, "notes": "5 attempts/day. Requires Normal completed first. Only Light Side units allowed."},
        "nodes": {nid: build_campaign_node(nid, d, "light_side_hard", 5) for nid, d in LS_HARD_NODES.items()},
    }

    # Light Side Normal (partial - relic-relevant + key nodes)
    campaigns["light_side_normal"] = {
        "meta": {"energy_type": "normal", "daily_limit": None, "notes": "No attempt limit. Only Light Side units. Partial coverage - relic-relevant gear nodes included."},
        "nodes": {nid: build_campaign_node(nid, d, "light_side_normal", None) for nid, d in LS_NORMAL_NODES.items()},
    }

    # Dark Side Hard
    campaigns["dark_side_hard"] = {
        "meta": {"energy_type": "normal", "daily_limit": 5, "notes": "5 attempts/day. Requires Normal completed first. Only Dark Side units allowed."},
        "nodes": {nid: build_campaign_node(nid, d, "dark_side_hard", 5) for nid, d in DS_HARD_NODES.items()},
    }

    # Dark Side Normal (partial)
    campaigns["dark_side_normal"] = {
        "meta": {"energy_type": "normal", "daily_limit": None, "notes": "No attempt limit. Only Dark Side units. Partial coverage - relic-relevant gear nodes included."},
        "nodes": {nid: build_campaign_node(nid, d, "dark_side_normal", None) for nid, d in DS_NORMAL_NODES.items()},
    }

    # Fleet Hard
    campaigns["fleet_hard"] = {
        "meta": {"energy_type": "ship", "daily_limit": 5, "notes": "5 attempts/day. Requires Normal completed first. Ships only."},
        "nodes": {nid: build_campaign_node(nid, d, "fleet_hard", 5) for nid, d in FLEET_HARD_NODES.items()},
    }

    # Fleet Normal (partial)
    campaigns["fleet_normal"] = {
        "meta": {"energy_type": "ship", "daily_limit": None, "notes": "No attempt limit. Ships only. Partial coverage - relic-relevant gear nodes included."},
        "nodes": {nid: build_campaign_node(nid, d, "fleet_normal", None) for nid, d in FLEET_NORMAL_NODES.items()},
    }

    return {
        "version": "2026-05-07",
        "source": "swgoh.wiki",
        "planning_modes": REFRESH_PLAYBOOK["planning_modes"],
        "refresh_playbook": REFRESH_PLAYBOOK,
        "campaigns": campaigns,
    }


# ── BUILD CHARACTER_FARMS.JSON ────────────────────────────────────────────────

def build_character_farms_json(campaign_data: dict) -> dict:
    char_index: dict = defaultdict(lambda: {"campaign_nodes": [], "store_sources": [], "other": []})
    ship_index: dict = defaultdict(lambda: {"campaign_nodes": [], "store_sources": [], "other": []})

    for campaign_id, campaign in campaign_data["campaigns"].items():
        for node_id, node in campaign["nodes"].items():
            entry = {
                "campaign": campaign_id,
                "node": node_id,
                "energy_cost": node["energy_cost"],
                "energy_type": node["energy_type"],
                "daily_limit": node["daily_limit"],
                "level_required": node["level_required"],
            }
            for char in node.get("character_shards", []):
                char_index[char]["campaign_nodes"].append(entry.copy())
            for ship in node.get("ship_shards", []):
                ship_index[ship]["campaign_nodes"].append(entry.copy())

    # Known store sources (not on campaign nodes)
    store_chars = {
        "First Order Officer": ["Cantina Credits Store"],
        "Colonel Starck": ["Cantina Credits Store"],
        "Razor Crest": ["Cantina Credits Store"],  # ship but include in char for searching
    }
    store_ships = {
        "Razor Crest": ["Cantina Credits Store"],
        "Finalizer": ["GET2 (Guild Events Store Tier 2)"],
    }

    for name, sources in store_chars.items():
        char_index[name]["store_sources"].extend(sources)
    for name, sources in store_ships.items():
        ship_index[name]["store_sources"].extend(sources)

    return {
        "version": "2026-05-07",
        "source": "swgoh.wiki + community data",
        "planning_modes": REFRESH_PLAYBOOK["planning_modes"],
        "refresh_playbook": REFRESH_PLAYBOOK,
        "characters": dict(char_index),
        "ships": dict(ship_index),
    }


# ── BUILD RELIC_MATERIALS.JSON ────────────────────────────────────────────────

def build_relic_materials_json() -> dict:
    return {
        "version": "2026-05-07",
        "source": "swgoh.wiki/wiki/Relic_Amplifier",
        "notes": "All quantities are per-level (not cumulative) unless noted. Characters must reach Gear 13 before the Scavenger/relic system unlocks.",
        "planning_modes": REFRESH_PLAYBOOK["planning_modes"],
        "refresh_playbook": REFRESH_PLAYBOOK,
        "per_level": RELIC_LEVELS,
        "cumulative_totals": RELIC_CUMULATIVE,
        "scrap_farming": SCRAP_FARMING,
    }


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    campaign_data = build_campaign_nodes_json()
    farms_data = build_character_farms_json(campaign_data)
    relic_data = build_relic_materials_json()

    campaign_path = DATA_DIR / "campaign_nodes.json"
    farms_path = DATA_DIR / "character_farms.json"
    relic_path = DATA_DIR / "relic_materials.json"

    campaign_path.write_text(json.dumps(campaign_data, indent=2, ensure_ascii=False))
    farms_path.write_text(json.dumps(farms_data, indent=2, ensure_ascii=False))
    relic_path.write_text(json.dumps(relic_data, indent=2, ensure_ascii=False))

    # Stats
    total_nodes = sum(len(c["nodes"]) for c in campaign_data["campaigns"].values())
    total_chars = len(farms_data["characters"])
    total_ships = len(farms_data["ships"])

    print(f"campaign_nodes.json  : {total_nodes} nodes across {len(campaign_data['campaigns'])} campaigns")
    print(f"character_farms.json : {total_chars} characters, {total_ships} ships indexed")
    print(f"relic_materials.json : {len(relic_data['per_level'])} relic levels, {len(relic_data['scrap_farming'])} scrap materials")
    print(f"\nFiles written to {DATA_DIR}/")


if __name__ == "__main__":
    main()
