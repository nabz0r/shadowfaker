"""Audit the genuine second-scale evidence in cached Riot timelines.

Event timestamps and loci are distinct from sampled player positions. This
module publishes aggregate observability only, never match-level traces.
"""
from __future__ import annotations

from bisect import bisect_right
from collections import Counter
import json
from pathlib import Path
import statistics

from tqdm import tqdm

from .config import CONFIG
from .events64 import event_category
from .util import atomic_json, read_json

HORIZONS_S = (1, 5, 10, 30)
PUBLIC = CONFIG.root / "docs" / "data" / "public_second_scale.json"


def strict_xy(point: object) -> tuple[float, float] | None:
    """Return normalized continuous coordinates without inventing missing data."""
    if not isinstance(point, dict):
        return None
    try:
        x, y = float(point["x"]), float(point["y"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (0 <= x <= 15_000 and 0 <= y <= 15_000):
        return None
    return x / 15_000, y / 15_000


def summarize_match(match: dict, timeline: dict, puuid: str) -> dict:
    players = (match.get("info") or {}).get("participants") or []
    own = next((row for row in players if row.get("puuid") == puuid), None)
    if own is None:
        raise ValueError("Target PUUID absent from match")
    pid, team = int(own["participantId"]), int(own["teamId"])
    teams = {int(row["participantId"]): int(row["teamId"]) for row in players}
    frames = sorted((timeline.get("info") or {}).get("frames") or [],
                    key=lambda frame: int(frame.get("timestamp") or 0))
    if len(frames) < 2:
        raise ValueError("At least two timestamped frames are required")
    anchors, player_anchors, events, categories = [], 0, [], Counter()
    timed, located, off_frame, involved, involved_located = 0, 0, 0, 0, 0
    frame_times = {int(frame.get("timestamp") or 0) for frame in frames}
    for frame in frames:
        t = int(frame.get("timestamp") or 0)
        pf = frame.get("participantFrames") or {}
        for row in pf.values():
            if strict_xy((row or {}).get("position")) is not None:
                player_anchors += 1
        own_frame = pf.get(str(pid)) or pf.get(pid) or {}
        if strict_xy(own_frame.get("position")) is not None:
            anchors.append(t)
        for event in frame.get("events") or []:
            raw_t = event.get("timestamp")
            if raw_t is None:
                continue
            try:
                event_t = int(raw_t)
            except (TypeError, ValueError):
                continue
            if event_t < 0:
                continue
            timed += 1
            category = event_category(event, pid, team, teams)
            if category is None and event.get("type") in ("ITEM_PURCHASED", "SKILL_LEVEL_UP"):
                category = str(event["type"]).lower()
            if category:
                categories[category] += 1
            xy = strict_xy(event.get("position"))
            located += xy is not None
            off_frame += event_t not in frame_times
            related = pid in (event.get("participantId"), event.get("killerId"),
                              event.get("victimId"), event.get("creatorId")) or \
                      pid in (event.get("assistingParticipantIds") or [])
            involved += related
            involved_located += bool(related and xy is not None)
            events.append((event_t, bool(related), bool(category in ("faker_kill", "faker_death"))))
    anchors = sorted(set(anchors))
    gaps = [b - a for a, b in zip(anchors, anchors[1:]) if b > a]
    events.sort()
    event_times = [row[0] for row in events]
    # Prefix sums count events in (t, t+h] without changing the sampled state.
    prefix_related, prefix_combat = [0], [0]
    for _, related, combat in events:
        prefix_related.append(prefix_related[-1] + int(related))
        prefix_combat.append(prefix_combat[-1] + int(combat))
    horizon = {}
    for seconds in HORIZONS_S:
        windows = any_event = faker_event = faker_combat = new_position = 0
        for i, t in enumerate(anchors[:-1]):
            limit = t + seconds * 1000
            if limit > anchors[-1]:
                continue
            windows += 1
            lo, hi = bisect_right(event_times, t), bisect_right(event_times, limit)
            any_event += hi > lo
            faker_event += prefix_related[hi] > prefix_related[lo]
            faker_combat += prefix_combat[hi] > prefix_combat[lo]
            new_position += anchors[i + 1] <= limit
        horizon[str(seconds)] = {"windows": windows, "with_event": any_event,
                                 "with_faker_involvement": faker_event,
                                 "with_faker_combat": faker_combat,
                                 "with_new_faker_position": new_position}
    return {"faker_position_anchors": len(anchors), "player_position_anchors": player_anchors,
            "faker_position_gaps_ms": gaps, "timestamped_events": timed,
            "located_event_loci": located, "events_off_frame": off_frame,
            "faker_involved_events": involved, "faker_involved_located_loci": involved_located,
            "event_categories": categories, "horizons": horizon}


def build(limit: int | None = None, output: Path = PUBLIC) -> dict:
    manifest = read_json(CONFIG.raw / "manifest.json")
    meta = read_json(CONFIG.processed / "meta.json")
    if not manifest or not meta:
        raise FileNotFoundError("Cached ranked matches and parsed metadata are required")
    ids = [mid for mid in manifest["order"] if mid in meta["counts"]]
    if limit is not None:
        ids = ids[:limit]
    totals, classes, horizon, gaps = Counter(), Counter(), {}, []
    errors = 0
    for mid in tqdm(ids, desc="second-scale evidence", unit="game"):
        try:
            match = json.loads((CONFIG.raw / "matches" / f"{mid}.json").read_text())
            timeline = json.loads((CONFIG.raw / "timelines" / f"{mid}.json").read_text())
            one = summarize_match(match, timeline, manifest["account"]["puuid"])
            gaps.extend(one.pop("faker_position_gaps_ms"))
            classes.update(one.pop("event_categories"))
            for seconds, counts in one.pop("horizons").items():
                horizon.setdefault(seconds, Counter()).update(counts)
            totals.update(one)
        except Exception:
            errors += 1
    if not totals["faker_position_anchors"]:
        raise ValueError("No Faker position anchors found")
    report = {"schema_version": 1, "source": "cached KR queue-420 Riot match-v5 timelines",
              "source_matches": len(ids) - errors, "parse_errors": errors,
              "totals": dict(totals), "event_categories": dict(sorted(classes.items())),
              "faker_position_gap_seconds": {
                  "median": round(statistics.median(gaps) / 1000, 2),
                  "p10": round(sorted(gaps)[int(.1 * (len(gaps)-1))] / 1000, 2),
                  "p90": round(sorted(gaps)[int(.9 * (len(gaps)-1))] / 1000, 2)},
              "horizons_seconds": {key: dict(horizon[key]) for key in map(str, HORIZONS_S)},
              "semantics": {"event_time": "API timestamp; not a Faker click timestamp unless attributed",
                            "event_xy": "continuous event locus when provided; not player position",
                            "player_xy": "observed only at timestamped participant frames",
                            "between_frames": "unknown; no interpolation becomes ground truth",
                            "grid": "rendering resolution, not measurement resolution"}}
    atomic_json(output, report)
    return report
