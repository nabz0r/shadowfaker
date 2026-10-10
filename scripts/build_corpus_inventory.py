#!/usr/bin/env python3
"""Publish aggregate inventory counts; never publish raw matches or IDs."""
import json
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
    with sqlite3.connect(text_db) as db:
        text_kinds = dict(db.execute("SELECT source_kind,COUNT(*) FROM documents GROUP BY source_kind"))
    result = {
        "schema_version": 1,
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
        "warehouse": {
            "ranked_matches": count_table(warehouse, "matches"),
            "frames": states, "actor_rows": actors,
            "transitions": transitions, "events": events,
            "events_with_coordinates": events_positioned,
            "events_without_coordinates": events - events_positioned,
            "event_categories": by_category,
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
