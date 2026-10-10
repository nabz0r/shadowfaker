"""Small marked-event predictor, evaluated only on held-out validation matches."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import random

import numpy as np
import torch
from torch import nn

from .config import CONFIG
from .event_clock import CLASSES, FEATURES, SCHEMA_VERSION
from .util import atomic_json, read_json

DATA = CONFIG.processed / "event_clock"
MODEL = CONFIG.models / "event_clock.pt"
RESULT = CONFIG.artifacts / "event_clock_validation.json"


class EventMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(len(FEATURES), 128), nn.GELU(),
                                 nn.Linear(128, 128), nn.GELU(),
                                 nn.Linear(128, len(CLASSES)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def _iter_batches(ids: list[str], batch: int, shuffle: bool, rng: random.Random):
    ids = list(ids)
    if shuffle:
        rng.shuffle(ids)
    for mid in ids:
        with np.load(DATA / f"{mid}.npz") as z:
            x, y = z["x"], z["y"].astype(np.int64)
        order = np.arange(len(y))
        if shuffle:
            rng.shuffle(order)
        for start in range(0,len(order),batch):
            select = order[start:start+batch]
            yield mid, x[select], y[select]


def _frequencies(ids: list[str]) -> tuple[np.ndarray, np.ndarray]:
    total = np.ones(len(CLASSES), dtype=np.float64)  # Dirichlet smoothing
    by_phase = np.ones((3,len(CLASSES)), dtype=np.float64)
    for mid in ids:
        with np.load(DATA / f"{mid}.npz") as z:
            y, minute = z["y"].astype(int), z["x"][:,0]*60
        np.add.at(total, y, 1)
        phase = np.where(minute < 10, 0, np.where(minute < 20, 1, 2))
        np.add.at(by_phase, (phase,y), 1)
    return total/total.sum(), by_phase/by_phase.sum(axis=1,keepdims=True)


def _metrics(prob: np.ndarray, label: np.ndarray) -> dict:
    prediction = prob.argmax(axis=1)
    onehot = np.eye(len(CLASSES))[label]
    tp = np.bincount(label[prediction==label], minlength=len(CLASSES))
    predicted = np.bincount(prediction, minlength=len(CLASSES))
    actual = np.bincount(label, minlength=len(CLASSES))
    precision = tp/np.maximum(1,predicted)
    recall = tp/np.maximum(1,actual)
    f1 = np.where(precision+recall > 0, 2*precision*recall/np.maximum(precision+recall,1e-9),0)
    return {"n": len(label), "accuracy": float(np.mean(prediction==label)),
            "nll": float(-np.log(np.maximum(prob[np.arange(len(label)),label],1e-9)).mean()),
            "brier": float(np.mean(np.sum((prob-onehot)**2,axis=1))),
            "macro_f1": float(f1.mean()),
            "event_binary_recall": float(((prediction!=0)&(label!=0)).sum()/max(1,(label!=0).sum())),
            "by_class_f1": {name: float(f1[i]) for i,name in enumerate(CLASSES)}}


def run(pilot: bool = False, epochs: int = 25, batch: int = 512,
        with_euw: bool = False) -> dict:
    torch.manual_seed(CONFIG.seed)
    np.random.seed(CONFIG.seed)
    rng = random.Random(CONFIG.seed)
    parent = read_json(CONFIG.processed / "meta.json")
    generated = read_json(DATA / "meta.json")
    if generated.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Build event_clock dataset first")
    train_ids = [mid for mid in parent["splits"]["train"] if (DATA/f"{mid}.npz").exists()]
    val_ids = [mid for mid in parent["splits"]["val"] if (DATA/f"{mid}.npz").exists()]
    if pilot:
        train_ids, val_ids = train_ids[:3], val_ids[:2]
    if with_euw:
        alias = read_json(DATA / "alias_meta.json")
        if alias.get("schema_version") != SCHEMA_VERSION or alias.get("matches") != 31:
            raise ValueError("Build the complete EUW auxiliary dataset first")
        alias_manifest = read_json(CONFIG.raw / "aliases" / "manifest.json")
        train_ids += [mid for mid,row in alias_manifest["games"].items()
                      if row.get("status") == "ok" and row.get("alias") == "Hide on bush#61151"]
    if not train_ids or not val_ids:
        raise ValueError("Need disjoint train and validation matches")
    if set(train_ids)&set(val_ids):
        raise AssertionError("match leakage")
    global_prob, phase_prob = _frequencies(train_ids)
    # CPU is the reproducible default for the small batches in this head. The
    # existing pipeline benchmarks MPS separately for its larger transformer.
    device = torch.device("cpu")
    net = EventMLP().to(device)
    optimizer = torch.optim.AdamW(net.parameters(), lr=8e-4, weight_decay=1e-3)
    best, best_epoch, stale, history = float("inf"), 0, 0, []
    target_model = MODEL.with_name("event_clock_pilot.pt" if pilot else
                                   "event_clock_euw.pt" if with_euw else "event_clock.pt")
    target_model.parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(1,epochs+1):
        net.train()
        train_loss, train_n = 0.0, 0
        for _, x,y in _iter_batches(train_ids,batch,True,rng):
            xb = torch.from_numpy(x).to(device)
            yb = torch.from_numpy(y).to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = nn.functional.cross_entropy(net(xb), yb)
            loss.backward()
            optimizer.step()
            train_loss += float(loss.detach())*len(y)
            train_n += len(y)
        net.eval()
        val_loss, val_n = 0.0, 0
        with torch.no_grad():
            for _,x,y in _iter_batches(val_ids,batch,False,rng):
                logits = net(torch.from_numpy(x).to(device))
                val_loss += float(nn.functional.cross_entropy(logits,torch.from_numpy(y).to(device)))*len(y)
                val_n += len(y)
        score = val_loss/val_n
        history.append({"epoch": epoch, "train_nll": train_loss/train_n, "val_nll": score})
        if score < best-1e-4:
            best, best_epoch, stale = score, epoch, 0
            torch.save(net.state_dict(),target_model)
        else:
            stale += 1
            if stale >= 3:
                break
    net.load_state_dict(torch.load(target_model,map_location=device,weights_only=True))
    net.eval()
    labels, pred, phases = [], [], []
    with torch.no_grad():
        for _,x,y in _iter_batches(val_ids,batch,False,rng):
            labels.append(y)
            pred.append(net(torch.from_numpy(x)).softmax(-1).numpy())
            phases.append(np.where(x[:,0]*60<10,0,np.where(x[:,0]*60<20,1,2)))
    label = np.concatenate(labels)
    prob = np.concatenate(pred)
    phase = np.concatenate(phases)
    report = {"schema_version": 1, "pilot": pilot, "with_euw": with_euw,
              "target": "first marked event in next 10 seconds",
              "train_matches": len(train_ids), "validation_matches": len(val_ids),
              "train_windows": 0, "validation_windows": len(label),
              "parameters": sum(p.numel() for p in net.parameters()),
              "best_epoch": best_epoch, "history": history,
              "model": _metrics(prob,label),
              "global_frequency": _metrics(np.broadcast_to(global_prob,prob.shape),label),
              "phase_frequency": _metrics(phase_prob[phase],label),
              "class_counts_validation": dict(zip(CLASSES,np.bincount(label,minlength=len(CLASSES)).tolist())),
              "selection": "validation only; historic test and prospective lockbox untouched",
              "position_note": "10-second event locus is not Faker's position"}
    # Exact train count is read from local files, not inferred from total corpus.
    for mid in train_ids:
        with np.load(DATA/f"{mid}.npz") as z:
            report["train_windows"] += len(z["y"])
    output = RESULT.with_name("event_clock_pilot.json" if pilot else
                              "event_clock_euw_validation.json" if with_euw else "event_clock_validation.json")
    output.parent.mkdir(parents=True,exist_ok=True)
    atomic_json(output,report)
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pilot",action="store_true")
    p.add_argument("--with-euw",action="store_true")
    p.add_argument("--epochs",type=int,default=25)
    a=p.parse_args()
    r=run(a.pilot,a.epochs,with_euw=a.with_euw)
    print(json.dumps({k:v for k,v in r.items() if k != "history"},indent=2))


if __name__ == "__main__":
    main()
