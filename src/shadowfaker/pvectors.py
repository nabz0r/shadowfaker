"""Local neural state vectors and retrospective game vectors centred on Faker.

The 128-D state vectors come from the trained 16x16 encoder. Their labels are
never part of the encoding. A game vector summarizes a completed game and is
only for retrieval, never a causal prediction feature.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm

from .config import CONFIG
from .evaluate import load_model
from .finegrid import ROOT64
from .util import atomic_json, read_json

ROOT = CONFIG.root / "data" / "pvectors"


def encode(model, x: torch.Tensor, champion: torch.Tensor) -> torch.Tensor:
    h = model.numeric(x) + model.champion(champion.clamp(0,999))[:,None,:]
    h = h + model.time(torch.arange(x.shape[1],device=x.device))[None]
    return model.norm(model.encoder(h)[:,-1])


def build(output: Path = ROOT, limit: int | None = None) -> dict:
    meta = read_json(ROOT64 / "meta.json")
    if not meta: raise FileNotFoundError("Prepare 64x64 observations first")
    checkpoint = CONFIG.models / "best.pt"
    checkpoint_hash = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    ids = [mid for split in ("train","val","test") for mid in meta["splits"][split]]
    if limit is not None: ids=ids[:limit]
    signature = hashlib.sha256(json.dumps({"checkpoint":checkpoint_hash,"ids":ids,
                                            "counts":meta["counts"]},sort_keys=True).encode()).hexdigest()
    existing = read_json(output / "index.json")
    if existing and existing.get("signature")==signature and all((output/name).is_file() for name in
        ("states.npy","labels64.npy","games.npy","index.json")):
        return existing
    model = load_model(read_json(CONFIG.processed / "meta.json"),checkpoint)
    model.eval()
    output.mkdir(parents=True,exist_ok=True)
    total=sum(meta["counts"][mid] for mid in ids)
    width=model.numeric.out_features
    vectors=np.lib.format.open_memmap(output/"states.npy",mode="w+",dtype=np.float32,shape=(total,width))
    labels=np.lib.format.open_memmap(output/"labels64.npy",mode="w+",dtype=np.int32,shape=(total,))
    games=np.lib.format.open_memmap(output/"games.npy",mode="w+",dtype=np.float32,shape=(len(ids),width+64))
    records=[]; cursor=0
    with torch.no_grad():
        for game_idx,mid in enumerate(tqdm(ids,desc="neural pvector index",unit="game")):
            source=CONFIG.processed/"matches"/f"{mid}.npz"
            if not source.exists(): source=ROOT64/"matches"/f"{mid}.npz"
            with np.load(source) as state,np.load(ROOT64/"labels"/f"{mid}.npz") as target:
                x=state["x_oracle" if model.view=="oracle" else "x"]
                champion=state["champion"]
                vectors_one=np.concatenate([encode(model,torch.from_numpy(x[i:i+128].copy()),
                                                    torch.from_numpy(champion[i:i+128].copy())).numpy()
                                            for i in range(0,len(x),128)])
                norm=np.linalg.norm(vectors_one,axis=1,keepdims=True).clip(1e-8)
                vectors_one=(vectors_one/norm).astype(np.float32)
                count=len(vectors_one)
                vectors[cursor:cursor+count]=vectors_one
                labels[cursor:cursor+count]=target["region"]
                histogram=np.bincount((target["region"]//64//8)*8+(target["region"]%64//8),minlength=64)
                histogram=histogram/max(1,histogram.sum())
                # The final 64 values use completed-game destinations and are retrospective only.
                games[game_idx]=np.concatenate((vectors_one.mean(axis=0),histogram))
                records.append({"match_id":mid,"split":next(k for k in ("train","val","test") if mid in meta["splits"][k]),
                                "start":cursor,"count":count,"game_index":game_idx})
                cursor+=count
    del vectors,labels,games
    report={"schema_version":1,"signature":signature,"encoder_checkpoint_sha256":checkpoint_hash,
            "state_dimensions":width,"game_dimensions":width+64,"states":total,"games":len(ids),
            "records":records,"game_vector_uses_future":True,
            "note":"The game vectors are retrospective retrieval artifacts; state vectors use only the causal input window."}
    atomic_json(output/"index.json",report)
    return report


def nearest_games(match_id: str, k: int = 5, output: Path = ROOT) -> list[dict]:
    index=read_json(output/"index.json")
    records=index["records"]
    source=next((r for r in records if r["match_id"]==match_id),None)
    if source is None: raise KeyError(match_id)
    game=np.load(output/"games.npy",mmap_mode="r")
    vectors=np.asarray(game)
    norm=np.linalg.norm(vectors,axis=1).clip(1e-8)
    scores=(vectors@vectors[source["game_index"]])/(norm*norm[source["game_index"]])
    scores[source["game_index"]]=-np.inf
    selected=np.argsort(scores)[-k:][::-1]
    return [{"match_id":records[int(j)]["match_id"],"split":records[int(j)]["split"],
             "cosine":round(float(scores[j]),4)} for j in selected]


def validate_knn(output: Path = ROOT, k: int = 25) -> dict:
    index=read_json(output/"index.json")
    records=index["records"]
    train=[r for r in records if r["split"]=="train"]
    val=[r for r in records if r["split"]=="val"]
    vectors=np.load(output/"states.npy",mmap_mode="r")
    labels=np.load(output/"labels64.npy",mmap_mode="r")
    train_end=train[-1]["start"]+train[-1]["count"]
    val_start,val_end=val[0]["start"],val[-1]["start"]+val[-1]["count"]
    train_vectors=np.asarray(vectors[:train_end])
    train_labels=np.asarray(labels[:train_end])
    val_vectors=np.asarray(vectors[val_start:val_end])
    true=np.asarray(labels[val_start:val_end])
    predictions=[]
    for start in tqdm(range(0,len(val_vectors),64),desc="pvector validation",unit="batch"):
        scores=val_vectors[start:start+64]@train_vectors.T
        candidates=np.argpartition(scores,-k,axis=1)[:,-k:]
        for row,near in enumerate(candidates):
            votes=np.bincount(train_labels[near],weights=np.maximum(0,scores[row,near])**4,minlength=4096)
            predictions.append(int(votes.argmax()))
    pred=np.asarray(predictions)
    distance=np.hypot(pred%64-true%64,pred//64-true//64)
    common=int(np.bincount(train_labels,minlength=4096).argmax())
    report={"schema_version":1,"split":"val","matches":len(val),"samples":len(true),"k":k,
            "exact64":float(np.mean(pred==true)),"within4_cells":float(np.mean(distance<=4)),
            "mean_distance_cells":float(distance.mean()),"train_mode_exact64":float(np.mean(true==common)),
            "note":"Exploratory nearest-neighbour baseline; learned encoder was trained only on training matches, but this k value is not prospectively frozen."}
    atomic_json(CONFIG.artifacts/"pvector_validation.json",report)
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=("build","validate","nearest"))
    parser.add_argument("--match-id")
    parser.add_argument("--limit",type=int)
    args=parser.parse_args()
    if args.stage=="build":
        result=build(limit=args.limit)
        print({key:value for key,value in result.items() if key!="records"})
    elif args.stage=="validate": print(validate_knn())
    else: print(nearest_games(args.match_id or read_json(ROOT/"index.json")["records"][0]["match_id"]))


if __name__=="__main__": main()
