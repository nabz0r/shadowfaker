"""Local sparse 512x512 atlas; no match-level Riot records are published."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sqlite3

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .events64 import CATEGORIES, event_category, phase
from .fine512 import GRID, ARTIFACTS, cell512
from .state_matrix import DB
from .util import atomic_json, read_json

ATLAS = ARTIFACTS / "atlas.json"
PHASES = ("early", "middle", "late")


def _record(counter: Counter, *, total: int | None = None, missing: int = 0) -> dict:
    return {"cells": [[int(index), int(count)] for index, count in sorted(counter.items())],
            "total": int(sum(counter.values()) + missing if total is None else total),
            "without_position": int(missing)}


def build(limit: int | None = None, output: Path = ATLAS,
          evaluation: Path = ARTIFACTS / "evaluation_val.json", db: Path = DB) -> dict:
    report = read_json(evaluation)
    if not report or report.get("grid") != GRID or report.get("status") != "development_validation_only":
        raise FileNotFoundError("Run 512 validation before building its atlas")
    manifest = read_json(CONFIG.raw / "manifest.json")
    if not manifest: raise FileNotFoundError("Ranked manifest missing")
    ids = manifest["order"][:limit] if limit is not None else manifest["order"]
    ranked = set(ids)
    positions = {ph: {"positions_enemy": Counter(), "positions_allies": Counter()} for ph in PHASES}
    event_counts = {ph: {name: Counter() for name in CATEGORIES} for ph in PHASES}
    missing = {ph: Counter() for ph in PHASES}
    totals = {ph: Counter() for ph in PHASES}
    with sqlite3.connect(db) as connection:
        rows = connection.execute("""SELECT s.match_id, s.timestamp_ms, a.side, a.x, a.y
            FROM actors a JOIN states s ON a.match_id=s.match_id AND a.frame_index=s.frame_index
            WHERE a.x IS NOT NULL AND a.y IS NOT NULL AND a.side IN ('ally','enemy')""")
        for mid, timestamp, side, x, y in rows:
            if mid not in ranked: continue
            ph = phase(timestamp)
            key = "positions_enemy" if side == "enemy" else "positions_allies"
            positions[ph][key][int(cell512(np.array([x, y])))] += 1
    errors = {}
    for mid in tqdm(ids, desc="512 event atlas", unit="game"):
        try:
            match = json.loads((CONFIG.raw / "matches" / f"{mid}.json").read_text())
            timeline = json.loads((CONFIG.raw / "timelines" / f"{mid}.json").read_text())
            players = (match.get("info") or {}).get("participants") or []
            own = next(p for p in players if p.get("puuid") == manifest["account"]["puuid"])
            pid = int(own.get("participantId") or 0)
            side = int(own.get("teamId") or 0)
            teams = {int(p.get("participantId") or 0): int(p.get("teamId") or 0) for p in players}
            for frame in (timeline.get("info") or {}).get("frames") or []:
                for event in frame.get("events") or []:
                    name = event_category(event, pid, side, teams)
                    if name is None: continue
                    ph = phase(float(event.get("timestamp") or frame.get("timestamp") or 0))
                    totals[ph][name] += 1
                    pos = event.get("position") or {}
                    try:
                        if pos.get("x") is None or pos.get("y") is None: raise ValueError("no coordinates")
                        point = np.array([float(pos["x"]) / 15000, float(pos["y"]) / 15000])
                        if not np.isfinite(point).all(): raise ValueError("nonfinite coordinates")
                        event_counts[ph][name][int(cell512(point))] += 1
                    except (ValueError, TypeError):
                        missing[ph][name] += 1
        except Exception as exc:
            errors[mid] = str(exc)
    phases = {}
    for ph in PHASES:
        source = report["phases"][ph]
        phases[ph] = {kind: _record(Counter(dict(source[key])), total=source["samples"])
                      for key, kind in (("observed", "positions_real"), ("predicted", "positions_model"))}
        for key in ("positions_enemy", "positions_allies"):
            phases[ph][key] = _record(positions[ph][key])
        for name in CATEGORIES:
            phases[ph][name] = _record(event_counts[ph][name], total=totals[ph][name], missing=missing[ph][name])
    result = {"schema_version": 1, "grid": GRID, "ranked_matches": len(ids) - len(errors),
              "validation_matches": report["matches"], "validation_samples": report["samples"],
              "destination_model": "64x64 frozen parent + learned 8x8 conditional subcell; development validation only",
              "position_step_seconds": "approximately 60", "events_have_timestamps": True,
              "privacy": "local aggregate only; this file is ignored by Git",
              "errors": errors, "phases": phases}
    atomic_json(output, result)
    return result


def main():
    result = build()
    print({"grid": result["grid"], "ranked_matches": result["ranked_matches"],
           "validation_samples": result["validation_samples"], "errors": len(result["errors"])})


if __name__ == "__main__": main()
