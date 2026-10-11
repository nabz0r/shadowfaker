"""Private, source-linked IoC ledger for future grounded model experiments.

The ten-second clock labels events, while actor positions remain sampled at
Riot timeline frames. `context` queries never read rows after the cutoff t.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

import numpy as np
from tqdm import tqdm

from .action_sanitation import DATA as ACTIONS, FEATURE_NAMES, SCHEMA_VERSION as ACTION_SCHEMA, _digest
from .config import CONFIG
from .faker_actions import CLASSES, HORIZON_MS
from .features import cs, number, position
from .ioc import ITEM_TYPES, apply_item_event, inventory_snapshots
from .util import atomic_json, read_json

SCHEMA_VERSION = 2
DB = CONFIG.processed / "faker_ioc.sqlite"
EXPORT = CONFIG.processed / "faker_ioc_train.jsonl"
PUBLIC = CONFIG.root / "docs" / "data" / "public_ioc_ledger.json"
# Riot's teamPosition is supplied by completed-match metadata. Its ten
# role-specific distance channels are retained for historical model audits,
# but a prospective text export must not learn from a retrospective role tag.
RETROSPECTIVE_FEATURES = tuple(name for name in FEATURE_NAMES
                               if name.startswith(("ally_", "enemy_")) and name.endswith("_distance"))
EXPORT_FEATURES = tuple(name for name in FEATURE_NAMES if name not in RETROSPECTIVE_FEATURES)

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS games (
 match_id TEXT PRIMARY KEY, split TEXT NOT NULL, source_sha256 TEXT NOT NULL,
 actions_sha256 TEXT NOT NULL, patch TEXT, faker_pid INTEGER NOT NULL,
 faker_team_id INTEGER NOT NULL, faker_champion_id INTEGER NOT NULL,
 snapshot_count INTEGER NOT NULL, event_count INTEGER NOT NULL, window_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS snapshots (
 match_id TEXT NOT NULL, frame_index INTEGER NOT NULL, timestamp_ms INTEGER NOT NULL,
 PRIMARY KEY(match_id,frame_index), FOREIGN KEY(match_id) REFERENCES games(match_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS actors (
 match_id TEXT NOT NULL, frame_index INTEGER NOT NULL, participant_id INTEGER NOT NULL,
 side TEXT NOT NULL, role TEXT, champion_id INTEGER, x REAL, y REAL,
 total_gold REAL, current_gold REAL, xp REAL, level REAL, cs REAL,
 jungle_cs REAL, health_fraction REAL, items_json TEXT NOT NULL,
 PRIMARY KEY(match_id,frame_index,participant_id),
 FOREIGN KEY(match_id,frame_index) REFERENCES snapshots(match_id,frame_index) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS events (
 match_id TEXT NOT NULL, frame_index INTEGER NOT NULL, event_index INTEGER NOT NULL,
 timestamp_ms INTEGER NOT NULL, event_type TEXT NOT NULL,
 faker_relation TEXT NOT NULL, actor_id INTEGER, victim_id INTEGER,
 assists_json TEXT NOT NULL, x REAL, y REAL, item_id INTEGER, skill_slot INTEGER,
 before_item_id INTEGER, after_item_id INTEGER,
 monster_type TEXT, building_type TEXT, team_id INTEGER,
 PRIMARY KEY(match_id,frame_index,event_index),
 FOREIGN KEY(match_id) REFERENCES games(match_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS windows (
 match_id TEXT NOT NULL, window_index INTEGER NOT NULL, t_ms INTEGER NOT NULL,
 frame_index INTEGER NOT NULL, features BLOB NOT NULL,
 labels_json TEXT NOT NULL, first_delay_json TEXT NOT NULL,
 PRIMARY KEY(match_id,window_index),
 FOREIGN KEY(match_id,frame_index) REFERENCES snapshots(match_id,frame_index) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_events_time ON events(match_id,timestamp_ms);
CREATE INDEX IF NOT EXISTS idx_windows_time ON windows(match_id,t_ms);
CREATE INDEX IF NOT EXISTS idx_games_split ON games(split);
"""


def connect(path: Path = DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(SCHEMA)
    old = db.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
    if old and int(old[0]) != SCHEMA_VERSION:
        db.close()
        archive = path.with_name(f"{path.stem}.schema-{old[0]}{path.suffix}")
        if archive.exists():
            raise ValueError(f"IoC schema archive already exists: {archive}; choose a new database path")
        path.rename(archive)
        return connect(path)
    db.execute("INSERT OR REPLACE INTO metadata VALUES ('schema_version',?)", (str(SCHEMA_VERSION),))
    db.execute("INSERT OR REPLACE INTO metadata VALUES ('feature_names',?)", (json.dumps(FEATURE_NAMES),))
    db.execute("INSERT OR REPLACE INTO metadata VALUES ('label_names',?)", (json.dumps(CLASSES),))
    db.commit()
    return db


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _maybe_int(value):
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _xy(obj: dict) -> tuple[float | None, float | None]:
    p = position(obj)
    return (None, None) if p is None else (float(p[0]), float(p[1]))


def _event_row(mid: str, fi: int, ei: int, event: dict, faker_pid: int) -> tuple:
    kind = str(event.get("type") or "UNKNOWN")
    actor = _maybe_int(event.get("participantId"))
    if actor is None:
        actor = _maybe_int(event.get("killerId"))
    if actor is None:
        actor = _maybe_int(event.get("creatorId"))
    victim = _maybe_int(event.get("victimId"))
    assists = event.get("assistingParticipantIds") or []
    assists = [int(a) for a in assists if type(a) is int and 1 <= a <= 10]
    relation = ("actor" if actor == faker_pid else "victim" if victim == faker_pid
                else "assist" if faker_pid in assists else "none")
    x, y = _xy(event)
    return (mid, fi, ei, int(event["timestamp"]), kind, relation, actor, victim,
            json.dumps(assists), x, y, _maybe_int(event.get("itemId")),
            _maybe_int(event.get("skillSlot")), _maybe_int(event.get("beforeId")),
            _maybe_int(event.get("afterId")), event.get("monsterType"),
            event.get("buildingType"), _maybe_int(event.get("teamId")))


def _rows(mid: str, match: dict, timeline: dict, puuid: str, sample: dict, split: str,
          source_sha: str, action_sha: str) -> tuple[tuple, list, list, list, list]:
    players = match["info"]["participants"]
    own = next(p for p in players if p.get("puuid") == puuid)
    pid, team = int(own["participantId"]), int(own["teamId"])
    by_pid = {int(p["participantId"]): p for p in players}
    frames = timeline["info"]["frames"]
    inventories, _ = inventory_snapshots(timeline)
    snapshots, actors, events = [], [], []
    for fi, frame in enumerate(frames):
        ts = int(frame["timestamp"])
        snapshots.append((mid, fi, ts))
        pf = frame.get("participantFrames") or {}
        for actor_id in range(1, 11):
            player = by_pid[actor_id]
            state = pf.get(str(actor_id)) or pf.get(actor_id) or {}
            x, y = _xy(state)
            stats = state.get("championStats") or {}
            hpmax = number(stats.get("healthMax"), 0)
            hp = max(0, min(1, number(stats.get("health"), 0) / hpmax)) if hpmax > 0 else None
            side = "faker" if actor_id == pid else "ally" if int(player["teamId"]) == team else "enemy"
            actors.append((mid, fi, actor_id, side, player.get("teamPosition") or "UNKNOWN",
                           _maybe_int(player.get("championId")), x, y,
                           number(state.get("totalGold")) if state else None,
                           number(state.get("currentGold")) if state else None,
                           number(state.get("xp")) if state else None,
                           number(state.get("level")) if state else None,
                           cs(state) if state else None,
                           number(state.get("jungleMinionsKilled")) if state else None, hp,
                           json.dumps(sorted(item for item, count in inventories[fi][actor_id].items()
                                             for _ in range(count)))))
        for ei, event in enumerate(frame.get("events") or []):
            if type(event.get("timestamp")) is int:
                events.append(_event_row(mid, fi, ei, event, pid))
    x, times, fi, y, delays = (sample[k] for k in ("x", "t_ms", "frame_index", "y", "first_delay_ms"))
    if (x.shape != (len(times), len(FEATURE_NAMES)) or y.shape != (len(times), len(CLASSES))
            or delays.shape != y.shape or len(fi) != len(times)):
        raise ValueError("sanitized action arrays have incompatible shapes")
    if any(int(fi[i]) >= len(frames) or int(frames[int(fi[i])]["timestamp"]) > int(t)
           or int(t) + HORIZON_MS > int(frames[-1]["timestamp"])
           for i, t in enumerate(times)):
        raise ValueError("a window uses a future or missing snapshot")
    windows = [(mid, i, int(t), int(fi[i]), np.asarray(x[i], dtype="<f4").tobytes(),
                json.dumps([int(v) for v in y[i]]), json.dumps([int(v) for v in delays[i]]))
               for i, t in enumerate(times)]
    game = (mid, split, source_sha, action_sha, match["info"].get("gameVersion"),
            pid, team, int(own.get("championId") or 0), len(snapshots), len(events), len(windows))
    return game, snapshots, actors, events, windows


def build(*, pilot: bool = False, path: Path = DB) -> dict:
    manifest = read_json(CONFIG.raw / "manifest.json")
    meta = read_json(CONFIG.processed / "meta.json")
    if not manifest or not meta:
        raise FileNotFoundError("Ranked cache and split are required")
    splits = meta["splits"]
    ids = splits["train"][:3] + splits["val"][:2] if pilot else [
        mid for mid in manifest["order"] if mid in meta["counts"]]
    split_of = {mid: split for split, mids in splits.items() for mid in mids}
    db = connect(path)
    counts, errors = Counter(), {}
    for mid in tqdm(ids, desc="IoC evidence ledger", unit="game"):
        try:
            match_path = CONFIG.raw / "matches" / f"{mid}.json"
            timeline_path = CONFIG.raw / "timelines" / f"{mid}.json"
            action_path = ACTIONS / f"{mid}.npz"
            source_sha, action_sha = _digest(match_path, timeline_path), _sha(action_path)
            row = db.execute("SELECT source_sha256,actions_sha256,split FROM games WHERE match_id=?", (mid,)).fetchone()
            if row == (source_sha, action_sha, split_of[mid]):
                counts["cached"] += 1
                continue
            with np.load(action_path, allow_pickle=False) as z:
                if int(z["schema_version"]) != ACTION_SCHEMA or int(z["horizon_ms"]) != HORIZON_MS or str(z["source_sha256"]) != source_sha:
                    raise ValueError("sanitized action cache is stale; rebuild action sanitation first")
                sample = {k: z[k] for k in ("x", "t_ms", "frame_index", "y", "first_delay_ms")}
            match, timeline = read_json(match_path), read_json(timeline_path)
            if (match.get("metadata") or {}).get("matchId") != mid or (timeline.get("metadata") or {}).get("matchId") != mid:
                raise ValueError("match/timeline identity mismatch")
            game, snapshots, actors, events, windows = _rows(
                mid, match, timeline, manifest["account"]["puuid"], sample,
                split_of[mid], source_sha, action_sha)
            with db:
                db.execute("DELETE FROM games WHERE match_id=?", (mid,))
                db.execute("INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?)", game)
                db.executemany("INSERT INTO snapshots VALUES (?,?,?)", snapshots)
                db.executemany("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", actors)
                db.executemany("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", events)
                db.executemany("INSERT INTO windows VALUES (?,?,?,?,?,?,?)", windows)
            counts["rebuilt"] += 1
        except Exception as exc:
            errors[mid] = str(exc)
    tables = {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
              for table in ("games", "snapshots", "actors", "events", "windows")}
    split_counts = {split: n for split, n in db.execute(
        "SELECT g.split,COUNT(*) FROM windows w JOIN games g USING(match_id) GROUP BY g.split")}
    db.close()
    report = {"schema_version": SCHEMA_VERSION, "private_database": str(path),
              "tables": tables, "windows_by_split": split_counts,
              "cached_matches": counts["cached"], "rebuilt_matches": counts["rebuilt"],
              "errors": errors, "position_clock": "sampled timeline frames only",
              "event_clock": "event timestamps", "view": "omniscient Riot timeline, not Faker POV"}
    atomic_json(path.with_suffix(".summary.json"), report)
    return report


def context(db: sqlite3.Connection, match_id: str, window_index: int) -> tuple[dict, dict]:
    """Serialize one causal input plus a strictly separate future target."""
    db.row_factory = sqlite3.Row
    row = db.execute("""SELECT w.*,g.split,g.patch,g.faker_pid,g.faker_champion_id,
      s.timestamp_ms AS snapshot_ms FROM windows w JOIN games g USING(match_id)
      JOIN snapshots s ON s.match_id=w.match_id AND s.frame_index=w.frame_index
      WHERE w.match_id=? AND w.window_index=?""", (match_id, window_index)).fetchone()
    if row is None:
        raise KeyError((match_id, window_index))
    t = int(row["t_ms"])
    if int(row["snapshot_ms"]) > t:
        raise ValueError("future snapshot in context")
    actors = [dict(a) for a in db.execute("""SELECT participant_id,side,champion_id,x,y,
      total_gold,current_gold,xp,level,cs,jungle_cs,health_fraction,items_json FROM actors
      WHERE match_id=? AND frame_index=? ORDER BY participant_id""",
      (match_id, row["frame_index"]))]
    for a in actors:
        a["items_at_snapshot"] = json.loads(a.pop("items_json"))
        a["items_at_t"] = list(a["items_at_snapshot"])
    # The frame's inventory is already inclusive at snapshot_ms. Replay only
    # events in (snapshot_ms,t] so an item bought between frames is causal.
    inventories = {a["participant_id"]: Counter(a["items_at_snapshot"]) for a in actors}
    for event in db.execute("""SELECT timestamp_ms,event_type,actor_id,item_id,before_item_id,after_item_id
      FROM events WHERE match_id=? AND timestamp_ms>? AND timestamp_ms<=?
      AND event_type IN ('ITEM_PURCHASED','ITEM_SOLD','ITEM_DESTROYED','ITEM_UNDO')
      ORDER BY timestamp_ms,frame_index,event_index""", (match_id, row["snapshot_ms"], t)):
        if event[1] not in ITEM_TYPES or event[2] not in inventories:
            continue
        apply_item_event(inventories[event[2]], {"type": event[1], "itemId": event[3],
                                                 "beforeId": event[4], "afterId": event[5]})
    for a in actors:
        a["items_at_t"] = sorted(item for item, count in inventories[a["participant_id"]].items()
                                 for _ in range(count))
    events = [dict(e) for e in db.execute("""SELECT timestamp_ms,event_type,faker_relation,
      actor_id,victim_id,assists_json,x,y,item_id,skill_slot,before_item_id,after_item_id,monster_type,building_type,
      team_id,frame_index,event_index FROM events
      WHERE match_id=? AND timestamp_ms>? AND timestamp_ms<=?
      ORDER BY timestamp_ms,frame_index,event_index""", (match_id, t-60_000, t))]
    for e in events:
        e["assists"] = json.loads(e.pop("assists_json"))
    features = np.frombuffer(row["features"], dtype="<f4")
    if len(features) != len(FEATURE_NAMES) or any(e["timestamp_ms"] > t for e in events):
        raise ValueError("corrupt or future context")
    source = {"match_id": match_id, "window_index": window_index,
              "snapshot_frame_index": int(row["frame_index"]),
              "event_source": "Riot timeline; event frame_index/event_index"}
    inp = {"source": source, "split": row["split"], "t_ms": t,
           "horizon_ms": HORIZON_MS, "patch": row["patch"],
           "faker_participant_id": row["faker_pid"], "faker_champion_id": row["faker_champion_id"],
           "snapshot_ms": row["snapshot_ms"], "snapshot_age_ms": t-int(row["snapshot_ms"]),
           "view": "omniscient_timeline", "positions_are_sampled": True,
           "actors": actors, "past_60s_events": events,
           "causal_features": {name: float(value) for name, value in zip(FEATURE_NAMES, features)
                               if name in EXPORT_FEATURES},
           "withheld_retrospective_metadata": "Riot teamPosition and ten role-distance fields"}
    labels, delays = json.loads(row["labels_json"]), json.loads(row["first_delay_json"])
    target = {"interval": "(t,t+10000ms]", "observed_faker_events":
              {name: {"present": bool(labels[i]), "first_delay_ms": delays[i] if labels[i] else None}
               for i, name in enumerate(CLASSES)}}
    return inp, target


def export_train(path: Path = DB, output: Path = EXPORT, limit: int | None = None) -> dict:
    """Stream only train matches; never serialize validation or test labels."""
    if not path.is_file():
        raise FileNotFoundError(path)
    db = connect(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    n = 0
    try:
        with temp.open("w", encoding="utf-8") as file:
            cursor = db.execute("""SELECT w.match_id,w.window_index FROM windows w
              JOIN games g USING(match_id) WHERE g.split='train'
              ORDER BY w.match_id,w.window_index""")
            for mid, wi in cursor:
                inp, target = context(db, mid, wi)
                file.write(json.dumps({"input": inp, "target": target}, ensure_ascii=False,
                                      separators=(",", ":")) + "\n")
                n += 1
                if limit is not None and n >= limit:
                    break
        temp.replace(output)
    finally:
        temp.unlink(missing_ok=True)
        db.close()
    return {"private_export": str(output), "train_examples": n,
            "val_or_test_examples_exported": 0, "schema_version": SCHEMA_VERSION}


def publish_aggregate(path: Path = DB, output: Path = PUBLIC) -> dict:
    """Publish counts and schema only, with no match IDs, row values or labels."""
    if not path.is_file():
        raise FileNotFoundError(path)
    db = connect(path)
    tables = {name: db.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
              for name in ("games", "snapshots", "actors", "events", "windows")}
    splits = dict(db.execute("""SELECT g.split,COUNT(*) FROM windows w
      JOIN games g USING(match_id) GROUP BY g.split"""))
    event_types = dict(db.execute("SELECT event_type,COUNT(*) FROM events GROUP BY event_type"))
    relations = dict(db.execute("SELECT faker_relation,COUNT(*) FROM events GROUP BY faker_relation"))
    db.close()
    report = {"schema_version": SCHEMA_VERSION, "tables": tables,
              "windows_by_split": splits, "event_types": event_types,
              "faker_event_relation": relations, "stored_feature_count": len(FEATURE_NAMES),
              "strict_export_feature_count": len(EXPORT_FEATURES),
              "label_count": len(CLASSES), "future_horizon_seconds": HORIZON_MS // 1000,
              "position_sampling": "approximately 60 seconds; last observed frame",
              "event_sampling": "Riot event timestamps", "view": "omniscient timeline",
              "privacy": "row-level database and exports remain local"}
    atomic_json(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or export the private Faker IoC ledger")
    parser.add_argument("command", choices=("build", "export", "summary"))
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    result = (build(pilot=args.pilot) if args.command == "build" else
              export_train(limit=args.limit) if args.command == "export" else publish_aggregate())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
