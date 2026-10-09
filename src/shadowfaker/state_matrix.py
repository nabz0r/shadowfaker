"""Local, Faker-centred timeline warehouse and sparse observed transition matrix.

This database is deliberately ignored by Git. It stores observed state_t and
observed state_t+1 separately; Riot timelines do not contain mouse clicks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .events64 import event_category, position_cell
from .features import _participant, position, cs, number
from .finegrid import cell
from .util import atomic_json, read_json

DB = CONFIG.root / "data" / "processed64" / "faker_states.sqlite"
TRANSITIONS = CONFIG.root / "data" / "processed64" / "observed_transitions.npz"

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS matches (
 match_id TEXT PRIMARY KEY, source_sha256 TEXT NOT NULL, queue_id INTEGER,
 map_id INTEGER, champion_id INTEGER, own_participant_id INTEGER,
 state_count INTEGER NOT NULL, transition_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS states (
 match_id TEXT NOT NULL, frame_index INTEGER NOT NULL, timestamp_ms INTEGER NOT NULL,
 own_x REAL, own_y REAL, own_cell64 INTEGER, own_gold REAL, own_xp REAL,
 team_gold REAL, enemy_gold REAL, team_xp REAL, enemy_xp REAL,
 PRIMARY KEY(match_id,frame_index),
 FOREIGN KEY(match_id) REFERENCES matches(match_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS actors (
 match_id TEXT NOT NULL, frame_index INTEGER NOT NULL, participant_id INTEGER NOT NULL,
 side TEXT NOT NULL, role TEXT, champion_id INTEGER,
 x REAL, y REAL, cell64 INTEGER, gold REAL, xp REAL, level REAL, cs REAL,
 PRIMARY KEY(match_id,frame_index,participant_id),
 FOREIGN KEY(match_id,frame_index) REFERENCES states(match_id,frame_index) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS events (
 match_id TEXT NOT NULL, frame_index INTEGER NOT NULL, event_index INTEGER NOT NULL,
 timestamp_ms INTEGER NOT NULL, category TEXT NOT NULL, cell64 INTEGER,
 actor_id INTEGER, victim_id INTEGER, item_id INTEGER, skill_slot INTEGER,
 PRIMARY KEY(match_id,frame_index,event_index),
 FOREIGN KEY(match_id,frame_index) REFERENCES states(match_id,frame_index) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS transitions (
 match_id TEXT NOT NULL, frame_index INTEGER NOT NULL,
 from_cell64 INTEGER, to_cell64 INTEGER NOT NULL, dx REAL, dy REAL,
 first_item INTEGER, first_skill INTEGER,
 PRIMARY KEY(match_id,frame_index),
 FOREIGN KEY(match_id,frame_index) REFERENCES states(match_id,frame_index) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS states_time ON states(match_id,timestamp_ms);
CREATE INDEX IF NOT EXISTS actors_role ON actors(role,side,cell64);
CREATE INDEX IF NOT EXISTS events_type_time ON events(category,timestamp_ms);
CREATE INDEX IF NOT EXISTS transitions_cells ON transitions(from_cell64,to_cell64);
"""


def _frame_rows(match: dict, timeline: dict, puuid: str, mid: str) -> tuple[list, list, list, list]:
    pid, team_id, champion = _participant(match, timeline, puuid)
    players = (match.get("info") or {}).get("participants") or []
    teams = {int(p.get("participantId") or i+1): int(p.get("teamId") or 0) for i,p in enumerate(players)}
    roles = {int(p.get("participantId") or i+1): str(p.get("teamPosition") or "UNKNOWN") for i,p in enumerate(players)}
    champs = {int(p.get("participantId") or i+1): int(p.get("championId") or 0) for i,p in enumerate(players)}
    frames = (timeline.get("info") or {}).get("frames") or []
    states, actors, events, transitions = [], [], [], []
    for i, frame in enumerate(frames):
        pf = frame.get("participantFrames") or {}
        actor_frame = {p: pf.get(str(p)) or pf.get(p) or {} for p in range(1,11)}
        own = actor_frame[pid]
        own_pos = position(own)
        team_gold = sum(number(a.get("totalGold")) for p,a in actor_frame.items() if teams.get(p)==team_id)
        enemy_gold = sum(number(a.get("totalGold")) for p,a in actor_frame.items() if teams.get(p)!=team_id)
        team_xp = sum(number(a.get("xp")) for p,a in actor_frame.items() if teams.get(p)==team_id)
        enemy_xp = sum(number(a.get("xp")) for p,a in actor_frame.items() if teams.get(p)!=team_id)
        states.append((mid,i,int(number(frame.get("timestamp"),i*60000)),
                       None if own_pos is None else float(own_pos[0]),
                       None if own_pos is None else float(own_pos[1]),
                       None if own_pos is None else cell(own_pos),
                       number(own.get("totalGold")),number(own.get("xp")),team_gold,enemy_gold,team_xp,enemy_xp))
        for p,a in actor_frame.items():
            pos = position(a)
            actors.append((mid,i,p,"faker" if p==pid else "ally" if teams.get(p)==team_id else "enemy",
                           roles.get(p),champs.get(p),None if pos is None else float(pos[0]),
                           None if pos is None else float(pos[1]),None if pos is None else cell(pos),
                           number(a.get("totalGold")),number(a.get("xp")),number(a.get("level")),cs(a)))
        for j,event in enumerate(frame.get("events") or []):
            category = event_category(event,pid,team_id,teams)
            if category is None and event.get("type") not in ("ITEM_PURCHASED","SKILL_LEVEL_UP"):
                continue
            events.append((mid,i,j,int(number(event.get("timestamp"),frame.get("timestamp",i*60000))),
                           category or str(event.get("type")),position_cell(event),
                           int(event.get("participantId") or event.get("killerId") or event.get("creatorId") or 0),
                           int(event.get("victimId") or 0),int(event.get("itemId") or 0),int(event.get("skillSlot") or 0)))
        if i + 1 < len(frames):
            next_frame = frames[i+1]
            next_own = (next_frame.get("participantFrames") or {}).get(str(pid)) or (next_frame.get("participantFrames") or {}).get(pid) or {}
            destination = position(next_own)
            if destination is None:
                continue
            low = int(number(frame.get("timestamp"),i*60000))
            high = int(number(next_frame.get("timestamp"),(i+1)*60000))
            upcoming = [e for e in next_frame.get("events") or [] if low < number(e.get("timestamp"),high) <= high
                        and int(e.get("participantId") or 0)==pid]
            purchases = [int(e.get("itemId")) for e in upcoming if e.get("type")=="ITEM_PURCHASED" and e.get("itemId")]
            skills = [int(e.get("skillSlot")) for e in upcoming if e.get("type")=="SKILL_LEVEL_UP" and e.get("skillSlot")]
            transitions.append((mid,i,None if own_pos is None else cell(own_pos),cell(destination),
                                None if own_pos is None else float(destination[0]-own_pos[0]),
                                None if own_pos is None else float(destination[1]-own_pos[1]),
                                purchases[0] if purchases else None,skills[0] if skills else None))
    return states,actors,events,transitions


def build(limit: int | None = None, db_path: Path = DB, matrix_path: Path = TRANSITIONS) -> dict:
    manifest = read_json(CONFIG.raw / "manifest.json")
    meta = read_json(CONFIG.processed / "meta.json")
    if not manifest or not meta: raise FileNotFoundError("Fetch and parse ranked matches first")
    allowed = set(meta["counts"])
    ids = [mid for mid in manifest["order"] if mid in allowed]
    if limit is not None: ids = ids[:limit]
    db_path.parent.mkdir(parents=True,exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.executescript(SCHEMA)
    written,skipped,errors = 0,0,{}
    for mid in tqdm(ids,desc="Faker state warehouse",unit="game"):
        try:
            match_path = CONFIG.raw / "matches" / f"{mid}.json"
            timeline_path = CONFIG.raw / "timelines" / f"{mid}.json"
            source = timeline_path.read_bytes()
            fingerprint = hashlib.sha256(match_path.read_bytes()+source).hexdigest()
            existing = connection.execute("SELECT source_sha256 FROM matches WHERE match_id=?",(mid,)).fetchone()
            if existing and existing[0]==fingerprint:
                skipped += 1
                continue
            match,timeline = json.loads(match_path.read_text()),json.loads(source)
            states,actors,events,transitions = _frame_rows(match,timeline,manifest["account"]["puuid"],mid)
            if not states: raise ValueError("No timeline states")
            own_pid,_,champion = _participant(match,timeline,manifest["account"]["puuid"])
            info = match.get("info") or {}
            with connection:
                connection.execute("DELETE FROM matches WHERE match_id=?",(mid,))
                connection.execute("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?)",
                                   (mid,fingerprint,int(info.get("queueId") or -1),int(info.get("mapId") or -1),
                                    champion,own_pid,len(states),len(transitions)))
                connection.executemany("INSERT INTO states VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",states)
                connection.executemany("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",actors)
                connection.executemany("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?)",events)
                connection.executemany("INSERT INTO transitions VALUES (?,?,?,?,?,?,?,?)",transitions)
            written += 1
        except Exception as exc:
            errors[mid] = str(exc)
    # Sparse CSR: row = current observed cell, column = next observed cell.
    # Reuse SQL counts directly instead of expanding observations in memory.
    counts = {(int(a),int(b)):int(n) for a,b,n in connection.execute(
        "SELECT from_cell64,to_cell64,COUNT(*) FROM transitions WHERE from_cell64 IS NOT NULL GROUP BY from_cell64,to_cell64")}
    keys = sorted(counts)
    indptr = np.zeros(4097,dtype=np.int64)
    for a,_ in keys: indptr[a+1] += 1
    indptr = np.cumsum(indptr)
    np.savez_compressed(matrix_path,indptr=indptr,indices=np.asarray([b for _,b in keys],np.int32),
                        counts=np.asarray([counts[key] for key in keys],np.int32),shape=np.asarray([4096,4096]))
    report = {"schema_version":1,"matches_in_database":connection.execute("SELECT COUNT(*) FROM matches").fetchone()[0],
              "states":connection.execute("SELECT COUNT(*) FROM states").fetchone()[0],
              "transitions":connection.execute("SELECT COUNT(*) FROM transitions").fetchone()[0],
              "events":connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
              "sparse_nonzero_transitions":len(keys),"written":written,"cached":skipped,"errors":errors,
              "clicks_available":False,"source":"same-PUUID ranked solo timeline, local only"}
    connection.close()
    atomic_json(db_path.with_suffix(".summary.json"),report)
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--limit",type=int)
    args=parser.parse_args()
    print(build(args.limit))


if __name__=="__main__": main()
