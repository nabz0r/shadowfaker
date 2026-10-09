"""Observable one-minute movement tags for Faker, never inferred intent."""
import argparse
import json
import logging
from pathlib import Path

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .features import FEATURE_NAMES, _participant, _save_npz, position, region
from .util import atomic_json, read_json

LOG = logging.getLogger(__name__)
SCHEMA_VERSION = 1
ROLES = ("JUNGLE", "BOTTOM", "UTILITY", "MIDDLE", "TOP")
TAG_NAMES = ("approach_jungle", "approach_bot", "approach_support", "approach_mid",
             "approach_top", "approach_dragon", "approach_baron", "reset_base")
OBJECTIVES = (("dragon_alive", np.array([9866, 4414], dtype=np.float32) / 15000),
              ("baron_alive", np.array([5007, 10471], dtype=np.float32) / 15000))


def _approached(start: np.ndarray, end: np.ndarray, target: np.ndarray) -> bool:
    """At least 1200 units closer and within 4500 units by the next frame."""
    start_distance = float(np.linalg.norm(start - target) * 15000)
    end_distance = float(np.linalg.norm(end - target) * 15000)
    return start_distance - end_distance >= 1200 and end_distance <= 4500


def extract_tags(match: dict, timeline: dict, puuid: str, samples: dict) -> dict:
    pid, team_id, _ = _participant(match, timeline, puuid)
    participants = (match.get("info") or {}).get("participants") or []
    allies = {str(p.get("teamPosition") or ""): int(p.get("participantId") or index + 1)
              for index, p in enumerate(participants)
              if p.get("puuid") != puuid and int(p.get("teamId") or 0) == team_id}
    frames = (timeline.get("info") or {}).get("frames") or []
    labels, masks, regions = [], [], []
    for index, frame in enumerate(frames[:-1]):
        current_frames = frame.get("participantFrames") or {}
        next_frames = frames[index + 1].get("participantFrames") or {}
        nxt = next_frames.get(str(pid)) or next_frames.get(pid) or {}
        end = position(nxt)
        if end is None:
            continue
        own = current_frames.get(str(pid)) or current_frames.get(pid) or {}
        start = position(own)
        row = np.zeros(len(TAG_NAMES), dtype=np.int8)
        valid = np.zeros(len(TAG_NAMES), dtype=np.bool_)
        if start is not None:
            for j, role in enumerate(ROLES):
                ally_id = allies.get(role)
                if ally_id is None:
                    continue
                ally = current_frames.get(str(ally_id)) or current_frames.get(ally_id) or {}
                target = position(ally)
                if target is not None:
                    valid[j] = True
                    row[j] = _approached(start, end, target)
            sample_index = len(labels)
            for offset, (feature, target) in enumerate(OBJECTIVES, start=len(ROLES)):
                if samples["x"][sample_index, -1, FEATURE_NAMES.index(feature)] > .5:
                    valid[offset] = True
                    row[offset] = _approached(start, end, target)
            base = (np.array([400, 400]) if team_id == 100 else np.array([14300, 14300])) / 15000
            valid[-1] = True
            row[-1] = float(np.linalg.norm(end - base) * 15000) <= 1800 and float(np.linalg.norm(start - base) * 15000) > 1800
        labels.append(row)
        masks.append(valid)
        regions.append(region(end))
    if len(labels) != len(samples["region"]) or not np.array_equal(regions, samples["region"]):
        raise ValueError("Macro-tag alignment differs from the supervised region labels")
    return {"tags": np.stack(labels), "valid": np.stack(masks)}


def build(raw: Path = CONFIG.raw, processed: Path = CONFIG.processed, limit: int | None = None) -> dict:
    meta = read_json(processed / "meta.json")
    manifest = read_json(raw / "manifest.json")
    if not meta or not manifest:
        raise FileNotFoundError("Fetched and parsed matches are required")
    output = processed / "macro_actions"
    output.mkdir(parents=True, exist_ok=True)
    prior = read_json(output / "meta.json", {})
    incompatible = (prior.get("schema_version") not in (None, SCHEMA_VERSION)
                    or prior.get("base_schema_version") not in (None, meta["schema_version"])
                    or prior.get("source_puuid") not in (None, manifest["account"]["puuid"]))
    ids = list(meta["counts"])
    if limit is not None:
        ids = ids[:limit]
    errors = {}
    for mid in tqdm(ids, desc="macro action tags", unit="game"):
        path = output / f"{mid}.npz"
        try:
            if incompatible or not path.exists():
                match = read_json(raw / "matches" / f"{mid}.json")
                timeline = read_json(raw / "timelines" / f"{mid}.json")
                with np.load(processed / "matches" / f"{mid}.npz") as arrays:
                    samples = {"x": arrays["x"], "region": arrays["region"]}
                labels = extract_tags(match, timeline, manifest["account"]["puuid"], samples)
                _save_npz(path, labels)
        except Exception as exc:
            LOG.exception("Macro tags failed for %s; continuing", mid)
            errors[mid] = str(exc)
    counts = {name: {"positive": 0, "valid": 0} for name in TAG_NAMES}
    phase_counts = {phase: {name: {"positive": 0, "valid": 0} for name in TAG_NAMES}
                    for phase in ("early_0_10", "mid_10_20", "late_20_plus")}
    usable = []
    for mid in ids:
        if mid in errors:
            continue
        try:
            with np.load(output / f"{mid}.npz") as arrays:
                labels, valid = arrays["tags"], arrays["valid"]
            with np.load(processed / "matches" / f"{mid}.npz") as source:
                minute = source["minute"]
            if len(minute) != len(labels):
                raise ValueError("Macro tags and minute arrays differ in length")
        except Exception as exc:
            LOG.exception("Macro summary failed for %s; continuing", mid)
            errors[mid] = str(exc)
            continue
        for j, name in enumerate(TAG_NAMES):
            counts[name]["valid"] += int(valid[:, j].sum())
            counts[name]["positive"] += int((labels[:, j] * valid[:, j]).sum())
            for phase, selected in (("early_0_10", minute < 10),
                                    ("mid_10_20", (minute >= 10) & (minute < 20)),
                                    ("late_20_plus", minute >= 20)):
                phase_counts[phase][name]["valid"] += int((valid[:, j] & selected).sum())
                phase_counts[phase][name]["positive"] += int((labels[:, j] * valid[:, j] * selected).sum())
        usable.append(mid)
    result = {"schema_version": SCHEMA_VERSION, "base_schema_version": meta["schema_version"],
              "source_puuid": manifest["account"]["puuid"],
              "tag_names": TAG_NAMES, "definition": "One-minute movement proxy: 1200 units closer and within 4500 units of a present ally/live objective; base entry within 1800 units.",
              "matches": len(usable), "source_match_ids": usable, "counts": counts,
              "by_phase": phase_counts, "errors": errors}
    atomic_json(output / "meta.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    result = build(limit=args.limit)
    print(json.dumps({key: value for key, value in result.items() if key != "source_match_ids"}, indent=2))


if __name__ == "__main__":
    main()
