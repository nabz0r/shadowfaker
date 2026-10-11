"""Audited, causal Faker action windows. Raw match details remain local.

The contract distinguishes invalid evidence from a genuine negative label.
Identical Riot events are counted but not deduplicated: two consumables or
ward records may share a timestamp and the target is binary per window.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .event_clock import (FEATURES, HORIZON_MS, SCHEMA_VERSION as CLOCK_SCHEMA,
                          extract as clock_extract)
from .faker_actions import CLASSES, extract as action_labels
from .features import position, number
from .util import atomic_json, read_json

SCHEMA_VERSION = 2
DATA = CONFIG.processed / "faker_actions_sanitized_10s"
EXTRAS = ("own_current_gold", "own_unspent_gold_fraction", "own_cs",
          "own_jungle_cs", "own_health_fraction", "own_position_observed",
          "own_gold_delta_frame", "own_xp_delta_frame", "own_cs_delta_frame",
          "own_move_delta_frame", "distance_to_own_nexus")
FEATURE_NAMES = tuple(FEATURES) + EXTRAS
ATTRIBUTION_FIELDS = {"ITEM_PURCHASED": "participantId", "SKILL_LEVEL_UP": "participantId",
                      "WARD_PLACED": "creatorId", "WARD_KILL": "killerId",
                      "CHAMPION_KILL": "victimId"}


def audit_match(match: dict, timeline: dict, mid: str, puuid: str) -> dict:
    """Hard failures quarantine a match; soft anomalies are counted only."""
    reasons, counts = [], Counter()
    info, ti = match.get("info") or {}, timeline.get("info") or {}
    players, frames = info.get("participants") or [], ti.get("frames") or []
    if (match.get("metadata") or {}).get("matchId") != mid or (timeline.get("metadata") or {}).get("matchId") != mid:
        reasons.append("match_id_mismatch")
    if info.get("queueId") != 420 or number(info.get("gameDuration"), 0) < 300:
        reasons.append("not_complete_ranked_solo")
    pids = [p.get("participantId") for p in players]
    if len(players) != 10 or set(pids) != set(range(1, 11)):
        reasons.append("participant_roster_invalid")
    targets = [p for p in players if p.get("puuid") == puuid]
    if len(targets) != 1:
        reasons.append("target_identity_invalid")
    target_pid = targets[0].get("participantId") if len(targets) == 1 else None
    times = [f.get("timestamp") for f in frames]
    if (len(times) < 2 or any(type(t) is not int or t < 0 for t in times)
            or any(a >= b for a, b in zip(times, times[1:]))):
        reasons.append("frame_clock_invalid")
        last = None
    else:
        last = times[-1]
        if last < 300_000 or abs(last / 1000 - number(info.get("gameDuration"), 0)) > 90:
            reasons.append("duration_frame_mismatch")
    if target_pid is not None:
        for frame in frames:
            own = _own(frame, target_pid)
            if not own:
                counts["missing_target_frame"] += 1
            elif position(own) is None:
                counts["missing_target_position"] += 1
    seen: set[str] = set()
    for frame in frames:
        for event in frame.get("events") or []:
            counts["events"] += 1
            kind = event.get("type")
            if kind not in ATTRIBUTION_FIELDS:
                continue
            counts["targetable_events"] += 1
            ts = event.get("timestamp")
            if type(ts) is not int or ts < 0 or (last is not None and ts > last):
                counts["invalid_targetable_timestamps"] += 1
                reasons.append("targetable_event_clock_invalid")
            actor = event.get(ATTRIBUTION_FIELDS[kind])
            # Riot uses participant 0 for system events, notably starting items
            # and environmental wards. It is not a missing Faker identifier.
            if actor is None:
                counts["missing_targetable_actor"] += 1
                reasons.append("targetable_actor_missing")
            elif actor == 0:
                counts["system_actor_zero"] += 1
            elif type(actor) is not int or actor not in range(1, 11):
                counts["invalid_targetable_actor"] += 1
                reasons.append("targetable_actor_invalid")
            if kind == "CHAMPION_KILL":
                assistants = event.get("assistingParticipantIds") or []
                if (not isinstance(assistants, list)
                        or any(type(a) is not int or a not in range(1, 11) for a in assistants)):
                    counts["invalid_assist_roster"] += 1
                    reasons.append("assist_roster_invalid")
            if target_pid is not None and actor == target_pid:
                counts["faker_events"] += 1
            signature = json.dumps(event, sort_keys=True, separators=(",", ":"))
            if signature in seen:
                counts["identical_event_records"] += 1
            seen.add(signature)
    if last is not None:
        counts["frames"] = len(frames)
        counts["last_frame_ms"] = last
    return {"eligible": not reasons, "reasons": sorted(set(reasons)),
            "counts": dict(counts), "participant_id": target_pid}


def _digest(*paths: Path) -> str:
    h = hashlib.sha256()
    for path in paths:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                h.update(chunk)
    return h.hexdigest()


def _own(frame: dict, pid: int) -> dict:
    pf = frame.get("participantFrames") or {}
    return pf.get(str(pid)) or pf.get(pid) or {}


def extra_features(frames: list[dict], frame_indices: np.ndarray, pid: int,
                   team_id: int) -> np.ndarray:
    """Only the last observed frame and its predecessor may enter state t."""
    base = np.zeros((len(frames), len(EXTRAS)), dtype=np.float32)
    nexus = (1000 / 15000, 1000 / 15000) if team_id == 100 else (14000 / 15000, 14000 / 15000)
    for i, frame in enumerate(frames):
        now, prev = _own(frame, pid), _own(frames[i - 1], pid) if i else {}
        gold = max(0, number(now.get("currentGold"), 0))
        total = max(0, number(now.get("totalGold"), 0))
        cs = max(0, number(now.get("minionsKilled"), 0))
        xp = max(0, number(now.get("xp"), 0))
        xy, old_xy = position(now), position(prev)
        stats = now.get("championStats") or {}
        hp, hpmax = number(stats.get("health"), 0), number(stats.get("healthMax"), 0)
        base[i] = (min(1, gold / 5000), min(1, gold / max(total, 1)),
                   min(1, cs / 400), min(1, number(now.get("jungleMinionsKilled"), 0) / 300),
                   max(0, min(1, hp / hpmax)) if hpmax > 0 else 0,
                   float(xy is not None),
                   max(-1, min(1, (total - number(prev.get("totalGold"), total)) / 3000)) if i else 0,
                   max(-1, min(1, (xp - number(prev.get("xp"), xp)) / 4000)) if i else 0,
                   max(-1, min(1, (cs - number(prev.get("minionsKilled"), cs)) / 80)) if i else 0,
                   min(1, math.dist(xy, old_xy) / math.sqrt(2)) if xy is not None and old_xy is not None else 0,
                   min(1, math.dist(xy, nexus) / math.sqrt(2)) if xy is not None else 1)
    return base[np.asarray(frame_indices, dtype=np.int64)]


def _atomic_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as file:
        tmp = Path(file.name)
    try:
        np.savez_compressed(tmp, **arrays)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def build(*, pilot: bool = False, out: Path = DATA) -> dict:
    manifest = read_json(CONFIG.raw / "manifest.json")
    parent = read_json(CONFIG.processed / "meta.json")
    if not manifest or not parent:
        raise FileNotFoundError("Ranked cache and match split required")
    splits = parent["splits"]
    ids = splits["train"][:3] + splits["val"][:2] if pilot else [
        mid for mid in manifest["order"] if mid in parent["counts"]]
    split_map = {mid: split for split, mids in splits.items() for mid in mids}
    counts, anomaly_counts, reasons, per_match = Counter(), Counter(), Counter(), {}
    out.mkdir(parents=True, exist_ok=True)
    for mid in tqdm(ids, desc="Audit Faker 10s", unit="game"):
        game_path = CONFIG.raw / "matches" / f"{mid}.json"
        timeline_path = CONFIG.raw / "timelines" / f"{mid}.json"
        target = out / f"{mid}.npz"
        try:
            match, timeline = read_json(game_path), read_json(timeline_path)
            audit = audit_match(match, timeline, mid, manifest["account"]["puuid"])
            anomaly_counts.update({k: v for k, v in audit["counts"].items() if k not in ("frames", "last_frame_ms")})
            if not audit["eligible"]:
                reasons.update(audit["reasons"])
                per_match[mid] = {"status": "quarantined", "reasons": audit["reasons"]}
                continue
            source_hash = _digest(game_path, timeline_path)
            cached = False
            if target.exists():
                try:
                    with np.load(target) as z:
                        cached = (int(z["schema_version"]) == SCHEMA_VERSION
                                  and str(z["source_sha256"]) == source_hash
                                  and int(z["horizon_ms"]) == HORIZON_MS)
                        if cached:
                            y = z["y"]
                except (OSError, KeyError, ValueError):
                    cached = False
            if not cached:
                source = clock_extract(match, timeline, manifest["account"]["puuid"])
                x, t_ms, fi = source["x"], source["t_ms"], source["frame_index"]
                frames = timeline["info"]["frames"]
                if len(fi) != len(t_ms) or len(x) != len(t_ms) or (len(fi) and int(fi.max()) >= len(frames)):
                    raise ValueError("event_clock window alignment invalid")
                if len(t_ms) and (np.any(np.diff(t_ms) != HORIZON_MS)
                                  or np.any(t_ms + HORIZON_MS > frames[-1]["timestamp"])):
                    raise ValueError("event_clock horizon invalid")
                extra = extra_features(frames, fi, int(audit["participant_id"]),
                                       int(next(p["teamId"] for p in match["info"]["participants"]
                                                if p["participantId"] == audit["participant_id"])))
                labels = action_labels(timeline, int(audit["participant_id"]), t_ms)
                x = np.concatenate([x, extra], axis=1)
                y = labels["y"]
                _atomic_npz(target, x=x, t_ms=t_ms, y=y, first_delay_ms=labels["first_delay_ms"],
                            frame_index=fi, schema_version=np.asarray(SCHEMA_VERSION),
                            horizon_ms=np.asarray(HORIZON_MS), source_sha256=np.asarray(source_hash))
            counts["matches"] += 1
            counts["windows"] += len(y)
            counts[f"split_{split_map[mid]}"] += len(y)
            counts["cache_hits" if cached else "rebuilt"] += 1
            for c, name in enumerate(CLASSES):
                counts[f"positive_{name}"] += int(y[:, c].sum())
            per_match[mid] = {"status": "eligible", "windows": len(y),
                              "source_sha256": source_hash}
        except Exception as exc:
            reasons["processing_error"] += 1
            per_match[mid] = {"status": "quarantined", "reasons": [str(exc)]}
    counts["quarantined_matches"] = sum(row["status"] == "quarantined" for row in per_match.values())
    public = {"schema_version": SCHEMA_VERSION, "clock_schema": CLOCK_SCHEMA,
              "horizon_ms": HORIZON_MS, "features": FEATURE_NAMES, "classes": CLASSES,
              "pilot": pilot, "counts": dict(counts), "anomalies": dict(anomaly_counts),
              "quarantine_reasons": dict(reasons),
              "policy": "quarantine uncertain matches; participant 0 is system; identical records retained for binary labels"}
    atomic_json(out / "meta.json", public)
    atomic_json(out / "private_manifest.json", per_match)
    return public
