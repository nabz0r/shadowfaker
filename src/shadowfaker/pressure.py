"""Enemy movement and local proximity around Faker, measured without intent claims."""
import argparse
from collections import defaultdict
from pathlib import Path
import sqlite3

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .state_matrix import DB
from .util import atomic_json

PUBLIC = CONFIG.root / "docs" / "data" / "public_pressure.json"
RADII_UNITS = (1000, 1500, 2500, 3500, 5000)
DEFAULT_RADIUS_UNITS = 2500


def summarize(limit: int | None = None, database: Path = DB, output: Path = PUBLIC) -> dict:
    db=sqlite3.connect(database)
    ids=[row[0] for row in db.execute("SELECT match_id FROM matches ORDER BY match_id")]
    if limit is not None: ids=ids[:limit]
    table={name:{"frames":0,"near_enemies":0,"near_allies":0,"enemy_arrivals":0,
                 "nearest_distance_sum":0.0} for name in ("0/1","0/2","other")}
    phase={name:{"frames":0,"near_enemies":0,"enemy_arrivals":0,
                 "enemy_density":[0]*4096,"ally_density":[0]*4096} for name in ("early","middle","late")}
    profiles={str(radius): {
        "phases": {name: {"frames": 0, "near_enemies": 0, "enemy_arrivals": 0}
                   for name in ("early", "middle", "late")},
        "score_slices": {name: {"frames": 0, "near_enemies": 0, "enemy_arrivals": 0}
                         for name in ("0/1", "0/2", "other")}}
        for radius in RADII_UNITS}
    count=0
    for mid in tqdm(ids,desc="enemy pressure around Faker",unit="game"):
        rows=db.execute("""SELECT a.frame_index,a.participant_id,a.side,a.x,a.y,a.cell64,s.timestamp_ms
            FROM actors a JOIN states s ON s.match_id=a.match_id AND s.frame_index=a.frame_index
            WHERE a.match_id=? ORDER BY a.frame_index,a.participant_id""",(mid,)).fetchall()
        deaths=defaultdict(lambda:[0,0])
        for frame,category in db.execute("SELECT frame_index,category FROM events WHERE match_id=? AND category IN ('faker_kill','faker_death')",(mid,)):
            deaths[frame][0 if category=="faker_kill" else 1]+=1
        grouped=defaultdict(list)
        for row in rows: grouped[row[0]].append(row)
        prev_near={radius:set() for radius in RADII_UNITS};prev_known=set();kills=dead=0
        for frame,actors in sorted(grouped.items()):
            kills+=deaths[frame][0];dead+=deaths[frame][1]
            own=next((a for a in actors if a[2]=="faker"),None)
            if own is None or own[3] is None:
                prev_near={radius:set() for radius in RADII_UNITS};prev_known=set();continue
            minute=own[6]/60000
            period="early" if minute<10 else "middle" if minute<20 else "late"
            nearby={radius:set() for radius in RADII_UNITS};known_enemies=set()
            near_allies=[];enemy_distances=[]
            for actor in actors:
                if actor[5] is not None:
                    if actor[2]=="enemy": phase[period]["enemy_density"][actor[5]]+=1
                    elif actor[2]=="ally": phase[period]["ally_density"][actor[5]]+=1
                if actor[3] is None or actor[2]=="faker": continue
                distance=((actor[3]-own[3])**2+(actor[4]-own[4])**2)**.5
                if actor[2]=="enemy":
                    known_enemies.add(actor[1])
                    enemy_distances.append(distance)
                    for radius in RADII_UNITS:
                        if distance<=radius/15000: nearby[radius].add(actor[1])
                elif distance<=DEFAULT_RADIUS_UNITS/15000: near_allies.append(actor[1])
            near_enemies=nearby[DEFAULT_RADIUS_UNITS]
            arrivals=len((near_enemies-prev_near[DEFAULT_RADIUS_UNITS]) & prev_known)
            group="0/1" if kills==0 and dead==1 else "0/2" if kills==0 and dead==2 else "other"
            for radius, present in nearby.items():
                entered=len((present-prev_near[radius]) & prev_known)
                for bucket in (profiles[str(radius)]["phases"][period],
                               profiles[str(radius)]["score_slices"][group]):
                    bucket["frames"]+=1
                    bucket["near_enemies"]+=len(present)
                    bucket["enemy_arrivals"]+=entered
                prev_near[radius]=present
            prev_known=known_enemies
            table[group]["frames"]+=1
            table[group]["near_enemies"]+=len(near_enemies)
            table[group]["near_allies"]+=len(near_allies)
            table[group]["enemy_arrivals"]+=arrivals
            table[group]["nearest_distance_sum"]+=min(enemy_distances) if enemy_distances else 1
            phase[period]["frames"]+=1
            phase[period]["near_enemies"]+=len(near_enemies)
            phase[period]["enemy_arrivals"]+=arrivals
            count+=1
    for values in table.values():
        n=values["frames"]
        values["mean_near_enemies"]=values["near_enemies"]/n if n else None
        values["mean_near_allies"]=values["near_allies"]/n if n else None
        values["mean_nearest_enemy_units"]=values.pop("nearest_distance_sum")/n*15000 if n else None
        values["arrival_rate_per_frame"]=values["enemy_arrivals"]/n if n else None
    for values in phase.values():
        n=max(1,values["frames"])
        values["mean_near_enemies"]=values["near_enemies"]/n
        values["arrival_rate_per_frame"]=values["enemy_arrivals"]/n
    for profile in profiles.values():
        for bucket in (*profile["phases"].values(), *profile["score_slices"].values()):
            n=bucket["frames"]
            bucket["mean_near_enemies"]=bucket["near_enemies"]/n if n else None
            bucket["arrival_rate_per_frame"]=bucket["enemy_arrivals"]/n if n else None
    report={"schema_version":2,"source_matches":len(ids),"states_with_faker_position":count,
            "radius_units":DEFAULT_RADIUS_UNITS,"available_radii_units":list(RADII_UNITS),
            "radius_profiles":profiles,"score_slices":table,"phases":phase,
            "warning":"Enemy positions are timeline god-view. Arrival means a known enemy was outside the chosen circle in the prior sampled frame and inside it in the current frame; missing positions and first frames do not count. This is a net sampled proximity proxy, not vision, resource spending, target intent or causal impact."}
    atomic_json(output,report)
    db.close()
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--limit",type=int)
    args=parser.parse_args()
    result=summarize(args.limit)
    print({k:v for k,v in result.items() if k!="phases"})


if __name__=="__main__":main()
