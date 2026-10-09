import argparse
import hashlib
import json
import logging
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from .config import CONFIG
from .dataset import MatchDataset
from .model import MacroTransformer, parameter_count
from .util import atomic_json, read_json, seed_all

LOG = logging.getLogger(__name__)


def signature(meta: dict) -> str:
    return hashlib.sha256(json.dumps({"splits": meta["splits"], "item_vocab": meta["item_vocab"], "schema": meta["schema_version"]}, sort_keys=True).encode()).hexdigest()


def loss_parts(outputs, targets, region_weights):
    region, item, skill = outputs
    _, _, y_region, y_item, y_skill = targets
    region_loss = nn.functional.cross_entropy(region, y_region, weight=region_weights)
    item_weight = torch.ones(item.shape[-1], device=item.device)
    item_weight[0] = .25
    skill_weight = torch.tensor([.25, 1, 1, 1, 1], device=skill.device)
    item_loss = nn.functional.cross_entropy(item, y_item, weight=item_weight)
    skill_loss = nn.functional.cross_entropy(skill, y_skill, weight=skill_weight)
    return region_loss, item_loss, skill_loss


def train_epoch(model, loader, optimizer, device, weights, train=True):
    model.train(train)
    totals = np.zeros(5, dtype=float)
    for batch in loader:
        batch = [tensor.to(device) for tensor in batch]
        with torch.set_grad_enabled(train):
            outputs = model(batch[0], batch[1])
            r, i, s = loss_parts(outputs, batch, weights)
            loss = r + .3 * i + .2 * s
            if train:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
        count = len(batch[0])
        totals += np.array([float(loss.detach()), float(r.detach()), float(i.detach()), float(s.detach()),
                            float((outputs[0].argmax(-1) == batch[2]).float().mean().detach())]) * count
    return (totals / max(1, len(loader.dataset))).tolist()


def benchmark(meta: dict, processed: Path, batch_size: int = 64) -> dict:
    ds = MatchDataset(processed, meta, "train")
    sample = Subset(ds, list(range(min(len(ds), 256))))
    candidates = ["cpu"] + (["mps"] if torch.backends.mps.is_available() else [])
    measured = {}
    for device in candidates:
        seed_all(CONFIG.seed)
        model = MacroTransformer(meta["feature_dim"], len(meta["item_vocab"]) + 2).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
        weights = torch.tensor(meta["region_weights"], dtype=torch.float32, device=device)
        loader = DataLoader(sample, batch_size=batch_size, shuffle=False)
        started = time.perf_counter()
        train_epoch(model, loader, optimizer, device, weights)
        if device == "mps":
            torch.mps.synchronize()
        measured[device] = round(time.perf_counter() - started, 3)
        LOG.info("One mini-epoch benchmark %s: %.3f seconds", device, measured[device])
    return measured


def train(processed: Path = CONFIG.processed, models: Path = CONFIG.models, runs: Path = CONFIG.runs,
          epochs: int = 25, batch_size: int = 64, patience: int = 5,
          lr: float = 3e-4, width: int = 128, layers: int = 2, force: bool = False) -> dict:
    meta = read_json(processed / "meta.json")
    if not meta:
        raise FileNotFoundError("Processed meta.json missing; run parse first")
    seed_all(CONFIG.seed)
    models.mkdir(parents=True, exist_ok=True)
    runs.mkdir(parents=True, exist_ok=True)
    sig = signature(meta)
    checkpoint = models / "best.pt"
    if checkpoint.exists():
        existing = torch.load(checkpoint, map_location="cpu", weights_only=False)
        if (not force and existing.get("signature") == sig and existing.get("epochs_target", 0) >= epochs
                and existing.get("hyperparams") == {"lr": lr, "width": width, "layers": layers}):
            LOG.info("Reusing checkpoint for matching dataset signature")
            return existing["training"]
    timings = benchmark(meta, processed, batch_size)
    device = min(timings, key=timings.get)
    seed_all(CONFIG.seed)
    model = MacroTransformer(meta["feature_dim"], len(meta["item_vocab"]) + 2, width=width, layers=layers).to(device)
    if parameter_count(model) >= 5_000_000:
        raise AssertionError("Model exceeds 5M parameters")
    training = {"device": device, "benchmark_seconds": timings, "parameters": parameter_count(model),
                "seed": CONFIG.seed, "signature": sig, "hyperparams": {"lr": lr, "width": width, "layers": layers}, "history": []}
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=.01)
    weights = torch.tensor(meta["region_weights"], dtype=torch.float32, device=device)
    train_loader = DataLoader(MatchDataset(processed, meta, "train"), batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(MatchDataset(processed, meta, "val"), batch_size=batch_size, shuffle=False, num_workers=0)
    writer = SummaryWriter(str(runs / sig[:12]))
    best, stale = float("inf"), 0
    for epoch in tqdm(range(1, epochs + 1), desc="training", unit="epoch"):
        tr = train_epoch(model, train_loader, optimizer, device, weights)
        va = train_epoch(model, val_loader, optimizer, device, weights, train=False)
        row = {"epoch": epoch, "train_loss": tr[0], "val_loss": va[0], "train_region_acc": tr[4], "val_region_acc": va[4]}
        training["history"].append(row)
        for k, value in row.items():
            if k != "epoch":
                writer.add_scalar(k, value, epoch)
        LOG.info("Epoch %d train %.3f val %.3f region %.3f", epoch, tr[0], va[0], va[4])
        if va[0] < best - 1e-4:
            best, stale = va[0], 0
            state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            torch.save({"state_dict": state, "signature": sig, "epochs_target": epochs,
                        "hyperparams": {"lr": lr, "width": width, "layers": layers},
                        "training": training.copy(), "config": {"feature_dim": meta["feature_dim"], "items": len(meta["item_vocab"]) + 2,
                                                             "width": width, "layers": layers}}, checkpoint)
        else:
            stale += 1
            if stale >= patience:
                break
    writer.close()
    training["best_val_loss"] = best
    training["epochs_ran"] = len(training["history"])
    atomic_json(models / "training.json", training)
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    saved["training"] = training
    torch.save(saved, checkpoint)
    return training


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    print(train(epochs=args.epochs, batch_size=args.batch_size))


if __name__ == "__main__":
    main()
