"""Local, provenance-aware catalog of Faker professional game summaries.

CSV match summaries have no player trajectories; never merge them into the
solo queue spatial dataset or treat end-of-game fields as live features.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

from .config import CONFIG
from .util import atomic_json

DB = CONFIG.root / "data" / "processed" / "pro_catalog.sqlite"
SOURCE = "https://github.com/twodotone/finalLOL/tree/main/data/csv"
UPSTREAM = "https://oracleselixir.com/match-data/"


def import_csv(paths: list[Path], db: Path = DB, limit: int | None = None) -> dict:
    db.parent.mkdir(parents=True, exist_ok=True)
    cx = sqlite3.connect(db)
    cx.executescript("""
    CREATE TABLE IF NOT EXISTS sources (
      sha256 TEXT PRIMARY KEY, filename TEXT, mirror_url TEXT, upstream_url TEXT,
      provenance_status TEXT, year TEXT, bytes INTEGER);
    CREATE TABLE IF NOT EXISTS games (
      source_sha256 TEXT NOT NULL, game_id TEXT NOT NULL, game_date TEXT,
      league TEXT, team TEXT, role TEXT, champion TEXT, win INTEGER,
      kills INTEGER, deaths INTEGER, assists INTEGER, completeness TEXT,
      PRIMARY KEY (source_sha256,game_id));
    CREATE INDEX IF NOT EXISTS games_date ON games(game_date);
    """)
    accepted = Counter()
    seen = Counter()
    rejected = Counter()
    source_info = []
    for path in paths:
        fingerprint = hashlib.sha256()
        with path.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                fingerprint.update(block)
        digest = fingerprint.hexdigest()
        year = path.stem.split("_")[-1]
        # The local mirror can be incomplete or stale. It is a documented
        # candidate source, not a provider-verified original or a Faker POV.
        source_info.append({"year_hint": year, "sha256": digest, "bytes": path.stat().st_size})
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            required = {"gameid", "playername", "teamname", "position", "date"}
            if not required.issubset(reader.fieldnames or ()):
                raise ValueError(f"Missing Oracle-style columns: {path}")
            # A refreshed annual snapshot replaces its older local version.
            # Keep one source per year so reruns cannot inflate the catalog.
            old_sources = [row[0] for row in cx.execute(
                "SELECT sha256 FROM sources WHERE year = ? AND sha256 != ?", (year, digest))]
            for old_digest in old_sources:
                cx.execute("DELETE FROM games WHERE source_sha256 = ?", (old_digest,))
                cx.execute("DELETE FROM sources WHERE sha256 = ?", (old_digest,))
            cx.execute("INSERT OR REPLACE INTO sources VALUES (?,?,?,?,?,?,?)",
                       (digest, path.name, SOURCE, UPSTREAM, "unverified_public_mirror", year, path.stat().st_size))
            for row in reader:
                if (row.get("playername") or "").strip().casefold() != "faker":
                    continue
                seen[year] += 1
                game_id = (row.get("gameid") or "").strip()
                team = (row.get("teamname") or "").strip()
                role = (row.get("position") or "").strip().lower()
                if not game_id or team not in ("T1", "SK Telecom T1", "SKT") or role != "mid":
                    rejected[year] += 1
                    continue
                def integer(key: str) -> int | None:
                    try:
                        return int(float(row[key])) if row.get(key) else None
                    except (TypeError, ValueError):
                        return None
                win = integer("result")
                cx.execute("INSERT OR REPLACE INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                           (digest, game_id, row.get("date"), row.get("league"), team, role,
                            row.get("champion"), win, integer("kills"), integer("deaths"),
                            integer("assists"), row.get("datacompleteness")))
                accepted[year] += 1
                if limit is not None and sum(accepted.values()) >= limit:
                    break
        cx.commit()
        if limit is not None and sum(accepted.values()) >= limit:
            break
    unique_games = cx.execute("SELECT COUNT(DISTINCT game_id) FROM games").fetchone()[0]
    result = {"schema_version": 1, "pro_domain": "match_summary_only",
              "provenance": "unverified_public_mirror_of_Oracle_Elixir",
              "source_page": SOURCE, "upstream_page": UPSTREAM,
              "source_files": source_info, "faker_rows_seen": dict(seen),
              "accepted_by_year_hint": dict(accepted), "rejected": dict(rejected),
              "unique_games": unique_games,
              "limitations": "Mirror may be stale; attribution is playername/team/role in a third-party table. No temporal positions, POV, or verified game-to-Riot-ID crosswalk."}
    atomic_json(db.with_suffix(".meta.json"), result)
    cx.close()
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="+", type=Path)
    p.add_argument("--db", type=Path, default=DB)
    p.add_argument("--limit", type=int)
    a = p.parse_args()
    print(json.dumps(import_csv(a.paths, a.db, a.limit), indent=2))


if __name__ == "__main__":
    main()
