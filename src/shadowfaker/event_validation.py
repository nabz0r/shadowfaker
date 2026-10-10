"""Independently reconcile public event aggregates with cached Riot timelines.

Only counts leave the local machine. A matching row proves transcription of an
API event, not that Faker saw it or that an analyst knows why it happened.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import sqlite3

from tqdm import tqdm

from .config import CONFIG
from .events64 import event_category
from .state_matrix import DB
from .util import atomic_json, read_json

OUT = CONFIG.root / "docs" / "data" / "public_event_validation.json"
MONSTERS = {"DRAGON": "dragon", "BARON_NASHOR": "baron",
            "RIFTHERALD": "herald", "HORDE": "grubs"}
SPATIAL_MEANING = {
    "faker_kill": "victim/event locus, not Faker's position",
    "faker_death": "victim/event locus; Faker is the victim",
    "ally_kill": "victim/event locus, not ally position",
    "enemy_kill": "victim/event locus, not enemy position",
    "dragon": "monster/event locus", "baron": "monster/event locus",
    "herald": "monster/event locus", "grubs": "monster/event locus",
    "building": "destroyed building/event locus",
    "ward_placed": "no coordinates supplied by this cohort",
    "ward_cleared": "no coordinates supplied by this cohort",
    "ITEM_PURCHASED": "no coordinates; time and item only",
    "SKILL_LEVEL_UP": "no coordinates; time and skill only",
}


def independent_category(event: dict, own_pid: int, own_team: int,
                         teams: dict[int, int]) -> str | None:
    """Explicit audit rules, separate from the production event classifier."""
    kind = event.get("type")
    if kind == "CHAMPION_KILL":
        victim, killer = event.get("victimId"), event.get("killerId")
        if victim == own_pid:
            return "faker_death"
        if killer == own_pid:
            return "faker_kill"
        if teams.get(killer) == own_team:
            return "ally_kill"
        if teams.get(killer) in (100, 200):
            return "enemy_kill"
    elif kind == "ELITE_MONSTER_KILL":
        return MONSTERS.get(str(event.get("monsterType") or "").upper())
    elif kind == "BUILDING_KILL":
        return "building"
    elif kind == "WARD_PLACED":
        return "ward_placed"
    elif kind == "WARD_KILL":
        return "ward_cleared"
    elif kind in ("ITEM_PURCHASED", "SKILL_LEVEL_UP"):
        return kind
    return None


def strict_cell(event: dict) -> tuple[int | None, bool]:
    point = event.get("position")
    if not isinstance(point, dict) or point.get("x") is None or point.get("y") is None:
        return None, False
    try:
        x, y = float(point["x"]), float(point["y"])
    except (TypeError, ValueError):
        return None, True
    if not (0 <= x <= 15000 and 0 <= y <= 15000):
        return None, True
    return min(63, int(y / 15000 * 64)) * 64 + min(63, int(x / 15000 * 64)), False


def missing_required(event: dict, category: str) -> bool:
    if event.get("timestamp") is None:
        return True
    if category in ("faker_kill", "faker_death", "ally_kill", "enemy_kill"):
        return not (1 <= int(event.get("victimId") or 0) <= 10)
    if category in MONSTERS.values():
        return not event.get("monsterType")
    if category == "building":
        return event.get("teamId") not in (100, 200)
    if category in ("ITEM_PURCHASED", "SKILL_LEVEL_UP"):
        pid = int(event.get("participantId") or 0)
        field = "itemId" if category == "ITEM_PURCHASED" else "skillSlot"
        return not (1 <= pid <= 10 and int(event.get(field) or 0) > 0)
    return False


def audit_match(match: dict, timeline: dict, puuid: str, indexed: dict[tuple[int, int], tuple]) -> dict:
    players = (match.get("info") or {}).get("participants") or []
    own = next(p for p in players if p.get("puuid") == puuid)
    own_pid, own_team = int(own["participantId"]), int(own["teamId"])
    teams = {int(p.get("participantId") or 0): int(p.get("teamId") or 0) for p in players}
    raw_types, excluded, metrics, issues = Counter(), Counter(), defaultdict(Counter), Counter()
    raw_keys = set()
    neutral = Counter()
    for frame_i, frame in enumerate((timeline.get("info") or {}).get("frames") or []):
        for event_i, event in enumerate(frame.get("events") or []):
            raw_keys.add((frame_i, event_i))
            kind = str(event.get("type") or "UNKNOWN")
            raw_types[kind] += 1
            if kind == "CHAMPION_KILL" and not event.get("killerId"):
                neutral["faker_victim" if event.get("victimId") == own_pid else "other_victim"] += 1
            category = independent_category(event, own_pid, own_team, teams)
            production = event_category(event, own_pid, own_team, teams)
            production_category = (production or kind) if kind in ("ITEM_PURCHASED", "SKILL_LEVEL_UP") else production
            if category != production_category:
                issues["classifier_disagreement"] += 1
            if category is None:
                excluded[kind] += 1
                if (frame_i, event_i) in indexed:
                    issues["unexpected_index_row"] += 1
                continue
            metric = metrics[category]
            metric["raw"] += 1
            key = (frame_i, event_i)
            row = indexed.get(key)
            if row is None:
                issues["missing_index_row"] += 1
                continue
            metric["indexed"] += 1
            cell, bad_cell = strict_cell(event)
            if event.get("position") is not None:
                metric["source_positioned"] += 1
            if bad_cell:
                metric["invalid_coordinate"] += 1
            if cell is not None:
                metric["located"] += 1
            if missing_required(event, category):
                metric["missing_required"] += 1
            actor = int(event.get("participantId") or event.get("killerId") or event.get("creatorId") or 0)
            if actor == 0:
                metric["unknown_actor"] += 1
            timestamp = event.get("timestamp")
            expected = (int(timestamp if timestamp is not None else frame.get("timestamp") or 0), category,
                        cell, actor, int(event.get("victimId") or 0),
                        int(event.get("itemId") or 0), int(event.get("skillSlot") or 0))
            if row == expected:
                metric["exact"] += 1
            else:
                metric["mismatch"] += 1
                issues["row_mismatch"] += 1
    orphan_count = len(indexed.keys() - raw_keys)
    if orphan_count:
        issues["orphan_index_row"] += orphan_count
    return {"raw_types": raw_types, "excluded": excluded, "categories": metrics,
            "issues": issues, "neutral": neutral}


def audit(limit: int | None = None, db_path: Path = DB, output: Path | None = OUT) -> dict:
    manifest, meta = read_json(CONFIG.raw / "manifest.json"), read_json(CONFIG.processed / "meta.json")
    ids = [mid for mid in manifest["order"] if mid in meta["counts"]]
    if limit is not None:
        ids = ids[:limit]
    totals, excluded, neutral, issues = Counter(), Counter(), Counter(), Counter()
    categories: dict[str, Counter] = defaultdict(Counter)
    failures = 0
    with sqlite3.connect(db_path) as db:
        for mid in tqdm(ids, desc="event validation", unit="game"):
            try:
                match = json.loads((CONFIG.raw / "matches" / f"{mid}.json").read_text())
                timeline = json.loads((CONFIG.raw / "timelines" / f"{mid}.json").read_text())
                rows = {(fi, ei): (ts, category, cell, actor, victim, item, skill)
                        for fi, ei, ts, category, cell, actor, victim, item, skill in db.execute(
                            "SELECT frame_index,event_index,timestamp_ms,category,cell64,actor_id,victim_id,item_id,skill_slot "
                            "FROM events WHERE match_id=?", (mid,))}
                one = audit_match(match, timeline, manifest["account"]["puuid"], rows)
                totals.update(one["raw_types"])
                excluded.update(one["excluded"])
                neutral.update(one["neutral"])
                issues.update(one["issues"])
                for name, counts in one["categories"].items():
                    categories[name].update(counts)
            except Exception:
                failures += 1
    details = {}
    for name, counts in sorted(categories.items()):
        details[name] = {**{key: int(counts[key]) for key in
                             ("raw", "indexed", "exact", "mismatch", "located",
                              "source_positioned", "invalid_coordinate", "unknown_actor", "missing_required")},
                         "spatial_meaning": SPATIAL_MEANING[name],
                         "status": "verified_transcription" if counts["raw"] == counts["exact"]
                         and not counts["invalid_coordinate"] else "needs_review",
                         "source_quality": "partial_actor_or_field" if counts["missing_required"]
                         else "recorded_fields_present"}
    report = {"schema_version": 1, "scope": "KR queue 420 usable matches; raw Riot match-v5 timelines vs local index",
              "audited_matches": len(ids) - failures, "failed_matches": failures,
              "raw_events": sum(totals.values()), "indexed_events": sum(v["indexed"] for v in details.values()),
              "exact_index_rows": sum(v["exact"] for v in details.values()),
              "raw_types": dict(sorted(totals.items())), "excluded_types": dict(sorted(excluded.items())),
              "neutral_champion_deaths": dict(neutral), "issues": dict(issues),
              "categories": details,
              "interpretation": "Exact transcription validates API fields only. Event coordinates are loci, not Faker's POV. Item holdings remain a separate noisy proxy."}
    if output is not None:
        atomic_json(output, report)
    return report
