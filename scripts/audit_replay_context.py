#!/usr/bin/env python3
"""Publish aggregate coverage of replay context, never raw match records."""
import argparse
from collections import Counter
import json
from pathlib import Path

from tqdm import tqdm

from shadowfaker.config import CONFIG
from shadowfaker.demo import _cached_patch_items
from shadowfaker.events64 import event_category
from shadowfaker.util import atomic_json, read_json


def audit(limit: int | None = None) -> dict:
    manifest = read_json(CONFIG.raw / "manifest.json")
    ids = manifest["order"][:limit]
    categories, details, item_coverage, patches = Counter(), Counter(), Counter(), Counter()
    errors = 0
    for mid in tqdm(ids, desc="replay context", unit="game"):
        try:
            match = json.loads((CONFIG.raw / "matches" / f"{mid}.json").read_text())
            timeline = json.loads((CONFIG.raw / "timelines" / f"{mid}.json").read_text())
            players = (match.get("info") or {}).get("participants") or []
            own = next(p for p in players if p.get("puuid") == manifest["account"]["puuid"])
            pid, team = int(own["participantId"]), int(own["teamId"])
            teams = {int(p["participantId"]): int(p["teamId"]) for p in players}
            release, catalog, _ = _cached_patch_items(match, CONFIG.raw)
            patches[release or "missing"] += 1
            for frame in (timeline.get("info") or {}).get("frames") or []:
                for event in frame.get("events") or []:
                    category = event_category(event, pid, team, teams)
                    kind = event.get("type")
                    if category is None and kind not in ("ITEM_PURCHASED", "SKILL_LEVEL_UP"):
                        continue
                    if kind in ("ITEM_PURCHASED", "SKILL_LEVEL_UP") and int(event.get("participantId") or 0) not in teams:
                        continue
                    categories[category or kind] += 1
                    if (event.get("position") or {}).get("x") is not None and (event.get("position") or {}).get("y") is not None:
                        details["with_event_position"] += 1
                    if kind == "CHAMPION_KILL":
                        if int(event.get("victimId") or 0) in teams: details["kill_with_victim"] += 1
                        if event.get("assistingParticipantIds"): details["kill_with_assists"] += 1
                    elif kind == "ELITE_MONSTER_KILL":
                        if event.get("monsterSubType"): details["monster_with_subtype"] += 1
                        if int(event.get("killerTeamId") or 0) in (100, 200): details["monster_with_killer_team"] += 1
                    elif kind == "BUILDING_KILL":
                        if event.get("laneType"): details["building_with_lane"] += 1
                        if event.get("towerType") or event.get("buildingType"): details["building_with_type"] += 1
                        if int(event.get("teamId") or 0) in (100, 200): details["building_with_destroyed_team"] += 1
                    elif kind in ("WARD_PLACED", "WARD_KILL"):
                        if event.get("wardType") and event["wardType"] != "UNDEFINED": details["ward_with_specific_type"] += 1
                        else: details["ward_type_unspecified"] += 1
                    elif kind == "ITEM_PURCHASED":
                        item_coverage["purchase_events"] += 1
                        if str(event.get("itemId") or "") in catalog: item_coverage["catalog_matched"] += 1
        except Exception:
            errors += 1
    return {"schema_version":1,"domain":"same-PUUID ranked 420 timelines; aggregate only",
            "games_read":len(ids)-errors,"errors":errors,"categories":dict(sorted(categories.items())),
            "details":dict(sorted(details.items())),"item_coverage":dict(item_coverage),
            "catalog_release_counts":dict(sorted(patches.items())),
            "note":"Timed events are not second-by-second player positions. A source field may be present without being visible to Faker."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path, default=CONFIG.root / "docs/data/public_replay_context.json")
    args = parser.parse_args()
    result = audit(args.limit)
    atomic_json(args.output, result)
    print(json.dumps({"games_read":result["games_read"],"errors":result["errors"],
                      "displayable_events":sum(result["categories"].values()),
                      "catalog_release_count":len(result["catalog_release_counts"])}))
