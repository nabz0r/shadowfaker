"""Time-causal item and ten-player context, cached one match at a time.

Riot's minute frame is a god-view observation. The proxy view only refreshes
enemy inventories when an enemy is near an observed ally; it is not fog of war.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .features import FEATURE_NAMES, ROLE_PRIORITY, _participant, number, position, _save_npz
from .interaction_core import NAMES as INTERACTION_NAMES
from .util import atomic_json, read_json

ROOT = CONFIG.root / "data" / "ioc"
HASH_BINS = 32
ACTOR_FIELDS = [*(f"item_bin_{i}" for i in range(HASH_BINS)),
                "item_slots", "item_changes_last_minute", "item_history_known"]
NAMES = [f"p{p}_{field}" for p in range(10) for field in ACTOR_FIELDS]
ITEM_TYPES = {"ITEM_PURCHASED", "ITEM_SOLD", "ITEM_DESTROYED", "ITEM_UNDO"}


def apply_item_event(items: Counter, event: dict) -> bool:
    """Apply one known item lifecycle event; return whether held items changed."""
    kind = event.get("type")
    item = int(event.get("itemId") or 0)
    before = int(event.get("beforeId") or 0)
    after = int(event.get("afterId") or 0)
    if kind == "ITEM_PURCHASED" and item > 0:
        items[item] += 1
        return True
    if kind in ("ITEM_SOLD", "ITEM_DESTROYED") and item > 0:
        if items[item] <= 0:
            return False
        items[item] -= 1
        if not items[item]: del items[item]
        return True
    if kind == "ITEM_UNDO":
        changed = False
        if before > 0 and items[before] > 0:
            items[before] -= 1
            if not items[before]: del items[before]
            changed = True
        if after > 0:
            items[after] += 1
            changed = True
        return changed
    return False


def inventory_snapshots(timeline: dict) -> tuple[list[dict[int, Counter]], list[dict[int, int]]]:
    """Inventory after all events with timestamp <= each frame's timestamp."""
    frames = (timeline.get("info") or {}).get("frames") or []
    events = sorted(((number(e.get("timestamp"), number(f.get("timestamp"), i*60000)), i, j, e)
                     for i, f in enumerate(frames) for j, e in enumerate(f.get("events") or [])
                     if e.get("type") in ITEM_TYPES), key=lambda row: row[:3])
    held = {p: Counter() for p in range(1, 11)}
    history, changes, cursor = [], [], 0
    for i, frame in enumerate(frames):
        now = number(frame.get("timestamp"), i * 60000)
        changed = Counter()
        while cursor < len(events) and events[cursor][0] <= now:
            _, _, _, event = events[cursor]
            participant = int(event.get("participantId") or 0)
            if participant in held and apply_item_event(held[participant], event):
                changed[participant] += 1
            cursor += 1
        history.append({p: state.copy() for p, state in held.items()})
        changes.append(dict(changed))
    return history, changes


def _actor_order(match: dict, timeline: dict, puuid: str) -> tuple[list[int], int]:
    pid, team_id, _ = _participant(match, timeline, puuid)
    players = (match.get("info") or {}).get("participants") or []
    teams = {int(p.get("participantId") or i+1): int(p.get("teamId") or (100 if i < 5 else 200))
             for i, p in enumerate(players)}
    roles = {int(p.get("participantId") or i+1): p.get("teamPosition") or "" for i, p in enumerate(players)}
    if len(teams) < 10: teams = {i: 100 if i <= 5 else 200 for i in range(1, 11)}
    sort_key = lambda p: (ROLE_PRIORITY.get(roles.get(p), 5), p)
    order = [pid] + sorted((p for p in range(1, 11) if p != pid and teams.get(p) == team_id), key=sort_key)
    order += sorted((p for p in range(1, 11) if teams.get(p) != team_id), key=sort_key)
    return order, team_id


def _item_vector(items: Counter, changes: int, known: bool = True) -> np.ndarray:
    result = np.zeros(len(ACTOR_FIELDS), np.float32)
    if not known: return result
    for item, count in items.items():
        result[(item * 2654435761) % HASH_BINS] += min(count, 6) / 6
    result[HASH_BINS] = min(sum(items.values()), 7) / 7
    result[HASH_BINS + 1] = min(changes, 5) / 5
    result[HASH_BINS + 2] = 1
    return result


def match_channels(match: dict, timeline: dict, puuid: str) -> tuple[np.ndarray, np.ndarray]:
    """Oracle and conservative enemy last-seen proxy, one vector per frame."""
    order, team_id = _actor_order(match, timeline, puuid)
    players = (match.get("info") or {}).get("participants") or []
    teams = {int(p.get("participantId") or i+1): int(p.get("teamId") or (100 if i < 5 else 200))
             for i, p in enumerate(players)}
    if len(teams) < 10: teams = {i: 100 if i <= 5 else 200 for i in range(1, 11)}
    frames = (timeline.get("info") or {}).get("frames") or []
    inventories, changes = inventory_snapshots(timeline)
    oracle = np.zeros((len(frames), len(NAMES)), np.float32)
    proxy = np.zeros_like(oracle)
    last_seen: dict[int, np.ndarray] = {}
    for fi, frame in enumerate(frames):
        pf = frame.get("participantFrames") or {}
        positions = {p: position(pf.get(str(p)) or pf.get(p) or {}) for p in range(1, 11)}
        allies = [pos for p, pos in positions.items() if teams.get(p) == team_id and pos is not None]
        for slot, participant in enumerate(order):
            start = slot * len(ACTOR_FIELDS)
            current = _item_vector(inventories[fi][participant], changes[fi].get(participant, 0))
            oracle[fi, start:start+len(ACTOR_FIELDS)] = current
            if teams.get(participant) == team_id:
                proxy[fi, start:start+len(ACTOR_FIELDS)] = current
            elif positions[participant] is not None and any(
                np.linalg.norm(positions[participant] - ally) <= 1600/15000 for ally in allies):
                last_seen[participant] = current.copy()
                proxy[fi, start:start+len(ACTOR_FIELDS)] = current
            elif participant in last_seen:
                remembered = last_seen[participant].copy()
                remembered[HASH_BINS + 1] = 0
                proxy[fi, start:start+len(ACTOR_FIELDS)] = remembered
    return proxy, oracle


def _windows(channels: np.ndarray, frames: list[dict], minutes: np.ndarray, window: int) -> np.ndarray:
    frame_minutes = np.asarray([number(f.get("timestamp"), i*60000)/60000 for i, f in enumerate(frames)])
    result = np.zeros((len(minutes), window, channels.shape[1]), np.float32)
    for sample, minute in enumerate(minutes):
        nearest = int(np.argmin(np.abs(frame_minutes - minute)))
        if abs(frame_minutes[nearest] - minute) > .0005:
            raise ValueError(f"Missing frame for minute {minute}")
        end = nearest + 1
        current = channels[max(0, end-window):end]
        result[sample, -len(current):] = current
    return result


def prepare(limit: int | None = None, output: Path = ROOT) -> dict:
    base_meta = read_json(CONFIG.root / "data" / "interaction" / "meta.json")
    manifest = read_json(CONFIG.raw / "manifest.json")
    if not base_meta or not manifest: raise FileNotFoundError("Parse interaction features first")
    splits = base_meta["splits"]
    ids = splits["train"] + splits["val"] + splits["test"]
    if limit is not None:
        ids = (splits["train"][:3] + splits["val"][:2]) if limit == 5 else ids[:limit]
    output.joinpath("matches").mkdir(parents=True, exist_ok=True)
    counts, errors = {}, {}
    for mid in tqdm(ids, desc="causal item IoC", unit="game"):
        try:
            target = output / "matches" / f"{mid}.npz"
            if not target.exists():
                with np.load(CONFIG.root / "data" / "interaction" / "matches" / f"{mid}.npz") as z:
                    data = {key:z[key] for key in z.files}
                match = json.loads((CONFIG.raw / "matches" / f"{mid}.json").read_text())
                timeline = json.loads((CONFIG.raw / "timelines" / f"{mid}.json").read_text())
                proxy, oracle = match_channels(match, timeline, manifest["account"]["puuid"])
                frames = (timeline.get("info") or {}).get("frames") or []
                for key, channels in (("x",proxy),("x_oracle",oracle)):
                    data[key] = np.concatenate((data[key], _windows(channels, frames, data["minute"], data[key].shape[1])), axis=-1)
                _save_npz(target, data)
            with np.load(target) as z:
                if z["x"].shape[2] != base_meta["feature_dim"] + len(NAMES):
                    raise ValueError("Stale IoC feature width")
                counts[mid] = len(z["x"])
        except Exception as exc:
            errors[mid] = str(exc)
    meta = copy.deepcopy(base_meta)
    meta["schema_version"] = 200 + base_meta["schema_version"]
    meta["feature_names"] = FEATURE_NAMES + INTERACTION_NAMES + NAMES
    meta["feature_dim"] = len(meta["feature_names"])
    meta["item_ioc"] = {"schema_version": 1, "hash_bins": HASH_BINS, "actor_fields": ACTOR_FIELDS,
                         "source": "timeline item events timestamp <= current frame only",
                         "item_slots_semantics": "legacy field name: capped event-derived item quantity, not exact inventory slots",
                         "history_known_semantics": "event ledger processed through t; does not certify complete inventory",
                         "enemy_view": "proximity last-seen proxy, not true fog of war"}
    meta["counts"], meta["errors"] = counts, errors
    meta["observations"] = sum(counts.values())
    meta["splits"] = {split:[mid for mid in splits[split] if mid in counts] for split in ("train","val","test")}
    atomic_json(output / "meta.json", meta)
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    meta = prepare(args.limit)
    print({"matches":len(meta["counts"]), "observations":meta["observations"],
           "features":meta["feature_dim"], "errors":meta["errors"]})


if __name__ == "__main__": main()
