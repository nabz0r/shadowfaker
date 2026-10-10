#!/usr/bin/env python3
"""Publish aggregate inventory counts; never publish raw matches or IDs."""
import json
from collections import Counter
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "docs" / "data" / "public_corpus_inventory.json"


def count_table(path: Path, table: str) -> int:
    with sqlite3.connect(path) as db:
        return db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def build() -> dict:
    original = json.loads((RAW / "manifest.json").read_text())
    alias = json.loads((RAW / "aliases" / "manifest.json").read_text())
    expanded = json.loads((RAW / "expanded_summary.json").read_text())
    meta = json.loads((ROOT / "data" / "processed" / "meta.json").read_text())
    finals = json.loads((ROOT / "docs" / "data" / "world_finals.json").read_text())
    warehouse = ROOT / "data" / "processed64" / "faker_states.sqlite"
    text_db = ROOT / "data" / "text" / "game_text.sqlite"
    with sqlite3.connect(warehouse) as db:
        states = db.execute("SELECT COUNT(*) FROM states").fetchone()[0]
        actors = db.execute("SELECT COUNT(*) FROM actors").fetchone()[0]
        transitions = db.execute("SELECT COUNT(*) FROM transitions").fetchone()[0]
        events = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        events_positioned = db.execute("SELECT COUNT(*) FROM events WHERE cell64 IS NOT NULL").fetchone()[0]
        by_category = dict(db.execute("SELECT category,COUNT(*) FROM events GROUP BY category"))
        event_breakdown = [{"category": category, "events": total, "positioned": positioned,
                            "actors": actors, "items": items, "skills": skills, "indexed": True}
                           for category,total,positioned,actors,items,skills in db.execute("""
                SELECT category,COUNT(*),SUM(cell64 IS NOT NULL),SUM(actor_id > 0),
                       SUM(item_id > 0),SUM(skill_slot > 0)
                FROM events GROUP BY category ORDER BY COUNT(*) DESC""")]
    item_lifecycle = Counter()
    for mid in meta["counts"]:
        timeline = json.loads((RAW / "timelines" / f"{mid}.json").read_text())
        item_lifecycle.update(e.get("type") for frame in (timeline.get("info") or {}).get("frames") or []
                              for e in frame.get("events") or []
                              if e.get("type") in {"ITEM_PURCHASED","ITEM_SOLD","ITEM_DESTROYED","ITEM_UNDO"})
    for category in ("ITEM_SOLD","ITEM_DESTROYED","ITEM_UNDO"):
        event_breakdown.append({"category":category,"events":item_lifecycle[category],
                                "positioned":0,"actors":None,"items":None,"skills":0,"indexed":False})
    with sqlite3.connect(text_db) as db:
        text_kinds = dict(db.execute("SELECT source_kind,COUNT(*) FROM documents GROUP BY source_kind"))
    result = {
        "schema_version": 2,
        "source_snapshot": original["latest_id_snapshot"],
        "raw_cache": {
            "match_json": len(list((RAW / "matches").glob("*.json"))),
            "timeline_json": len(list((RAW / "timelines").glob("*.json"))),
            "professional_csv": len(list((RAW / "pro").glob("*.csv"))),
        },
        "domains": {
            "kr_ranked_ids": len(original["games"]),
            "kr_ranked_usable": len(meta["counts"]),
            "kr_short_remakes": len(original["games"]) - len(meta["counts"]),
            "kr_other_modes_cached": expanded["other_mode_timeline_cached"],
            "euw_attributed_ranked": len(alias["games"]),
            "professional_mirror_summaries": count_table(ROOT / "data" / "processed" / "pro_catalog.sqlite", "games"),
            "curated_final_games": sum(len(f["games"]) for f in finals["finals"]),
            "curated_landmark_games": len(finals["extra_games"]),
        },
        "source_accounts": [{"riot_id":"#".join(original["account"]["resolved"]),
                             "region":"KR", "ranked_ids":len(original["games"]),
                             "usable_timelines":len(meta["counts"]),
                             "status":"Riot account-v1 PUUID resolved; personal identity not independently proven",
                             "source_url":None}] + [
            {"riot_id":riot_id,"region":"EUW" if account["route"]=="europe" else "NA",
             "ranked_ids":account["ranked_ids"],
             "usable_timelines":sum(game.get("status")=="ok" for game in alias["games"].values()
                                    if game.get("alias")==riot_id) if isinstance(alias["games"],dict) else None,
             "status":account["identity"], "claim":account["claim"],
             "source_url":account["source_url"] if account["ranked_ids"] else None}
            for riot_id, account in alias["accounts"].items()],
        "warehouse": {
            "ranked_matches": count_table(warehouse, "matches"),
            "frames": states, "actor_rows": actors,
            "transitions": transitions, "events": events,
            "events_with_coordinates": events_positioned,
            "events_without_coordinates": events - events_positioned,
            "event_categories": by_category,
            "event_breakdown": event_breakdown,
            "item_lifecycle_raw_counts": dict(item_lifecycle),
        },
        "search_index": text_kinds,
        "postgame_facts": count_table(ROOT / "data" / "processed" / "game_facts.sqlite", "games"),
        "limitations": [
            "A cached JSON is not an eligible ranked training game. The cache includes other modes, an attributed EUW account and short games.",
            "Event locations may refer to a victim, ward, monster or structure; they are not Faker positions.",
            "Professional summaries and final-game cards have no Riot trajectory and may overlap with other sources.",
            "Post-game KDA, damage and final items are retrospective catalog fields, never features at time t.",
            "The current ranked timeline samples player positions about once a minute; the ten-second target is an event type, not a position.",
        ],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    data = build()
    print(f"{data['raw_cache']['match_json']} cached matches; {data['warehouse']['frames']} frames; "
          f"{data['warehouse']['events_with_coordinates']}/{data['warehouse']['events']} placed events -> {OUT}")
