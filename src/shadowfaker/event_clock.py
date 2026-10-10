"""Causal ten-second risk windows for marked macro events.

This is an event prediction task, not sub-minute player tracking. Coordinates
on an event describe its locus and must never be called Faker's position.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .events64 import event_category, position_cell
from .features import position, number
from .util import atomic_json, read_json

CLASSES = ("none", "faker_kill", "faker_death", "ally_kill", "enemy_kill",
           "objective", "structure", "ward_placed", "ward_cleared")
ROLES = ("TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY")
HORIZON_MS = 10_000
SCHEMA_VERSION = 2
FEATURES = ("minute", "frame_age", "own_x", "own_y", "own_gold", "own_xp",
            "own_level", "gold_diff", "xp_diff", "nearest_ally", "nearest_enemy",
            *(f"ally_{r.lower()}_distance" for r in ROLES),
            *(f"enemy_{r.lower()}_distance" for r in ROLES),
            *(f"recent_{c}" for c in CLASSES[1:]),
            *(f"age_{c}" for c in CLASSES[1:]))


def mark(event: dict, pid: int, team: int, teams: dict[int, int]) -> int:
    category = event_category(event, pid, team, teams)
    if category in ("dragon", "baron", "herald", "grubs"):
        category = "objective"
    elif category == "building":
        category = "structure"
    try:
        return CLASSES.index(category)
    except ValueError:
        return 0


def _frame_feature(frame: dict, pid: int, team: int, players: list[dict]) -> list[float]:
    pf = frame.get("participantFrames") or {}
    own = pf.get(str(pid)) or pf.get(pid) or {}
    own_pos = position(own)
    own_x, own_y = own_pos if own_pos is not None else (None, None)
    allies, enemies = [], []
    by_role = {("ally", r): 1.0 for r in ROLES}
    by_role.update({("enemy", r): 1.0 for r in ROLES})
    gold = {"ally": 0.0, "enemy": 0.0}
    xp = {"ally": 0.0, "enemy": 0.0}
    for p in players:
        actor_id = int(p.get("participantId") or 0)
        actor = pf.get(str(actor_id)) or pf.get(actor_id) or {}
        side = "ally" if int(p.get("teamId") or 0) == team else "enemy"
        gold[side] += number(actor.get("totalGold"), 0)
        xp[side] += number(actor.get("xp"), 0)
        xy = position(actor)
        if xy is None or own_x is None or own_y is None or actor_id == pid:
            continue
        dist = min(1.0, ((xy[0]-own_x)**2 + (xy[1]-own_y)**2)**0.5 / 2**0.5)
        (allies if side == "ally" else enemies).append(dist)
        role = str(p.get("teamPosition") or p.get("individualPosition") or "").upper()
        if (side, role) in by_role:
            by_role[(side, role)] = dist
    return [0.0, 0.0,
            0.0 if own_x is None else own_x,
            0.0 if own_y is None else own_y,
            number(own.get("totalGold"), 0)/20_000,
            number(own.get("xp"), 0)/30_000,
            number(own.get("level"), 0)/18,
            (gold["ally"]-gold["enemy"])/50_000,
            (xp["ally"]-xp["enemy"])/80_000,
            min(allies, default=1.0), min(enemies, default=1.0),
            *(by_role[("ally", r)] for r in ROLES),
            *(by_role[("enemy", r)] for r in ROLES)]


def extract(match: dict, timeline: dict, puuid: str, horizon_ms: int = HORIZON_MS) -> dict[str, np.ndarray]:
    if horizon_ms <= 0:
        raise ValueError("horizon_ms must be positive")
    info = match.get("info") or {}
    players = info.get("participants") or []
    own = next((p for p in players if p.get("puuid") == puuid), None)
    if own is None:
        raise ValueError("PUUID absent from match")
    pid, team = int(own["participantId"]), int(own["teamId"])
    teams = {int(p.get("participantId") or 0): int(p.get("teamId") or 0) for p in players}
    frames = (timeline.get("info") or {}).get("frames") or []
    frames = sorted(frames, key=lambda f: number(f.get("timestamp"), 0))
    if len(frames) < 2:
        raise ValueError("fewer than two timeline frames")
    frame_times = [int(number(f.get("timestamp"), i*60_000)) for i, f in enumerate(frames)]
    events = []
    for frame in frames:
        for e in frame.get("events") or []:
            kind = mark(e, pid, team, teams)
            if kind:
                ts = int(number(e.get("timestamp"), -1))
                if ts >= 0:
                    events.append((ts, kind, position_cell(e)))
    events.sort(key=lambda x: x[0])
    event_times = [e[0] for e in events]
    rows, labels, cells, target_times, times, frame_indices = [], [], [], [], [], []
    base_cache: dict[int, list[float]] = {}
    for t in range(max(0, frame_times[0]), frame_times[-1]-horizon_ms+1, horizon_ms):
        fi = bisect_right(frame_times, t)-1
        if fi < 0:
            continue
        if fi not in base_cache:
            base_cache[fi] = _frame_feature(frames[fi], pid, team, players)
        base = base_cache[fi].copy()
        base[0] = min(1.0, t/3_600_000)
        base[1] = min(1.0, (t-frame_times[fi])/60_000)
        past_end = bisect_right(event_times, t)
        recent_start = bisect_right(event_times, t-60_000)
        recent = Counter(kind for _, kind, _ in events[recent_start:past_end])
        last = {}
        for ts, kind, _ in events[:past_end]:
            last[kind] = ts
        features = base + [min(1.0, recent[c]/5) for c in range(1,len(CLASSES))]
        features += [min(1.0, (t-last[c])/300_000) if c in last else 1.0 for c in range(1,len(CLASSES))]
        next_idx = past_end
        if next_idx < len(events) and events[next_idx][0] <= t+horizon_ms:
            ts, kind, cell = events[next_idx]
        else:
            ts, kind, cell = -1, 0, None
        rows.append(features)
        labels.append(kind)
        cells.append(-1 if cell is None else cell)
        target_times.append(ts)
        times.append(t)
        frame_indices.append(fi)
    return {"x": np.asarray(rows, dtype=np.float32).reshape(-1,len(FEATURES)),
            "schema_version": np.asarray(SCHEMA_VERSION, dtype=np.int16),
            "y": np.asarray(labels, dtype=np.uint8),
            "event_cell64": np.asarray(cells, dtype=np.int16),
            "event_t_ms": np.asarray(target_times, dtype=np.int32),
            "t_ms": np.asarray(times, dtype=np.int32),
            "frame_index": np.asarray(frame_indices, dtype=np.int16)}


def build(limit: int | None = None, out: Path = CONFIG.root / "data" / "processed" / "event_clock") -> dict:
    manifest = read_json(CONFIG.raw / "manifest.json")
    parent = read_json(CONFIG.processed / "meta.json")
    if not manifest or not parent:
        raise FileNotFoundError("Fetch and parse ranked data first")
    ids = [mid for mid in manifest["order"] if mid in parent["counts"]]
    if limit is not None:
        ids = ids[:limit]
    out.mkdir(parents=True, exist_ok=True)
    counts, errors, splits = Counter(), {}, Counter()
    split_map = {mid: split for split, mids in parent["splits"].items() for mid in mids}
    for mid in tqdm(ids, desc="10s event windows", unit="game"):
        target = out / f"{mid}.npz"
        try:
            valid_cache = False
            if target.exists():
                with np.load(target) as z:
                    valid_cache = "schema_version" in z and int(z["schema_version"]) == SCHEMA_VERSION
                    if valid_cache:
                        y = z["y"]
            if not valid_cache:
                m = read_json(CONFIG.raw / "matches" / f"{mid}.json")
                tl = read_json(CONFIG.raw / "timelines" / f"{mid}.json")
                sample = extract(m, tl, manifest["account"]["puuid"])
                np.savez_compressed(target, **sample)
                y = sample["y"]
            counts.update(Counter(int(x) for x in y))
            splits[split_map[mid]] += len(y)
        except Exception as exc:
            errors[mid] = str(exc)
    report = {"schema_version": SCHEMA_VERSION, "horizon_ms": HORIZON_MS, "classes": CLASSES,
              "features": FEATURES, "matches": len(ids)-len(errors),
              "windows": sum(counts.values()), "class_counts": {CLASSES[k]: v for k,v in sorted(counts.items())},
              "windows_by_split": dict(splits), "errors": errors,
              "source": "Riot match-v5, same PUUID, ranked queue 420",
              "scope": "first marked event in (t,t+10s]; event location is not Faker position"}
    atomic_json(out / "meta.json", report)
    return report


def build_alias(limit: int | None = None, out: Path = CONFIG.root / "data" / "processed" / "event_clock") -> dict:
    aliases = read_json(CONFIG.raw / "aliases" / "manifest.json")
    account = aliases["accounts"]["Hide on bush#61151"]
    puuid = account.get("puuid")
    if not puuid:
        raise ValueError("Run alias_fetch with account provenance first")
    ids = [mid for mid, row in aliases["games"].items()
           if row.get("status") == "ok" and row.get("alias") == "Hide on bush#61151"]
    if limit is not None:
        ids = ids[:limit]
    out.mkdir(parents=True, exist_ok=True)
    counts, errors = Counter(), {}
    for mid in tqdm(ids, desc="EUW attributed event windows", unit="game"):
        try:
            target = out / f"{mid}.npz"
            valid_cache = False
            if target.exists():
                with np.load(target) as z:
                    valid_cache = "schema_version" in z and int(z["schema_version"]) == SCHEMA_VERSION
                    if valid_cache:
                        y = z["y"]
            if not valid_cache:
                m = read_json(CONFIG.raw / "matches" / f"{mid}.json")
                tl = read_json(CONFIG.raw / "timelines" / f"{mid}.json")
                sample = extract(m, tl, puuid)
                np.savez_compressed(target, **sample)
                y = sample["y"]
            counts.update(Counter(int(x) for x in y))
        except Exception as exc:
            errors[mid] = str(exc)
    report = {"schema_version": SCHEMA_VERSION, "domain": "attributed_euw_soloq_2024",
              "account_claim": account["claim"], "source_url": account["source_url"],
              "matches": len(ids)-len(errors), "windows": sum(counts.values()),
              "class_counts": {CLASSES[k]: v for k,v in sorted(counts.items())},
              "errors": errors, "training_use": "optional auxiliary train only; never KR validation/test"}
    atomic_json(out / "alias_meta.json",report)
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int)
    p.add_argument("--alias", action="store_true")
    a = p.parse_args()
    print(json.dumps(build_alias(a.limit) if a.alias else build(a.limit), indent=2))


if __name__ == "__main__":
    main()
