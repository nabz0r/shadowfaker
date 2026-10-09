"""Causal one-minute observations and next-minute labels, one NPZ per match."""
import argparse
from collections import Counter
import json
import logging
import os
from pathlib import Path
import random
import tempfile

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .util import atomic_json, read_json

LOG = logging.getLogger(__name__)
FEATURE_NAMES = (["minute", "own_gold", "own_level", "own_xp", "own_cs", "team_gold", "enemy_gold", "gold_diff",
                  "own_kills", "own_deaths", "dragon_alive", "baron_alive", "herald_alive", "recent_kills", "recent_dragons",
                  "recent_towers", "recent_purchases"] +
                 [f"p{i}_{axis}" for i in range(10) for axis in ("x", "y", "visible", "level", "xp", "cs", "gold")])
FEATURE_DIM = len(FEATURE_NAMES)


def number(value, default=0.0):
    try:
        return float(value if value is not None else default)
    except (TypeError, ValueError):
        return float(default)


def position(frame: dict):
    p = frame.get("position") or frame.get("pos") or {}
    x, y = p.get("x"), p.get("y")
    if x is None or y is None:
        return None
    return np.array([np.clip(number(x) / 15000, 0, 0.99999), np.clip(number(y) / 15000, 0, 0.99999)], dtype=np.float32)


def region(pos: np.ndarray) -> int:
    return int(pos[1] * CONFIG.grid) * CONFIG.grid + int(pos[0] * CONFIG.grid)


def _participant(match: dict, timeline: dict, puuid: str) -> tuple[int, int, int]:
    participants = (match.get("info") or {}).get("participants") or []
    for index, p in enumerate(participants):
        if p.get("puuid") == puuid:
            pid = int(p.get("participantId") or index + 1)
            return pid, int(p.get("teamId") or (100 if pid <= 5 else 200)), int(p.get("championId") or 0)
    for index, p in enumerate((timeline.get("metadata") or {}).get("participants") or []):
        if p == puuid:
            pid = index + 1
            return pid, 100 if pid <= 5 else 200, 0
    raise ValueError("PUUID absent from match participants")


def extract_match(match: dict, timeline: dict, puuid: str, window: int = 8):
    pid, team_id, champion = _participant(match, timeline, puuid)
    participants = (match.get("info") or {}).get("participants") or []
    team_by_pid = {int(p.get("participantId") or i + 1): int(p.get("teamId") or (100 if i < 5 else 200)) for i, p in enumerate(participants)}
    if len(team_by_pid) < 10:
        team_by_pid = {i: 100 if i <= 5 else 200 for i in range(1, 11)}
    order = [pid] + [i for i in range(1, 11) if i != pid and team_by_pid.get(i) == team_id] + [i for i in range(1, 11) if team_by_pid.get(i) != team_id]
    frames = (timeline.get("info") or {}).get("frames") or []
    if len(frames) < 2:
        raise ValueError("Timeline has fewer than two frames")
    states, labels_region, labels_item, labels_skill, prev_regions, minutes = [], [], [], [], [], []
    last_pos = {i: np.zeros(2, dtype=np.float32) for i in range(1, 11)}
    feature_frames = []
    for index, frame in enumerate(frames):
        now = number(frame.get("timestamp"), index * 60000)
        pf = frame.get("participantFrames") or {}
        by_pid = {i: pf.get(str(i)) or pf.get(i) or {} for i in range(1, 11)}
        observed = {}
        for i in range(1, 11):
            pos = position(by_pid[i])
            observed[i] = pos is not None
            if pos is not None:
                last_pos[i] = pos
        own = by_pid[pid]
        ally_gold = sum(number(by_pid[i].get("totalGold")) for i in range(1, 11) if team_by_pid.get(i) == team_id)
        enemy_gold = sum(number(by_pid[i].get("totalGold")) for i in range(1, 11) if team_by_pid.get(i) != team_id)
        # Events are read only through the current timestamp. The next frame is used solely for the label.
        past = [e for f in frames[:index + 1] for e in (f.get("events") or []) if number(e.get("timestamp"), now) <= now]
        recent = [e for e in past if now - 60000 < number(e.get("timestamp"), now) <= now]
        def alive(kind: str, spawn: float, respawn: float, end: float = float("inf")) -> float:
            if now < spawn or now >= end:
                return 0.0
            kills = [number(e.get("timestamp")) for e in past if e.get("type") == "ELITE_MONSTER_KILL" and e.get("monsterType") == kind]
            return float(not kills or now >= max(kills) + respawn)
        own_kills = sum(e.get("type") == "CHAMPION_KILL" and e.get("killerId") == pid for e in past)
        own_deaths = sum(e.get("type") == "CHAMPION_KILL" and e.get("victimId") == pid for e in past)
        vec = [now / 60000 / 50, number(own.get("totalGold")) / 20000, number(own.get("level")) / 18,
               number(own.get("xp")) / 30000, number(own.get("minionsKilled")) / 400,
               ally_gold / 100000, enemy_gold / 100000, (ally_gold - enemy_gold) / 30000,
               own_kills / 20, own_deaths / 20, alive("DRAGON", 300000, 300000),
               alive("BARON_NASHOR", 1200000, 360000), alive("RIFTHERALD", 840000, 360000, 1200000),
               sum(e.get("type") == "CHAMPION_KILL" for e in recent) / 10,
               sum(e.get("type") == "ELITE_MONSTER_KILL" and e.get("monsterType") == "DRAGON" for e in recent),
               sum(e.get("type") == "BUILDING_KILL" for e in recent) / 5,
               sum(e.get("type") == "ITEM_PURCHASED" and e.get("participantId") == pid for e in recent) / 5]
        for i in order:
            player = by_pid[i]
            vec.extend((float(last_pos[i][0]), float(last_pos[i][1]), float(observed[i]),
                        number(player.get("level")) / 18, number(player.get("xp")) / 30000,
                        number(player.get("minionsKilled")) / 400, number(player.get("totalGold")) / 20000))
        feature_frames.append(np.asarray(vec, dtype=np.float32))
        if index + 1 == len(frames):
            continue
        nxt = frames[index + 1]
        nxt_pf = nxt.get("participantFrames") or {}
        nxt_own = nxt_pf.get(str(pid)) or nxt_pf.get(pid) or {}
        target_pos = position(nxt_own)
        if target_pos is None:  # no invented target location
            continue
        next_time = number(nxt.get("timestamp"), (index + 1) * 60000)
        next_events = [e for e in (nxt.get("events") or []) if now < number(e.get("timestamp"), next_time) <= next_time and e.get("participantId") == pid]
        purchases = [int(e.get("itemId") or 0) for e in next_events if e.get("type") == "ITEM_PURCHASED" and e.get("itemId")]
        skills = [int(e.get("skillSlot") or 0) for e in next_events if e.get("type") == "SKILL_LEVEL_UP" and 1 <= int(e.get("skillSlot") or 0) <= 4]
        sequence = np.zeros((window, FEATURE_DIM), dtype=np.float32)
        history = feature_frames[max(0, index - window + 1):index + 1]
        sequence[-len(history):] = history
        states.append(sequence)
        labels_region.append(region(target_pos))
        labels_item.append(purchases[0] if purchases else 0)
        labels_skill.append(skills[0] if skills else 0)
        prev_regions.append(region(last_pos[pid]) if observed[pid] else -1)
        minutes.append(now / 60000)
    if not states:
        raise ValueError("No frames with valid next position")
    return {"x": np.stack(states), "region": np.asarray(labels_region, np.int64),
            "item": np.asarray(labels_item, np.int64), "skill": np.asarray(labels_skill, np.int64),
            "previous": np.asarray(prev_regions, np.int64), "minute": np.asarray(minutes, np.float32),
            "champion": np.full(len(states), champion, np.int64)}


def _save_npz(path: Path, arrays: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as stream:
        temp = Path(stream.name)
    try:
        np.savez_compressed(temp, **arrays)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def parse(raw: Path = CONFIG.raw, processed: Path = CONFIG.processed, limit: int | None = None) -> dict:
    manifest = read_json(raw / "manifest.json")
    if not manifest:
        raise FileNotFoundError("Fetch manifest missing; run fetch first")
    puuid = manifest["account"]["puuid"]
    ids = manifest.get("order") or [i for i, e in manifest["games"].items() if e.get("status") == "ok"]
    if limit is not None:
        ids = ids[:limit]
    processed.mkdir(parents=True, exist_ok=True)
    usable, errors = [], {}
    prior_meta = read_json(processed / "meta.json", {})
    incompatible_cache = prior_meta.get("schema_version") not in (None, CONFIG.schema_version)
    for match_id in tqdm(ids, desc="parse matches", unit="game"):
        path = processed / "matches" / f"{match_id}.npz"
        try:
            if incompatible_cache or not path.exists():
                match = json.loads((raw / "matches" / f"{match_id}.json").read_text())
                timeline = json.loads((raw / "timelines" / f"{match_id}.json").read_text())
                arrays = extract_match(match, timeline, puuid, CONFIG.window)
                _save_npz(path, arrays)
            usable.append(match_id)
        except Exception as exc:
            LOG.exception("Parsing failed for %s; continuing", match_id)
            errors[match_id] = str(exc)
    if len(usable) < 3:
        raise ValueError(f"Need at least 3 parsed matches for train/val/test, got {len(usable)}")
    rng = random.Random(CONFIG.seed)
    shuffled = sorted(usable)
    rng.shuffle(shuffled)
    n_test = max(1, round(len(usable) * .1))
    n_val = max(1, round(len(usable) * .1))
    split = {"test": shuffled[:n_test], "val": shuffled[n_test:n_test + n_val], "train": shuffled[n_test + n_val:]}
    if not split["train"]:
        raise ValueError("Train split empty")
    items, regions, skills = Counter(), Counter(), Counter()
    counts = {}
    for match_id in usable:
        with np.load(processed / "matches" / f"{match_id}.npz") as z:
            counts[match_id] = int(len(z["region"]))
            if match_id in split["train"]:
                items.update(int(x) for x in z["item"] if x)
                regions.update(int(x) for x in z["region"])
                skills.update(int(x) for x in z["skill"])
    item_vocab = {str(item): i + 2 for i, (item, _) in enumerate(items.most_common())}
    # 0=no purchase, 1=unknown item; vocabulary is fitted on train matches only.
    freq = np.array([regions.get(i, 0) for i in range(256)], dtype=float)
    weights = np.sqrt((freq.sum() + 256) / (freq + 1))
    weights = np.clip(weights / np.mean(weights[freq > 0]), .25, 8).tolist()
    meta = {"schema_version": CONFIG.schema_version, "seed": CONFIG.seed, "window": CONFIG.window,
            "feature_names": FEATURE_NAMES, "feature_dim": FEATURE_DIM, "grid": CONFIG.grid,
            "splits": split, "counts": counts, "item_vocab": item_vocab, "region_weights": weights,
            "train_event_counts": {"items": dict(items), "skills": dict(skills)}, "errors": errors,
            "observations": sum(counts.values())}
    atomic_json(processed / "meta.json", meta)
    return meta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    result = parse(limit=args.limit)
    print(f"Parsed {len(result['counts'])} games, {result['observations']} observations; errors={len(result['errors'])}")


if __name__ == "__main__":
    main()
