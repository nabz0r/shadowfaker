"""Development-only 512² destination adapter over the frozen 64² model.

The parent model and historical test are never trained or scored here. A 64-way
conditional head selects one 8x8 subcell inside a parent 64x64 cell. Inference
uses a declared top-16 parent beam rather than a dense 262,144-class head.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from .config import CONFIG
from .finegrid import Grid64Dataset, Grid64Transformer, ROOT64, MODELS64
from .hierarchical import MatchBatchSampler
from .util import atomic_json, read_json, seed_all

GRID = 512
PARENT = 64
SUB = GRID // PARENT
MODELS = CONFIG.models / "grid512"
ARTIFACTS = CONFIG.artifacts / "grid512"


def cell512(xy: np.ndarray | torch.Tensor):
    """Normalized x/y to row-major 512² cells, with the upper edge clamped."""
    if isinstance(xy, torch.Tensor):
        integer = (xy.clamp(0, 1) * GRID).long().clamp(0, GRID - 1)
        return integer[..., 1] * GRID + integer[..., 0]
    integer = np.clip(np.asarray(xy) * GRID, 0, GRID - 1).astype(np.int64)
    return integer[..., 1] * GRID + integer[..., 0]


def parent64(cells):
    return (cells // GRID // SUB) * PARENT + (cells % GRID // SUB)


def subcell(cells):
    return (cells // GRID % SUB) * SUB + cells % SUB


def combine(parent, local):
    return ((parent // PARENT) * SUB + local // SUB) * GRID + (parent % PARENT) * SUB + local % SUB


class SubcellHead(nn.Module):
    def __init__(self, width: int = 128):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(width + 4, 128), nn.GELU(), nn.Linear(128, 64))

    def forward(self, h: torch.Tensor, forecast_xy: torch.Tensor, parents: torch.Tensor):
        centers = torch.stack(((parents % PARENT + .5) / PARENT,
                               (parents // PARENT + .5) / PARENT), -1)
        if parents.ndim == 2:
            h = h[:, None, :].expand(-1, parents.shape[1], -1)
            forecast_xy = forecast_xy[:, None, :].expand_as(centers)
        delta = (forecast_xy - centers) * PARENT
        return self.network(torch.cat((h, centers, delta), -1))


def _parent_model(device: str, checkpoint: Path = MODELS64 / "best.pt"):
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = Grid64Transformer(saved["width"], saved["layers"])
    model.load_state_dict(saved["state_dict"])
    model.to(device).eval()
    for parameter in model.parameters(): parameter.requires_grad_(False)
    return model, saved


def _loader(meta: dict, split: str, batch_size: int, pilot: bool):
    ids = meta["splits"][split][:4 if split == "train" else 1] if pilot else meta["splits"][split]
    local = dict(meta)
    local["splits"] = {**meta["splits"], split: ids}
    dataset = Grid64Dataset(local, split, ROOT64)
    if split == "train":
        return DataLoader(dataset, batch_sampler=MatchBatchSampler(dataset, batch_size)), ids
    return DataLoader(dataset, batch_size=batch_size), ids


def _epoch(base, head, loader, optimizer, device: str):
    train = optimizer is not None
    head.train(train)
    total = hits = count = 0
    for x, champion, region64, xy in loader:
        x, champion, region64, xy = (v.to(device) for v in (x, champion, region64, xy))
        target = cell512(xy)
        if not torch.equal(parent64(target), region64):
            raise ValueError("512 labels do not align with saved 64 parent cells")
        with torch.no_grad(): h, forecast = base.encode(x, champion)
        with torch.set_grad_enabled(train):
            logits = head(h, forecast, region64)
            label = subcell(target)
            loss = F.cross_entropy(logits, label)
            if train:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
        total += float(loss.detach()) * len(x)
        hits += int((logits.argmax(-1) == label).sum())
        count += len(x)
    return {"conditional_loss": total / max(1, count), "oracle_parent_subcell_top1": hits / max(1, count), "samples": count}


def train(epochs: int = 12, patience: int = 3, batch_size: int = 64, pilot: bool = False,
          models: Path | None = None) -> dict:
    meta = read_json(ROOT64 / "meta.json")
    if not meta or meta.get("grid") != PARENT:
        raise FileNotFoundError("Prepare the 64x64 ranked labels first")
    models = models or (MODELS / "pilot" if pilot else MODELS)
    models.mkdir(parents=True, exist_ok=True)
    parent_path = MODELS64 / "best.pt"
    digest = hashlib.sha256(parent_path.read_bytes()).hexdigest()
    train_loader, train_ids = _loader(meta, "train", batch_size, pilot)
    val_loader, val_ids = _loader(meta, "val", batch_size, pilot)
    signature = hashlib.sha256(json.dumps({"parent_sha256": digest, "train_ids": train_ids,
                                            "val_ids": val_ids, "grid": GRID, "seed": CONFIG.seed},
                                           sort_keys=True).encode()).hexdigest()
    path = models / "best.pt"
    if path.exists():
        saved = torch.load(path, map_location="cpu", weights_only=False)
        if saved.get("signature") == signature and saved.get("epochs_target", 0) >= epochs:
            return read_json(models / "training.json")
    seed_all(CONFIG.seed)
    candidate_devices = ["cpu", "mps"] if torch.backends.mps.is_available() else ["cpu"]
    timings = {}
    for device in candidate_devices:
        base, saved = _parent_model(device)
        seed_all(CONFIG.seed)
        head = SubcellHead(saved["width"]).to(device)
        sample = next(iter(val_loader))
        start = time.perf_counter()
        x, champion, parent, xy = (v.to(device) for v in sample)
        with torch.no_grad():
            h, forecast = base.encode(x, champion)
            head(h, forecast, parent)
        if device == "mps": torch.mps.synchronize()
        timings[device] = round(time.perf_counter() - start, 4)
        del base, head
    device = min(timings, key=timings.get)
    base, saved = _parent_model(device)
    seed_all(CONFIG.seed)
    head = SubcellHead(saved["width"]).to(device)
    parameters = sum(p.numel() for p in head.parameters())
    if parameters >= 5_000_000: raise ValueError("512 adapter exceeds model budget")
    optimizer = torch.optim.AdamW(head.parameters(), lr=3e-4, weight_decay=.01)
    report = {"grid": GRID, "parent_grid": PARENT, "adapter_parameters": parameters,
              "parent_sha256": digest, "device": device, "benchmark_seconds": timings,
              "pilot": pilot, "train_matches": len(train_ids), "val_matches": len(val_ids),
              "signature": signature, "epochs_target": epochs, "history": []}
    best, stale = math.inf, 0
    for epoch in tqdm(range(1, epochs + 1), desc="512 subcell adapter", unit="epoch"):
        result_train = _epoch(base, head, train_loader, optimizer, device)
        result_val = _epoch(base, head, val_loader, None, device)
        report["history"].append({"epoch": epoch, "train": result_train, "val": result_val})
        if result_val["conditional_loss"] < best - 1e-4:
            best, stale = result_val["conditional_loss"], 0
            temp = path.with_suffix(".tmp")
            torch.save({"state_dict": {k: v.detach().cpu() for k, v in head.state_dict().items()},
                        "signature": signature, "epochs_target": epochs, "parent_sha256": digest,
                        "width": saved["width"], "pilot": pilot}, temp)
            os.replace(temp, path)
        else:
            stale += 1
            if stale >= patience: break
    report["selected_epoch"] = min(report["history"], key=lambda row: row["val"]["conditional_loss"])["epoch"]
    atomic_json(models / "training.json", report)
    return report


def evaluate(pilot: bool = False, models: Path | None = None, artifacts: Path | None = None) -> dict:
    meta = read_json(ROOT64 / "meta.json")
    models = models or (MODELS / "pilot" if pilot else MODELS)
    artifacts = artifacts or (ARTIFACTS / "pilot" if pilot else ARTIFACTS)
    saved = torch.load(models / "best.pt", map_location="cpu", weights_only=False)
    base, parent_saved = _parent_model("cpu")
    digest = hashlib.sha256((MODELS64 / "best.pt").read_bytes()).hexdigest()
    if saved["parent_sha256"] != digest: raise ValueError("Frozen parent checkpoint changed")
    head = SubcellHead(saved["width"])
    head.load_state_dict(saved["state_dict"])
    head.eval()
    loader, ids = _loader(meta, "val", 32, pilot)
    train_ids = meta["splits"]["train"][:4] if pilot else meta["splits"]["train"]
    train_counts = Counter()
    for mid in tqdm(train_ids, desc="512 train prior", unit="game"):
        with np.load(ROOT64 / "labels" / f"{mid}.npz") as labels:
            train_counts.update(map(int, cell512(labels["xy"])))
    common = train_counts.most_common(1)[0][0]
    counts = {phase: {kind: Counter() for kind in ("observed", "predicted")} for phase in ("early", "middle", "late")}
    by_match = defaultdict(list)
    samples = model_hits = copy_hits = common_hits = parent_hits = oracle_hits = 0
    distance_sum = 0.0
    radius = {r: [0, 0] for r in (8, 16, 32, 64)}
    index = 0
    with torch.no_grad():
        for x, champion, region64, xy in tqdm(loader, desc="512 validation", unit="batch"):
            h, forecast = base.encode(x, champion)
            parent_logits = base.logits_from_encoded(h, forecast)
            best_parent = parent_logits.topk(16, dim=-1)
            local_logits = head(h, forecast, best_parent.indices)
            joint = F.log_softmax(best_parent.values, -1)[..., None] + F.log_softmax(local_logits, -1)
            winner = joint.flatten(1).argmax(-1)
            chosen_parent = best_parent.indices.gather(1, (winner // 64)[:, None]).squeeze(1)
            chosen_local = winner % 64
            predicted = combine(chosen_parent, chosen_local).numpy()
            true = cell512(xy).numpy()
            previous = cell512(x[:, -1, 17:19]).numpy()
            oracle_local = head(h, forecast, region64).argmax(-1).numpy()
            minute = x[:, -1, 0].numpy() * 50
            for j in range(len(x)):
                target = int(true[j]); guess = int(predicted[j]); old = int(previous[j])
                mid = loader.dataset.index[index + j][0]
                correct, copy, frequent = int(guess == target), int(old == target), int(common == target)
                by_match[mid].append((correct, copy, frequent))
                model_hits += correct; copy_hits += copy; common_hits += frequent
                parent_hits += int(chosen_parent[j] == region64[j])
                oracle_hits += int(oracle_local[j] == subcell(cell512(xy[j])).item())
                dist = math.hypot(guess % GRID - target % GRID, guess // GRID - target // GRID)
                old_dist = math.hypot(old % GRID - target % GRID, old // GRID - target // GRID)
                distance_sum += dist
                for r in radius:
                    radius[r][0] += dist <= r
                    radius[r][1] += old_dist <= r
                phase = "early" if minute[j] < 10 else "middle" if minute[j] < 20 else "late"
                counts[phase]["observed"][target] += 1
                counts[phase]["predicted"][guess] += 1
            index += len(x)
            samples += len(x)
    rng = np.random.default_rng(CONFIG.seed)
    groups = [np.asarray(by_match[mid]) for mid in ids]
    gains = []
    for _ in range(2000):
        rows = np.concatenate([groups[k] for k in rng.integers(0, len(groups), len(groups))])
        gains.append(100 * (rows[:, 0].mean() - max(rows[:, 1].mean(), rows[:, 2].mean())))
    report = {"schema_version": 1, "grid": GRID, "parent_grid": PARENT, "status": "development_validation_only",
              "parent_beam": 16, "matches": len(ids), "samples": samples,
              "model_top1": model_hits / samples, "copy_previous_top1": copy_hits / samples,
              "train_frequent_top1": common_hits / samples, "chosen_parent64_top1": parent_hits / samples,
              "oracle_parent_subcell_top1": oracle_hits / samples,
              "mean_distance_cells": distance_sum / samples,
              "within_radius_cells": {str(r): {"model": value[0] / samples, "copy_previous": value[1] / samples}
                                      for r, value in radius.items()},
              "gain_vs_best_baseline_bootstrap95_pp": np.quantile(gains, [.025, .975]).tolist(),
              "phases": {phase: {"samples": sum(counts[phase]["observed"].values()),
                                  "observed": [[k, v] for k, v in sorted(counts[phase]["observed"].items())],
                                  "predicted": [[k, v] for k, v in sorted(counts[phase]["predicted"].items())]}
                         for phase in counts},
              "parent_sha256": digest, "adapter_signature": saved["signature"],
              "note": "Frozen 64x64 parent plus learned 8x8 subcell head; beam-16 joint choice. This does not add subminute observations or prove Faker skill."}
    artifacts.mkdir(parents=True, exist_ok=True)
    atomic_json(artifacts / "evaluation_val.json", report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("train", "val"))
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--epochs", type=int, default=12)
    args = parser.parse_args()
    result = train(args.epochs, pilot=args.pilot) if args.stage == "train" else evaluate(args.pilot)
    print(json.dumps({k: v for k, v in result.items() if k not in ("history", "phases")}, indent=2))


if __name__ == "__main__": main()
