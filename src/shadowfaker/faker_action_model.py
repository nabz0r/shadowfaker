"""Multilabel next-ten-second Faker event predictor and train-only baselines."""
from __future__ import annotations

import argparse
import json
import random

import numpy as np
import torch
from torch import nn

from .config import CONFIG
from .event_clock import FEATURES
from .faker_actions import CLASSES, DATA, SCHEMA_VERSION
from .util import atomic_json, read_json

MODEL = CONFIG.models / "faker_actions_10s.pt"
PRIVATE = CONFIG.artifacts / "faker_actions_10s_validation.json"
PUBLIC = CONFIG.root / "docs" / "data" / "public_faker_actions_10s.json"


class ActionMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(len(FEATURES), 128), nn.GELU(),
                                 nn.Linear(128, 64), nn.GELU(),
                                 nn.Linear(64, len(CLASSES)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def _phase(x: np.ndarray) -> np.ndarray:
    minute = x[:, FEATURES.index("minute")] * 60
    return np.where(minute < 10, 0, np.where(minute < 20, 1, 2))


def _iter_batches(ids: list[str], batch: int, shuffle: bool, rng: random.Random):
    order_ids = list(ids)
    if shuffle:
        rng.shuffle(order_ids)
    for mid in order_ids:
        with np.load(DATA / f"{mid}.npz") as z:
            x, y = z["x"].astype(np.float32), z["y"].astype(np.float32)
        rows = list(range(len(y)))
        if shuffle:
            rng.shuffle(rows)
        for start in range(0, len(rows), batch):
            selection = rows[start:start + batch]
            yield mid, x[selection], y[selection]


def train_priors(ids: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Jeffreys-smoothed Bernoulli rates, estimated from train matches only."""
    total = np.full(len(CLASSES), .5, dtype=np.float64)
    count = 1
    phases = np.full((3, len(CLASSES)), .5, dtype=np.float64)
    phase_count = np.ones(3, dtype=np.float64)
    for mid in ids:
        with np.load(DATA / f"{mid}.npz") as z:
            x, y = z["x"], z["y"]
        total += y.sum(axis=0)
        count += len(y)
        for phase in range(3):
            subset = y[_phase(x) == phase]
            phases[phase] += subset.sum(axis=0)
            phase_count[phase] += len(subset)
    return total / count, phases / phase_count[:, None]


def average_precision(label: np.ndarray, probability: np.ndarray) -> float | None:
    """Average precision with equal scores treated as one threshold."""
    positive = int(label.sum())
    if not positive:
        return None
    order = np.argsort(-probability, kind="mergesort")
    ranked_y, ranked_p = label[order], probability[order]
    endpoints = np.r_[np.flatnonzero(np.diff(ranked_p) != 0), len(label) - 1]
    tp = np.cumsum(ranked_y)[endpoints]
    increments = np.diff(np.r_[0, tp])
    return float(np.sum((increments / positive) * (tp / (endpoints + 1))))


def metrics(label: np.ndarray, probability: np.ndarray) -> dict:
    p = np.clip(probability.astype(np.float64), 1e-7, 1 - 1e-7)
    y = label.astype(np.float64)
    nll = -(y * np.log(p) + (1 - y) * np.log1p(-p))
    brier = (p - y) ** 2
    classes = {}
    for c, name in enumerate(CLASSES):
        classes[name] = {"positives": int(y[:, c].sum()),
                         "prevalence": float(y[:, c].mean()),
                         "average_precision": average_precision(y[:, c], p[:, c]),
                         "nll": float(nll[:, c].mean()),
                         "brier": float(brier[:, c].mean())}
    aps = [row["average_precision"] for row in classes.values()
           if row["average_precision"] is not None]
    return {"windows": len(y), "nll": float(nll.mean()),
            "brier": float(brier.mean()), "macro_average_precision": float(np.mean(aps)),
            "per_class": classes}


def run(*, pilot: bool = False, epochs: int = 50, batch: int = 512) -> dict:
    if not 1 <= epochs <= 100 or batch < 16:
        raise ValueError("Invalid training parameters")
    generated = read_json(DATA / "meta.json")
    if generated.get("schema_version") != SCHEMA_VERSION or generated.get("pilot"):
        raise ValueError("Build the complete Faker action dataset first")
    split = read_json(CONFIG.processed / "meta.json")["splits"]
    train_ids, val_ids = list(split["train"]), list(split["val"])
    if pilot:
        train_ids, val_ids = train_ids[:3], val_ids[:2]
    if set(train_ids) & set(val_ids):
        raise AssertionError("Match leakage")
    if not all((DATA / f"{mid}.npz").exists() for mid in train_ids + val_ids):
        raise FileNotFoundError("Missing per-match action labels")
    torch.manual_seed(CONFIG.seed)
    np.random.seed(CONFIG.seed)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    rng = random.Random(CONFIG.seed)
    global_prior, phase_prior = train_priors(train_ids)
    model = ActionMLP()
    optimizer = torch.optim.AdamW(model.parameters(), lr=8e-4, weight_decay=1e-3)
    path = MODEL.with_name("faker_actions_10s_pilot.pt") if pilot else MODEL
    path.parent.mkdir(parents=True, exist_ok=True)
    best, best_epoch, stale, history = float("inf"), 0, 0, []
    for epoch in range(1, epochs + 1):
        model.train()
        train_sum = train_n = 0
        for _, x, y in _iter_batches(train_ids, batch, True, rng):
            optimizer.zero_grad(set_to_none=True)
            loss = nn.functional.binary_cross_entropy_with_logits(
                model(torch.from_numpy(x)), torch.from_numpy(y))
            loss.backward()
            optimizer.step()
            train_sum += float(loss.detach()) * len(y)
            train_n += len(y)
        model.eval()
        val_sum = val_n = 0
        with torch.no_grad():
            for _, x, y in _iter_batches(val_ids, batch, False, rng):
                loss = nn.functional.binary_cross_entropy_with_logits(
                    model(torch.from_numpy(x)), torch.from_numpy(y))
                val_sum += float(loss) * len(y)
                val_n += len(y)
        val_loss = val_sum / val_n
        history.append({"epoch": epoch, "train_nll": train_sum / train_n,
                        "validation_nll": val_loss})
        if val_loss < best - 1e-4:
            best, best_epoch, stale = val_loss, epoch, 0
            torch.save(model.state_dict(), path)
        else:
            stale += 1
            if stale >= 4:
                break
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    model.eval()
    ys, ps, global_ps, phase_ps, phase_bins, match_names = [], [], [], [], [], []
    with torch.no_grad():
        for mid, x, y in _iter_batches(val_ids, batch, False, rng):
            ys.append(y)
            ps.append(torch.sigmoid(model(torch.from_numpy(x))).numpy())
            global_ps.append(np.broadcast_to(global_prior, y.shape))
            phase = _phase(x)
            phase_bins.append(phase)
            phase_ps.append(phase_prior[phase])
            match_names.extend([mid] * len(y))
    label, prob = np.concatenate(ys), np.concatenate(ps)
    constant, phased = np.concatenate(global_ps), np.concatenate(phase_ps)
    phase_bin = np.concatenate(phase_bins)
    scores = {"model": metrics(label, prob),
              "global_train_frequency": metrics(label, constant),
              "phase_train_frequency": metrics(label, phased)}
    by_phase = {}
    for index, name in enumerate(("early", "middle", "late")):
        mask = phase_bin == index
        by_phase[name] = {"model": metrics(label[mask], prob[mask]),
                          "phase_train_frequency": metrics(label[mask], phased[mask])}
    # Bootstrap whole matches; overlapping windows are not independent trials.
    per_match = []
    match_names = np.asarray(match_names)
    for mid in val_ids:
        mask = match_names == mid
        y = label[mask]
        m = np.clip(prob[mask], 1e-7, 1 - 1e-7)
        p = np.clip(phased[mask], 1e-7, 1 - 1e-7)
        model_sum = float(-(y*np.log(m) + (1-y)*np.log1p(-m)).sum())
        phase_sum = float(-(y*np.log(p) + (1-y)*np.log1p(-p)).sum())
        per_match.append({"match_id": mid, "windows": len(y),
                          "model_nll_sum": model_sum, "phase_nll_sum": phase_sum})
    matrix = np.asarray([[r["windows"]*len(CLASSES), r["model_nll_sum"],
                          r["phase_nll_sum"]] for r in per_match])
    rng_boot = np.random.default_rng(CONFIG.seed)
    picks = rng_boot.integers(0, len(per_match), size=(2000, len(per_match)))
    drawn = matrix[picks].sum(axis=1)
    gain = (drawn[:, 2] - drawn[:, 1]) / drawn[:, 0]
    report = {"schema_version": 1, "pilot": pilot,
              "target": "seven Faker-attributed outcomes in next ten seconds",
              "train_matches": len(train_ids), "validation_matches": len(val_ids),
              "train_windows": train_n, "validation_windows": len(label),
              "parameters": sum(p.numel() for p in model.parameters()),
              "best_epoch": best_epoch, "history": history, "scores": scores,
              "by_phase": by_phase,
              "phase_nll_gain_model_vs_baseline": scores["phase_train_frequency"]["nll"] - scores["model"]["nll"],
              "phase_nll_gain_ci95_match_bootstrap": np.quantile(gain, [.025, .975]).tolist(),
              "selection": "historical validation; old test and future lockbox untouched",
              "limits": "event occurrence, not player position, click, vision, intention or action value",
              "per_match": per_match}
    private = PRIVATE.with_name("faker_actions_10s_pilot.json") if pilot else PRIVATE
    atomic_json(private, report)
    if not pilot:
        aggregate = {k: v for k, v in report.items() if k not in ("history", "per_match")}
        atomic_json(PUBLIC, aggregate)
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pilot", action="store_true")
    p.add_argument("--epochs", type=int, default=50)
    args = p.parse_args()
    report = run(pilot=args.pilot, epochs=args.epochs)
    print(json.dumps({k: v for k, v in report.items() if k not in ("history", "per_match")}, indent=2))


if __name__ == "__main__":
    main()
