"""Aggregate timestamped Riot timeline events onto a 64x64 research atlas."""
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .util import atomic_json, read_json

CATEGORIES = ("faker_kill", "faker_death", "ally_kill", "enemy_kill",
              "dragon", "baron", "herald", "grubs", "building", "ward_placed", "ward_cleared")
PHASES = ("early", "middle", "late")


def phase(timestamp: float) -> str:
    minute = timestamp / 60000
    return "early" if minute < 10 else "middle" if minute < 20 else "late"


def event_category(event: dict, pid: int, team_id: int, teams: dict[int, int]) -> str | None:
    kind = event.get("type")
    if kind == "CHAMPION_KILL":
        if event.get("victimId") == pid: return "faker_death"
        if event.get("killerId") == pid: return "faker_kill"
        killer_team = teams.get(int(event.get("killerId") or 0))
        if killer_team == team_id: return "ally_kill"
        if killer_team in (100, 200): return "enemy_kill"
    if kind == "ELITE_MONSTER_KILL":
        monster = str(event.get("monsterType") or "").upper()
        return {"DRAGON": "dragon", "BARON_NASHOR": "baron", "RIFTHERALD": "herald",
                "HORDE": "grubs"}.get(monster)
    if kind == "BUILDING_KILL": return "building"
    if kind == "WARD_PLACED": return "ward_placed"
    if kind == "WARD_KILL": return "ward_cleared"
    return None


def position_cell(event: dict) -> int | None:
    p = event.get("position") or {}
    if p.get("x") is None or p.get("y") is None: return None
    try:
        x = min(63, max(0, int(float(p["x"]) / 15000 * 64)))
        y = min(63, max(0, int(float(p["y"]) / 15000 * 64)))
    except (TypeError, ValueError):
        return None
    return y * 64 + x


def summarize_match(match: dict, timeline: dict, puuid: str) -> dict:
    players = (match.get("info") or {}).get("participants") or []
    own = next((p for p in players if p.get("puuid") == puuid), None)
    if own is None: raise ValueError("Target PUUID absent")
    pid, team_id = int(own.get("participantId") or 0), int(own.get("teamId") or 0)
    teams = {int(p.get("participantId") or 0): int(p.get("teamId") or 0) for p in players}
    cells = {ph: {name: np.zeros(4096, dtype=np.int32) for name in CATEGORIES} for ph in PHASES}
    totals = {ph: Counter() for ph in PHASES}
    missing = {ph: Counter() for ph in PHASES}
    for frame in (timeline.get("info") or {}).get("frames") or []:
        for event in frame.get("events") or []:
            name = event_category(event, pid, team_id, teams)
            if name is None: continue
            ph = phase(float(event.get("timestamp") or frame.get("timestamp") or 0))
            totals[ph][name] += 1
            cell = position_cell(event)
            if cell is None: missing[ph][name] += 1
            else: cells[ph][name][cell] += 1
    return {"cells": cells, "totals": totals, "missing": missing}


def aggregate(limit: int | None = None, output: Path = CONFIG.root / "docs" / "data" / "public_events64.json") -> dict:
    ranked = read_json(CONFIG.raw / "manifest.json")
    ids = ranked["order"][:limit] if limit is not None else ranked["order"]
    sums = {ph: {name: np.zeros(4096, dtype=np.int64) for name in CATEGORIES} for ph in PHASES}
    totals = {ph: Counter() for ph in PHASES}
    missing = {ph: Counter() for ph in PHASES}
    errors = 0
    for mid in tqdm(ids, desc="event atlas", unit="game"):
        try:
            match = json.loads((CONFIG.raw / "matches" / f"{mid}.json").read_text())
            timeline = json.loads((CONFIG.raw / "timelines" / f"{mid}.json").read_text())
            one = summarize_match(match, timeline, ranked["account"]["puuid"])
            for ph in PHASES:
                totals[ph].update(one["totals"][ph])
                missing[ph].update(one["missing"][ph])
                for name in CATEGORIES: sums[ph][name] += one["cells"][ph][name]
        except Exception:
            errors += 1
    report = {"schema_version": 1, "grid": 64, "source_matches": len(ids) - errors, "parse_errors": errors,
              "domain": "same-PUUID KR ranked solo queue 420; aggregate only",
              "note": "Event timestamps may be finer than 60 s; player positions are still sampled around 60 s. Missing event coordinates stay unplaced.",
              "phases": {ph: {name: {"total": totals[ph][name], "without_position": missing[ph][name],
                                    "cells": sums[ph][name].tolist()} for name in CATEGORIES} for ph in PHASES}}
    atomic_json(output, report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    report = aggregate(args.limit)
    print({"matches": report["source_matches"], "parse_errors": report["parse_errors"],
           "totals": {ph: {name: data["total"] for name, data in names.items()} for ph, names in report["phases"].items()}})


if __name__ == "__main__": main()
