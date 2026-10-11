"""Causal, Faker-attributed ten-second event labels from cached Riot timelines.

These are observed API events. Kills, deaths and assists are outcomes, not
intentions; event coordinates are never interpreted as Faker's position.
"""
from __future__ import annotations

from bisect import bisect_right
from collections import Counter
import os
from pathlib import Path
import tempfile

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .util import atomic_json, read_json

SCHEMA_VERSION = 1
HORIZON_MS = 10_000
CLASSES = ("purchase", "skill_point", "ward_placed", "ward_cleared",
           "kill", "death", "assist")
EVENT_DATA = CONFIG.processed / "event_clock"
DATA = CONFIG.processed / "faker_actions_10s"


def attributed(event: dict, pid: int) -> tuple[str, ...]:
    """Return only explicit Faker attribution; skip inferred/automatic events."""
    kind = event.get("type")
    if kind == "ITEM_PURCHASED" and event.get("participantId") == pid:
        return ("purchase",)
    if kind == "SKILL_LEVEL_UP" and event.get("participantId") == pid:
        return ("skill_point",)
    if kind == "WARD_PLACED" and event.get("creatorId") == pid:
        return ("ward_placed",)
    if kind == "WARD_KILL" and event.get("killerId") == pid:
        return ("ward_cleared",)
    if kind == "CHAMPION_KILL":
        if event.get("victimId") == pid:
            return ("death",)
        if event.get("killerId") == pid:
            return ("kill",)
        if pid in (event.get("assistingParticipantIds") or []):
            return ("assist",)
    return ()


def extract(timeline: dict, pid: int, t_ms: np.ndarray) -> dict[str, np.ndarray]:
    """Label events in (t,t+10s], preserving first-event delay per class."""
    by_class: dict[str, list[int]] = {name: [] for name in CLASSES}
    for frame in (timeline.get("info") or {}).get("frames") or []:
        for event in frame.get("events") or []:
            try:
                timestamp = int(event["timestamp"])
            except (KeyError, TypeError, ValueError):
                continue
            if timestamp < 0:
                continue
            for name in attributed(event, pid):
                by_class[name].append(timestamp)
    y = np.zeros((len(t_ms), len(CLASSES)), dtype=np.uint8)
    delay = np.full((len(t_ms), len(CLASSES)), -1, dtype=np.int16)
    for c, name in enumerate(CLASSES):
        times = sorted(by_class[name])
        for i, t in enumerate(t_ms):
            j = bisect_right(times, int(t))
            if j < len(times) and times[j] <= int(t) + HORIZON_MS:
                y[i, c] = 1
                delay[i, c] = times[j] - int(t)
    return {"y": y, "first_delay_ms": delay,
            "event_counts": np.asarray([len(by_class[name]) for name in CLASSES], dtype=np.int32)}


def _atomic_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as tmp:
        temporary = Path(tmp.name)
    try:
        np.savez_compressed(temporary, **arrays)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build(*, pilot: bool = False, out: Path = DATA) -> dict:
    manifest = read_json(CONFIG.raw / "manifest.json")
    parent = read_json(CONFIG.processed / "meta.json")
    if not manifest or not parent:
        raise FileNotFoundError("Ranked cache and match split required")
    splits = parent["splits"]
    ids = (splits["train"][:3] + splits["val"][:2]) if pilot else [
        mid for mid in manifest["order"] if mid in parent["counts"]]
    counts, events, errors = Counter(), Counter(), {}
    split_map = {mid: split for split, mids in splits.items() for mid in mids}
    for mid in tqdm(ids, desc="Faker 10s actions", unit="game"):
        target = out / f"{mid}.npz"
        try:
            if target.exists():
                with np.load(target) as z:
                    if int(z["schema_version"]) == SCHEMA_VERSION and int(z["horizon_ms"]) == HORIZON_MS:
                        y, event_counts = z["y"], z["event_counts"]
                    else:
                        raise KeyError("old schema")
            else:
                raise KeyError("not cached")
        except (OSError, KeyError, ValueError):
            try:
                match = read_json(CONFIG.raw / "matches" / f"{mid}.json")
                timeline = read_json(CONFIG.raw / "timelines" / f"{mid}.json")
                own = next(p for p in match["info"]["participants"]
                           if p.get("puuid") == manifest["account"]["puuid"])
                with np.load(EVENT_DATA / f"{mid}.npz") as z:
                    x, t_ms = z["x"], z["t_ms"]
                sample = extract(timeline, int(own["participantId"]), t_ms)
                y, event_counts = sample["y"], sample["event_counts"]
                _atomic_npz(target, x=x, t_ms=t_ms, **sample,
                            schema_version=np.asarray(SCHEMA_VERSION),
                            horizon_ms=np.asarray(HORIZON_MS))
            except Exception as exc:
                errors[mid] = str(exc)
                continue
        counts["matches"] += 1
        counts["windows"] += len(y)
        counts[f"split_{split_map[mid]}"] += len(y)
        counts["any_action_or_outcome"] += int(y.any(axis=1).sum())
        for c, name in enumerate(CLASSES):
            counts[f"positive_{name}"] += int(y[:, c].sum())
            events[name] += int(event_counts[c])
    report = {"schema_version": SCHEMA_VERSION, "horizon_ms": HORIZON_MS,
              "classes": CLASSES, "pilot": pilot, "counts": dict(counts),
              "source_event_counts": dict(events), "errors": errors,
              "target": "Faker-attributed event in (t,t+10s] per family; multilabel",
              "limits": "kills/deaths/assists are outcomes; no second-scale player position"}
    atomic_json(out / "meta.json", report)
    return report
