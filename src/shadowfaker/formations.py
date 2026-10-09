"""Descriptive ally clustering around the bot carry in Riot timelines.

This is a coverage audit for unusual formations, not a bot-lane detector or
counterfactual estimate. Only aggregate counts are suitable for publication.
"""
import argparse
from collections import Counter
import json
import logging
from pathlib import Path

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .features import position
from .util import atomic_json, read_json

LOG = logging.getLogger(__name__)
SCHEMA_VERSION = 1
RADIUS_UNITS = 2500
PHASES = ("early_3_10", "mid_10_20", "late_20_plus")


def extract(match: dict, timeline: dict, puuid: str) -> dict:
    participants = (match.get("info") or {}).get("participants") or []
    own = next((p for p in participants if p.get("puuid") == puuid), None)
    if own is None:
        raise ValueError("Target account absent from match")
    allies = [p for p in participants if p.get("teamId") == own.get("teamId")]
    if len(allies) != 5:
        raise ValueError("Expected five allied participants")
    bot = next((p for p in allies if p.get("teamPosition") == "BOTTOM"), None)
    if bot is None:
        raise ValueError("Bot carry role unavailable")
    bot_id = int(bot["participantId"])
    ally_ids = [int(p["participantId"]) for p in allies]
    out = {phase: Counter(valid=0, at_least_3=0, at_least_4=0, all_5=0) for phase in PHASES}
    early_five = False
    for frame in (timeline.get("info") or {}).get("frames") or []:
        minute = float(frame.get("timestamp") or 0) / 60000
        if minute < 3:
            continue  # Avoid the opening fountain cluster.
        phase = PHASES[0] if minute < 10 else PHASES[1] if minute < 20 else PHASES[2]
        by_id = frame.get("participantFrames") or {}
        places = {pid: position(by_id.get(str(pid)) or by_id.get(pid) or {}) for pid in ally_ids}
        if any(value is None for value in places.values()):
            continue
        anchor = places[bot_id]
        nearby = sum(float(np.linalg.norm(places[pid] - anchor) * 15000) <= RADIUS_UNITS
                     for pid in ally_ids)
        out[phase]["valid"] += 1
        for threshold, key in ((3, "at_least_3"), (4, "at_least_4"), (5, "all_5")):
            out[phase][key] += int(nearby >= threshold)
        if phase == PHASES[0] and nearby == 5:
            early_five = True
    return {"schema_version": SCHEMA_VERSION,
            "by_phase": {phase: dict(out[phase]) for phase in PHASES},
            "match_has_early_five": early_five}


def build(raw: Path = CONFIG.raw, processed: Path = CONFIG.processed,
          limit: int | None = None) -> dict:
    manifest = read_json(raw / "manifest.json")
    if not manifest:
        raise FileNotFoundError("Fetch manifest missing")
    ids = list(manifest.get("order") or [])
    if limit is not None:
        ids = ids[:limit]
    output = processed / "formations"
    (output / "matches").mkdir(parents=True, exist_ok=True)
    sums = {phase: Counter(valid=0, at_least_3=0, at_least_4=0, all_5=0) for phase in PHASES}
    errors = {}
    early_five_matches = 0
    completed = 0
    for mid in tqdm(ids, desc="formation audit", unit="game"):
        try:
            path = output / "matches" / f"{mid}.json"
            row = read_json(path)
            if not row or row.get("schema_version") != SCHEMA_VERSION:
                match = json.loads((raw / "matches" / f"{mid}.json").read_text())
                timeline = json.loads((raw / "timelines" / f"{mid}.json").read_text())
                row = extract(match, timeline, manifest["account"]["puuid"])
                atomic_json(path, row)
            for phase in PHASES:
                sums[phase].update(row["by_phase"][phase])
            early_five_matches += int(row["match_has_early_five"])
            completed += 1
        except Exception as exc:
            LOG.exception("Formation audit failed for %s; continuing", mid)
            errors[mid] = str(exc)
    result = {"schema_version": SCHEMA_VERSION, "definition":
              "At minutes >=3, count allied champions within 2500 game units of the bot carry, including the carry; all five positions must be present. This is not a bot-lane detector.",
              "matches": completed, "matches_with_early_all_five": early_five_matches,
              "by_phase": {phase: dict(sums[phase]) for phase in PHASES}, "errors": errors}
    atomic_json(output / "meta.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    result = build(limit=args.limit)
    print(json.dumps({key: value for key, value in result.items() if key != "errors"}, indent=2))


if __name__ == "__main__":
    main()
