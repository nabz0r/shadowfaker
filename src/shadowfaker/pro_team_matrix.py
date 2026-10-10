"""Faker-centred professional co-play history and 10/15-minute score matrices.

Professional CSV rows are a separate, unverified mirror domain. Nothing here
is joined to ranked solo-queue frames or interpreted as player-view movement.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3

from .config import CONFIG
from .util import atomic_json

ROOT = CONFIG.root
CATALOG = ROOT / "data" / "processed" / "pro_catalog.sqlite"
DB = ROOT / "data" / "processed" / "pro_team_matrix.sqlite"
PUBLIC = ROOT / "docs" / "data" / "public_team_matrix.json"
ROLES = ("top", "jng", "mid", "bot", "sup")
FOCUS = ("Faker", "Doran", "Oner", "Keria")
SNAPSHOT = ("golddiffat10", "golddiffat15", "xpdiffat10", "xpdiffat15",
            "killsat10", "assistsat10", "deathsat10")
SCHEMA_VERSION = 4

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS games(
 game_id TEXT PRIMARY KEY, game_date TEXT NOT NULL, season TEXT, league TEXT,
 patch TEXT, source_sha256 TEXT NOT NULL, win INTEGER, complete_snapshot INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS players(
 game_id TEXT NOT NULL, role TEXT NOT NULL, player TEXT NOT NULL, champion TEXT,
 gold_diff10 REAL, gold_diff15 REAL, xp_diff10 REAL, xp_diff15 REAL,
 kills10 REAL, assists10 REAL, deaths10 REAL,
 final_kills REAL, final_deaths REAL, final_assists REAL,
 final_damage REAL, final_vision REAL,
 PRIMARY KEY(game_id,role), FOREIGN KEY(game_id) REFERENCES games(game_id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS player_name ON players(player,role);
CREATE TABLE IF NOT EXISTS pair_history(
 game_id TEXT NOT NULL, teammate TEXT NOT NULL, prior_games INTEGER NOT NULL,
 prior_effective90 REAL NOT NULL, days_since REAL,
 PRIMARY KEY(game_id,teammate), FOREIGN KEY(game_id) REFERENCES games(game_id) ON DELETE CASCADE);
"""


def numeric(row: dict, field: str) -> float | None:
    try:
        value = float(row[field])
        return value if math.isfinite(value) else None
    except (KeyError, TypeError, ValueError):
        return None


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def prior_exposure(previous: list[datetime], current: datetime, half_life_days: float = 90) -> tuple[int, float, float | None]:
    earlier = [date for date in previous if date < current]
    days = lambda date: (current - date).total_seconds() / 86400
    return (len(earlier), sum(2 ** (-days(date) / half_life_days) for date in earlier),
            days(earlier[-1]) if earlier else None)


def build(*, paths: tuple[Path, ...] | None = None, db_path: Path = DB,
          pilot: int | None = None) -> dict:
    if paths is None:
        paths = tuple(sorted((ROOT / "data" / "raw" / "pro").glob("oracle_mirror_20*.csv")))
    if not paths or not CATALOG.is_file():
        raise FileNotFoundError("Build the local professional catalog and cached annual CSVs first")
    with sqlite3.connect(CATALOG) as catalog:
        selected = catalog.execute("SELECT game_id,game_date FROM games ORDER BY game_date,game_id").fetchall()
    if pilot is not None:
        selected = selected[:pilot]
    wanted = {game_id for game_id, _ in selected}
    source_shas = {path.name: fingerprint(path) for path in paths}
    selected_sha = hashlib.sha256(json.dumps(selected, sort_keys=True).encode()).hexdigest()
    source_stamp = json.dumps({"schema": SCHEMA_VERSION, "sources": source_shas,
                               "selected_sha256": selected_sha, "pilot": pilot}, sort_keys=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.executescript(SCHEMA)
        cached = db.execute("SELECT value FROM metadata WHERE key='source_stamp'").fetchone()
        if cached and cached[0] == source_stamp and db.execute("SELECT COUNT(*) FROM games").fetchone()[0]:
            return counts(db, cached=True)
        found: dict[str, list[tuple[str, dict]]] = defaultdict(list)
        for path in paths:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                for row in csv.DictReader(stream):
                    if (row.get("gameid") in wanted and row.get("teamname") in ("T1", "SK Telecom T1", "SKT")
                            and row.get("position") in ROLES):
                        found[row["gameid"]].append((path.name, row))
        clean = []
        skipped = Counter()
        for game_id, _ in selected:
            rows = found.get(game_id, [])
            by_role = {row.get("position"): row for _, row in rows}
            if len(rows) != 5 or set(by_role) != set(ROLES) or by_role["mid"].get("playername") != "Faker":
                skipped["not_exact_five_with_faker_mid"] += 1
                continue
            if any(row.get("date") != by_role["mid"].get("date") for row in by_role.values()):
                skipped["inconsistent_roster_date"] += 1
                continue
            faker = by_role["mid"]
            try:
                date = datetime.fromisoformat(faker["date"])
            except (KeyError, ValueError):
                skipped["invalid_date"] += 1
                continue
            if date.tzinfo is not None:
                date = date.astimezone(timezone.utc).replace(tzinfo=None)
            source_name = rows[0][0]
            if any(name != source_name for name, _ in rows):
                skipped["mixed_source"] += 1
                continue
            complete = all(numeric(row, field) is not None for row in by_role.values() for field in SNAPSHOT)
            clean.append((game_id, date, source_name, faker, by_role, complete))
        clean.sort(key=lambda part: (part[1], part[0]))
        history: dict[str, list[datetime]] = defaultdict(list)
        games = []
        players = []
        pairs = []
        for game_id, date, source_name, faker, by_role, complete in clean:
            games.append((game_id, date.isoformat(sep=" "), faker.get("year"), faker.get("league"),
                          faker.get("patch"), source_shas[source_name],
                          int(numeric(faker, "result")) if numeric(faker, "result") is not None else None,
                          int(complete)))
            for role in ROLES:
                row = by_role[role]
                players.append((game_id, role, row.get("playername") or "UNKNOWN", row.get("champion"),
                                *(numeric(row, field) for field in SNAPSHOT),
                                *(numeric(row, field) for field in ("kills", "deaths", "assists",
                                                                  "damagetochampions", "visionscore"))))
                if role == "mid":
                    continue
                teammate = row.get("playername") or "UNKNOWN"
                n, effective, days_since = prior_exposure(history[teammate], date)
                pairs.append((game_id, teammate, n, effective, days_since))
                history[teammate].append(date)
        with db:
            db.execute("DELETE FROM pair_history")
            db.execute("DELETE FROM players")
            db.execute("DELETE FROM games")
            db.executemany("INSERT INTO games VALUES (?,?,?,?,?,?,?,?)", games)
            db.executemany("INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", players)
            db.executemany("INSERT INTO pair_history VALUES (?,?,?,?,?)", pairs)
            db.execute("INSERT OR REPLACE INTO metadata VALUES ('source_stamp',?)", (source_stamp,))
            db.execute("INSERT OR REPLACE INTO metadata VALUES ('schema_version',?)", (str(SCHEMA_VERSION),))
        outcome = counts(db, cached=False)
        outcome["skipped"] = dict(skipped)
        return outcome


def counts(db: sqlite3.Connection, *, cached: bool) -> dict:
    return {"cached": cached,
            "games": db.execute("SELECT COUNT(*) FROM games").fetchone()[0],
            "player_rows": db.execute("SELECT COUNT(*) FROM players").fetchone()[0],
            "complete_10_15": db.execute("SELECT SUM(complete_snapshot) FROM games").fetchone()[0] or 0,
            "pair_rows": db.execute("SELECT COUNT(*) FROM pair_history").fetchone()[0]}


def summarize(db_path: Path = DB, output: Path = PUBLIC) -> dict:
    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        games = [dict(row) for row in db.execute("SELECT * FROM games ORDER BY game_date,game_id")]
        players = defaultdict(dict)
        for row in db.execute("SELECT * FROM players"):
            players[row["game_id"]][row["role"]] = dict(row)
        years = sorted({game["game_date"][:4] for game in games})
        def cohort(year: str | None) -> list[dict]:
            return [game for game in games if year is None or game["game_date"].startswith(year)]
        def pair_matrix(subset: list[dict]) -> list[list[int]]:
            names = [set(row["player"] for row in players[game["game_id"]].values()) for game in subset]
            return [[sum(a in group and b in group for group in names) for b in FOCUS] for a in FOCUS]
        def role_stats(subset: list[dict]) -> dict:
            out = {}
            for role in ROLES:
                rows = [players[game["game_id"]][role] for game in subset if game["complete_snapshot"]]
                def mean(field: str) -> float | None:
                    return round(sum(row[field] for row in rows) / len(rows), 2) if rows else None
                gold10, gold15, xp10, xp15 = map(mean, ("gold_diff10", "gold_diff15", "xp_diff10", "xp_diff15"))
                out[role] = {"n": len(rows), "gold_diff10": gold10, "gold_diff15": gold15,
                             "gold_swing10_15": round(gold15 - gold10, 2) if rows else None,
                             "xp_diff10": xp10, "xp_diff15": xp15,
                             "xp_swing10_15": round(xp15 - xp10, 2) if rows else None}
            return out
        def swing_matrix(subset: list[dict]) -> list[list[float | None]]:
            vectors = [[players[game["game_id"]][role]["gold_diff15"] -
                        players[game["game_id"]][role]["gold_diff10"] for role in ROLES]
                       for game in subset if game["complete_snapshot"]]
            if len(vectors) < 2:
                return [[None for _ in ROLES] for _ in ROLES]
            means = [sum(vector[i] for vector in vectors) / len(vectors) for i in range(len(ROLES))]
            centered = [[vector[i] - means[i] for i in range(len(ROLES))] for vector in vectors]
            squares = [sum(vector[i] ** 2 for vector in centered) for i in range(len(ROLES))]
            return [[round(sum(vector[i] * vector[j] for vector in centered) /
                           math.sqrt(squares[i] * squares[j]), 3)
                     if squares[i] and squares[j] else None for j in range(len(ROLES))]
                    for i in range(len(ROLES))]
        by_year = {}
        for year in years:
            subset = cohort(year)
            by_year[year] = {"games": len(subset),
                             "complete_10_15": sum(game["complete_snapshot"] for game in subset),
                             "pair_matrix": pair_matrix(subset), "roles": role_stats(subset),
                             "gold_swing_correlations": swing_matrix(subset)}
        # Monthly endpoints expose historical exposure, never row-level game IDs.
        monthly = defaultdict(dict)
        for game in games:
            month = game["game_date"][:7]
            for teammate, n, effective in db.execute(
                "SELECT teammate,prior_games,prior_effective90 FROM pair_history WHERE game_id=?", (game["game_id"],)):
                if teammate in FOCUS:
                    monthly[month][teammate] = {"prior_games": n, "effective90": round(effective, 2)}
        result = {"schema_version": SCHEMA_VERSION, "domain": "professional_match_summary_only",
                  "provenance": "unverified_public_mirror_of_Oracle_Elixir",
                  "source": "https://github.com/twodotone/finalLOL/tree/main/data/csv",
                  "official_roster_reference": "https://lolesports.com/en-US/teams/t1",
                  "games": len(games), "player_rows": sum(len(group) for group in players.values()),
                  "unknown_player_rows": sum(row["player"] == "UNKNOWN" for group in players.values() for row in group.values()),
                  "complete_10_15": sum(game["complete_snapshot"] for game in games),
                  "first_date": games[0]["game_date"][:10], "last_date": games[-1]["game_date"][:10],
                  "focus": list(FOCUS), "roles": list(ROLES), "years": years,
                  "by_year": by_year, "all": {"games": len(games),
                                           "complete_10_15": sum(game["complete_snapshot"] for game in games),
                                           "pair_matrix": pair_matrix(games), "roles": role_stats(games),
                                           "gold_swing_correlations": swing_matrix(games)},
                  "monthly_prior": [{"month": month, **monthly[month]} for month in sorted(monthly)],
                  "limits": "Shared games measure exposure, not communication, friendship, tactical influence or causal synergy. 10/15-minute scoreboard snapshots have no positions or POV; 2026 source ends before the current season. No professional row trains the ranked spatial model."}
    atomic_json(output, result)
    return result
