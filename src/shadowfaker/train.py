import argparse
import hashlib
import json
import logging
import os
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


def loss_parts(outputs, targets, region_weights, region_balance: float = .3,
               coarse_loss_weight: float = 0.0):
    region, item, skill, value = outputs
    _, _, y_region, y_item, y_skill, y_win = targets
    # Keep a class-balanced signal without letting rare regions dominate top-1 accuracy.
    region_loss = (region_balance * nn.functional.cross_entropy(region, y_region, weight=region_weights)
                   + (1 - region_balance) * nn.functional.cross_entropy(region, y_region))
    if coarse_loss_weight:
        # Sum probabilities of the four fine cells in each 8x8 macro cell.
        # The target comes from Faker's next position, like the 16x16 target.
        coarse_logits = region.reshape(-1, 8, 2, 8, 2).logsumexp(-1).logsumexp(2).reshape(-1, 64)
        coarse_target = (y_region // 16 // 2) * 8 + (y_region % 16 // 2)
        region_loss = region_loss + coarse_loss_weight * nn.functional.cross_entropy(coarse_logits, coarse_target)
    item_weight = torch.ones(item.shape[-1], device=item.device)
    item_weight[0] = .25
    skill_weight = torch.tensor([.25, 1, 1, 1, 1], device=skill.device)
    item_loss = nn.functional.cross_entropy(item, y_item, weight=item_weight)
    skill_loss = nn.functional.cross_entropy(skill, y_skill, weight=skill_weight)
    value_loss = nn.functional.binary_cross_entropy_with_logits(value, y_win)
    return region_loss, item_loss, skill_loss, value_loss


def train_epoch(model, loader, optimizer, device, weights, train=True, region_balance: float = .3,
                coarse_loss_weight: float = 0.0):
    model.train(train)
    totals = np.zeros(6, dtype=float)
    for batch in loader:
        batch = [tensor.to(device) for tensor in batch]
        with torch.set_grad_enabled(train):
            outputs = model(batch[0], batch[1])
            r, i, s, v = loss_parts(outputs, batch, weights, region_balance, coarse_loss_weight)
            loss = r + .3 * i + .2 * s + .1 * v
            if train:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
        count = len(batch[0])
        totals += np.array([float(loss.detach()), float(r.detach()), float(i.detach()), float(s.detach()), float(v.detach()),
                            float((outputs[0].argmax(-1) == batch[2]).float().mean().detach())]) * count
    return (totals / max(1, len(loader.dataset))).tolist()


def benchmark(meta: dict, processed: Path, batch_size: int = 64, view: str = "proxy",
              width: int = 128, layers: int = 2, spatial_head: bool = False,
              coarse_loss_weight: float = 0.0) -> dict:
    ds = MatchDataset(processed, meta, "train", view=view)
    sample = Subset(ds, list(range(min(len(ds), 256))))
    candidates = ["cpu"] + (["mps"] if torch.backends.mps.is_available() else [])
    measured = {}
    for device in candidates:
        seed_all(CONFIG.seed)
        model = MacroTransformer(meta["feature_dim"], len(meta["item_vocab"]) + 2,
                                 width=width, layers=layers, spatial_head=spatial_head).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
        weights = torch.tensor(meta["region_weights"], dtype=torch.float32, device=device)
        loader = DataLoader(sample, batch_size=batch_size, shuffle=False)
        started = time.perf_counter()
        train_epoch(model, loader, optimizer, device, weights, coarse_loss_weight=coarse_loss_weight)
        if device == "mps":
            torch.mps.synchronize()
        measured[device] = round(time.perf_counter() - started, 3)
        LOG.info("One mini-epoch benchmark %s: %.3f seconds", device, measured[device])
    return measured


def train(processed: Path = CONFIG.processed, models: Path = CONFIG.models, runs: Path = CONFIG.runs,
          epochs: int = 25, batch_size: int = 64, patience: int = 5,
          lr: float = 3e-4, width: int = 128, layers: int = 2, force: bool = False,
          view: str = "proxy", region_balance: float = .3, spatial_head: bool = False,
          coarse_loss_weight: float = 0.0) -> dict:
    meta = read_json(processed / "meta.json")
    if not meta:
        raise FileNotFoundError("Processed meta.json missing; run parse first")
    seed_all(CONFIG.seed)
    if not 0 <= region_balance <= 1:
        raise ValueError("region_balance must be between 0 and 1")
    if not 0 <= coarse_loss_weight <= 2:
        raise ValueError("coarse_loss_weight must be between 0 and 2")
    models.mkdir(parents=True, exist_ok=True)
    runs.mkdir(parents=True, exist_ok=True)
    sig = signature(meta)
    checkpoint = models / "best.pt"
    if checkpoint.exists():
        existing = torch.load(checkpoint, map_location="cpu", weights_only=False)
        existing_params = {"spatial_head": False, "coarse_loss_weight": 0.0, **existing.get("hyperparams", {})}
        if (not force and existing.get("signature") == sig and existing.get("epochs_target", 0) >= epochs
                and existing_params == {"lr": lr, "width": width, "layers": layers, "view": view,
                                        "region_balance": region_balance, "spatial_head": spatial_head,
                                        "coarse_loss_weight": coarse_loss_weight}):
            LOG.info("Reusing checkpoint for matching dataset signature")
            return existing["training"]
    timings = benchmark(meta, processed, batch_size, view, width, layers, spatial_head, coarse_loss_weight)
    device = min(timings, key=timings.get)
    seed_all(CONFIG.seed)
    model = MacroTransformer(meta["feature_dim"], len(meta["item_vocab"]) + 2, width=width, layers=layers,
                             spatial_head=spatial_head).to(device)
    if parameter_count(model) >= 5_000_000:
        raise AssertionError("Model exceeds 5M parameters")
    training = {"device": device, "benchmark_seconds": timings, "parameters": parameter_count(model),
                "seed": CONFIG.seed, "signature": sig, "hyperparams": {"lr": lr, "width": width, "layers": layers,
                                                                          "view": view, "region_balance": region_balance,
                                                                          "spatial_head": spatial_head,
                                                                          "coarse_loss_weight": coarse_loss_weight}, "history": []}
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=.01)
    weights = torch.tensor(meta["region_weights"], dtype=torch.float32, device=device)
    train_loader = DataLoader(MatchDataset(processed, meta, "train", view=view), batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(MatchDataset(processed, meta, "val", view=view), batch_size=batch_size, shuffle=False, num_workers=0)
    writer = SummaryWriter(str(runs / f"{sig[:12]}-{view}-{width}-{lr}-balance{region_balance}-spatial{int(spatial_head)}-coarse{coarse_loss_weight}"))
    best, stale = float("inf"), 0
    for epoch in tqdm(range(1, epochs + 1), desc="training", unit="epoch"):
        tr = train_epoch(model, train_loader, optimizer, device, weights, region_balance=region_balance,
                         coarse_loss_weight=coarse_loss_weight)
        va = train_epoch(model, val_loader, optimizer, device, weights, train=False, region_balance=region_balance,
                         coarse_loss_weight=coarse_loss_weight)
        row = {"epoch": epoch, "train_loss": tr[0], "val_loss": va[0], "train_region_acc": tr[5], "val_region_acc": va[5],
               "train_value_loss": tr[4], "val_value_loss": va[4]}
        training["history"].append(row)
        for k, value in row.items():
            if k != "epoch":
                writer.add_scalar(k, value, epoch)
        LOG.info("Epoch %d train %.3f val %.3f region %.3f", epoch, tr[0], va[0], va[5])
        if va[0] < best - 1e-4:
            best, stale = va[0], 0
            state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            temp_checkpoint = checkpoint.with_suffix(".tmp")
            torch.save({"state_dict": state, "signature": sig, "epochs_target": epochs,
                        "hyperparams": {"lr": lr, "width": width, "layers": layers, "view": view,
                                         "region_balance": region_balance, "spatial_head": spatial_head,
                                         "coarse_loss_weight": coarse_loss_weight},
                        "training": training.copy(), "config": {"feature_dim": meta["feature_dim"], "items": len(meta["item_vocab"]) + 2,
                                                             "width": width, "layers": layers, "view": view,
                                                             "spatial_head": spatial_head}}, temp_checkpoint)
            os.replace(temp_checkpoint, checkpoint)
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
    temp_checkpoint = checkpoint.with_suffix(".tmp")
    torch.save(saved, temp_checkpoint)
    os.replace(temp_checkpoint, checkpoint)
    return training


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--view", choices=["proxy", "oracle"], default="proxy")
    parser.add_argument("--region-balance", type=float, default=.3)
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--spatial-head", action="store_true")
    parser.add_argument("--coarse-loss-weight", type=float, default=0.0)
    parser.add_argument("--models-dir", type=Path, default=CONFIG.models)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    print(train(models=args.models_dir, epochs=args.epochs, batch_size=args.batch_size, view=args.view,
                region_balance=args.region_balance, width=args.width, layers=args.layers, lr=args.lr,
                spatial_head=args.spatial_head, coarse_loss_weight=args.coarse_loss_weight))


if __name__ == "__main__":
    main()
