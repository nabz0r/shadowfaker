"""Causal enemy-response and ally-cover variables for a separate neural candidate."""
import argparse
import copy
from pathlib import Path

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .features import FEATURE_NAMES, _save_npz
from .util import atomic_json, read_json

ROOT = CONFIG.root / "data" / "interaction"
NAMES = ["visible_enemy_count", "enemy_within_2500", "enemy_within_5000",
         "enemy_moves_toward_prior_faker", "allies_within_2500", "nearby_enemy_gold",
         "nearest_visible_enemy_distance", "nearest_visible_enemy_level_gap",
         "visible_enemy_jungle_to_dragon", "visible_enemy_jungle_to_baron",
         "enemy_dragon_presence", "enemy_baron_presence", "jungler_cover_under_pressure"]


def interaction_channels(window: np.ndarray) -> np.ndarray:
    """Every output step uses only this and earlier input frames (proxy or oracle)."""
    out=np.zeros((len(window),len(NAMES)),dtype=np.float32)
    dragon=np.array([9866,4414],dtype=np.float32)/15000
    baron=np.array([5007,10471],dtype=np.float32)/15000
    for step,frame in enumerate(window):
        own=frame[17:19]
        if frame[19] <= .5: continue
        allies=[frame[17+i*9:17+i*9+9] for i in range(1,5)]
        enemies=[frame[17+i*9:17+i*9+9] for i in range(5,10)]
        visible=[enemy for enemy in enemies if enemy[2]>.5]
        distances=[float(np.linalg.norm(enemy[:2]-own)) for enemy in visible]
        near=[enemy for enemy,distance in zip(visible,distances) if distance<=2500/15000]
        close_allies=[ally for ally in allies if ally[2]>.5 and np.linalg.norm(ally[:2]-own)<=2500/15000]
        out[step,0]=len(visible)/5
        out[step,1]=len(near)/5
        out[step,2]=sum(distance<=5000/15000 for distance in distances)/5
        out[step,4]=len(close_allies)/4
        out[step,5]=sum(enemy[8] for enemy in near)/5
        out[step,6]=min(distances) if distances else 1.5
        if visible:
            nearest=visible[int(np.argmin(distances))]
            out[step,7]=nearest[5]-frame[22]
        jungle=next((enemy for enemy in visible if round(float(enemy[4])*5)==2),None)
        if jungle is not None:
            out[step,8]=np.linalg.norm(jungle[:2]-dragon)
            out[step,9]=np.linalg.norm(jungle[:2]-baron)
        else: out[step,8:10]=1.5
        out[step,10]=sum(np.linalg.norm(enemy[:2]-dragon)<=2500/15000 for enemy in visible)/5
        out[step,11]=sum(np.linalg.norm(enemy[:2]-baron)<=2500/15000 for enemy in visible)/5
        ally_jungle=next((ally for ally in close_allies if round(float(ally[4])*5)==2),None)
        out[step,12]=float(ally_jungle is not None and bool(near))
        if step and window[step-1,19]>.5:
            previous=window[step-1]
            prior_own=previous[17:19]
            approaching=0
            for i in range(5,10):
                p=17+i*9
                if previous[p+2]>.5 and frame[p+2]>.5:
                    before=np.linalg.norm(previous[p:p+2]-prior_own)
                    after=np.linalg.norm(frame[p:p+2]-prior_own)
                    approaching+=bool(after+1e-5<before)
            out[step,3]=approaching/5
    return out


def prepare(limit: int | None = None, output: Path = ROOT) -> dict:
    old=read_json(CONFIG.processed/"meta.json")
    if not old: raise FileNotFoundError("Parse ranked matches first")
    ids=[mid for split in ("train","val","test") for mid in old["splits"][split]]
    if limit is not None: ids=ids[:limit]
    output.joinpath("matches").mkdir(parents=True,exist_ok=True)
    counts={};errors={}
    for mid in tqdm(ids,desc="interaction features",unit="game"):
        try:
            destination=output/"matches"/f"{mid}.npz"
            if not destination.exists():
                with np.load(CONFIG.processed/"matches"/f"{mid}.npz") as z:
                    data={key:z[key] for key in z.files}
                for key in ("x","x_oracle"):
                    base=data[key]
                    extra=np.stack([interaction_channels(one) for one in base])
                    data[key]=np.concatenate((base,extra),axis=-1)
                _save_npz(destination,data)
            with np.load(destination) as z: counts[mid]=len(z["x"])
        except Exception as exc: errors[mid]=str(exc)
    meta=copy.deepcopy(old)
    meta["schema_version"]=100+old["schema_version"]
    meta["feature_names"]=FEATURE_NAMES+NAMES
    meta["feature_dim"]=len(meta["feature_names"])
    meta["interaction_feature_names"]=NAMES
    meta["interaction_note"]="Only observed/proxy state_t and earlier; enemy reaction is movement toward Faker's previous position, not causal influence."
    meta["counts"]=counts
    meta["errors"]=errors
    meta["observations"]=sum(counts.values())
    meta["splits"]={split:[mid for mid in old["splits"][split] if mid in counts] for split in ("train","val","test")}
    if limit is not None and min(map(len,meta["splits"].values()))==0:
        meta["splits"]={"train":ids[2:],"val":[ids[1]],"test":[ids[0]]}
    atomic_json(output/"meta.json",meta)
    return meta


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--limit",type=int)
    args=parser.parse_args()
    meta=prepare(args.limit)
    print({"feature_dim":meta["feature_dim"],"observations":meta["observations"],
           "matches":len(meta["counts"]),"errors":len(meta["errors"]),
           "splits":{k:len(v) for k,v in meta["splits"].items()}})


if __name__=="__main__":main()
