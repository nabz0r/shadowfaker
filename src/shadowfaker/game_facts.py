"""Private, resumable post-game facts index for the ranked replay browser.

Everything here is known only after a match ends. Never join these columns into
the causal state at time t or use them as behavioral-cloning model features.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

from tqdm import tqdm

from .config import CONFIG

DB = CONFIG.root / "data" / "processed" / "game_facts.sqlite"


def connect(path: Path = DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS games (
        match_id TEXT PRIMARY KEY, source_sha256 TEXT NOT NULL,
        started_utc TEXT, duration_seconds INTEGER, patch TEXT,
        champion TEXT, side TEXT, won INTEGER, kills INTEGER, deaths INTEGER,
        assists INTEGER, cs INTEGER, damage_champions INTEGER, vision_score INTEGER,
        items_json TEXT NOT NULL, allies_json TEXT NOT NULL, enemies_json TEXT NOT NULL
    )""")
    return db


def parse_match(payload: dict, puuid: str) -> dict:
    info = payload.get("info") or {}
    participants = info.get("participants") or []
    own = next((p for p in participants if p.get("puuid") == puuid), None)
    if own is None:
        raise ValueError("Target account absent from match participants")
    team = own.get("teamId")
    timestamp = info.get("gameStartTimestamp") or info.get("gameCreation")
    started = datetime.fromtimestamp(timestamp / 1000, timezone.utc).isoformat(timespec="minutes") if timestamp else None
    duration = info.get("gameDuration")
    if isinstance(duration, (int, float)) and duration > 86400:
        duration /= 1000  # Older match-v5 patches used milliseconds.
    def champions(same: bool) -> list[str]:
        return [str(p.get("championName") or p.get("championId") or "?")
                for p in participants if (p.get("teamId") == team) == same]
    return {
        "match_id": payload.get("metadata", {}).get("matchId"),
        "started_utc": started,
        "duration_seconds": int(duration) if duration is not None else None,
        "patch": ".".join(str(info.get("gameVersion") or "").split(".")[:2]),
        "champion": str(own.get("championName") or own.get("championId") or "?"),
        "side": "BLUE" if team == 100 else "RED" if team == 200 else "UNKNOWN",
        "won": int(bool(own["win"])) if "win" in own else None,
        "kills": own.get("kills"), "deaths": own.get("deaths"), "assists": own.get("assists"),
        "cs": sum(int(own.get(k) or 0) for k in ("totalMinionsKilled", "neutralMinionsKilled")),
        "damage_champions": own.get("totalDamageDealtToChampions"),
        "vision_score": own.get("visionScore"),
        "items": [int(own.get(f"item{i}") or 0) for i in range(7) if int(own.get(f"item{i}") or 0) > 0],
        "allies": champions(True), "enemies": champions(False),
    }


def build(ids: list[str], puuid: str, raw_dir: Path, index: Path = DB) -> dict:
    db = connect(index)
    inserted = skipped = 0
    errors = {}
    try:
        for mid in tqdm(ids, desc="post-game facts", unit="game"):
            try:
                data = (raw_dir / f"{mid}.json").read_bytes()
                digest = hashlib.sha256(data).hexdigest()
                old = db.execute("SELECT source_sha256 FROM games WHERE match_id=?", (mid,)).fetchone()
                if old and old[0] == digest:
                    skipped += 1
                    continue
                fact = parse_match(json.loads(data), puuid)
                if fact["match_id"] != mid:
                    raise ValueError("Match ID differs from cache filename")
                with db:
                    db.execute("""INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(match_id) DO UPDATE SET
                        source_sha256=excluded.source_sha256,started_utc=excluded.started_utc,
                        duration_seconds=excluded.duration_seconds,patch=excluded.patch,
                        champion=excluded.champion,side=excluded.side,won=excluded.won,
                        kills=excluded.kills,deaths=excluded.deaths,assists=excluded.assists,
                        cs=excluded.cs,damage_champions=excluded.damage_champions,
                        vision_score=excluded.vision_score,items_json=excluded.items_json,
                        allies_json=excluded.allies_json,enemies_json=excluded.enemies_json""",
                        (mid, digest, fact["started_utc"], fact["duration_seconds"],
                         fact["patch"], fact["champion"], fact["side"], fact["won"],
                         fact["kills"], fact["deaths"], fact["assists"], fact["cs"],
                         fact["damage_champions"], fact["vision_score"],
                         json.dumps(fact["items"]), json.dumps(fact["allies"]), json.dumps(fact["enemies"])))
                inserted += 1
            except Exception as exc:
                errors[mid] = str(exc)
    finally:
        total = db.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        db.close()
    return {"requested": len(ids), "indexed": inserted, "reused": skipped,
            "total": total, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true", help="Index only five games")
    args = parser.parse_args()
    meta = json.loads((CONFIG.processed / "meta.json").read_text())
    ids = sorted(meta["counts"])
    puuid = json.loads((CONFIG.raw / "resolved_account.json").read_text())["puuid"]
    print(build(ids[:5] if args.pilot else ids, puuid, CONFIG.raw / "matches"))


if __name__ == "__main__":
    main()
