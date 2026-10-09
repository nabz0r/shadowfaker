"""Separate 64x64 experiment; the frozen 16x16 checkpoint is never modified."""
import argparse
from collections import Counter, OrderedDict, defaultdict
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import Dataset, DataLoader, Subset
from tqdm import tqdm

from .config import CONFIG
from .features import extract_match, position, FEATURE_DIM, FEATURE_NAMES, _save_npz
from .util import atomic_json, read_json, seed_all

LOG = logging.getLogger(__name__)
GRID = 64
ROOT64 = CONFIG.root / "data" / "processed64"
MODELS64 = CONFIG.root / "models" / "grid64"
ARTIFACTS64 = CONFIG.root / "artifacts" / "grid64"


def cell(pos: np.ndarray) -> int:
    return int(pos[1] * GRID) * GRID + int(pos[0] * GRID)


def _target_labels(match: dict, timeline: dict, puuid: str) -> dict:
    players = (match.get("info") or {}).get("participants") or []
    pid = next((int(p.get("participantId") or j + 1) for j, p in enumerate(players) if p.get("puuid") == puuid), None)
    if pid is None:
        raise ValueError("PUUID absent from match")
    frames = (timeline.get("info") or {}).get("frames") or []
    region, prev, xy, minutes = [], [], [], []
    last = None
    for i, frame in enumerate(frames[:-1]):
        pf = frame.get("participantFrames") or {}
        own = pf.get(str(pid)) or pf.get(pid) or {}
        current = position(own)
        if current is not None:
            last = current
        future = (frames[i + 1].get("participantFrames") or {})
        nxt = position(future.get(str(pid)) or future.get(pid) or {})
        if nxt is None:
            continue
        region.append(cell(nxt))
        prev.append(cell(last) if last is not None else -1)
        xy.append(nxt)
        minutes.append(float(frame.get("timestamp", i * 60000)) / 60000)
    return {"region": np.asarray(region, np.int64), "previous": np.asarray(prev, np.int64),
            "xy": np.asarray(xy, np.float32), "minute": np.asarray(minutes, np.float32)}


def prepare(limit: int | None = None, processed: Path = ROOT64) -> dict:
    ranked = read_json(CONFIG.raw / "manifest.json")
    old = read_json(CONFIG.processed / "meta.json")
    expanded = read_json(CONFIG.raw / "expanded_summary.json", {})
    if not ranked or not old:
        raise FileNotFoundError("Ranked raw and processed metadata required")
    puuid = ranked["account"]["puuid"]
    ranked_ids = [mid for mid in ranked["order"] if mid in old["counts"]]
    extra = expanded.get("extra_ids", [])
    ids = ranked_ids + [mid for mid in extra if mid not in ranked_ids]
    if limit is not None:
        ids = ids[:limit]
    counts, sources, errors = {}, {}, {}
    for mid in tqdm(ids, desc="prepare 64x64", unit="game"):
        try:
            match = json.loads((CONFIG.raw / "matches" / f"{mid}.json").read_text())
            timeline = json.loads((CONFIG.raw / "timelines" / f"{mid}.json").read_text())
            source = CONFIG.processed / "matches" / f"{mid}.npz"
            if not source.exists():
                source = processed / "matches" / f"{mid}.npz"
                if not source.exists():
                    _save_npz(source, extract_match(match, timeline, puuid, CONFIG.window))
            label_path = processed / "labels" / f"{mid}.npz"
            if not label_path.exists():
                _save_npz(label_path, _target_labels(match, timeline, puuid))
            with np.load(source) as z, np.load(label_path) as labels:
                if len(z["x"]) != len(labels["region"]) or not np.allclose(z["minute"], labels["minute"], atol=.001):
                    raise ValueError("64x64 labels do not align with causal examples")
                counts[mid] = len(labels["region"])
            info = match.get("info") or {}
            sources[mid] = {"queue": int(info.get("queueId") or -1), "map_id": int(info.get("mapId") or -1),
                            "domain": "ranked_solo" if mid in ranked_ids else "other_summoners_rift"}
        except Exception as exc:
            LOG.exception("64x64 prepare failed for %s", mid)
            errors[mid] = str(exc)
    if len(counts) < 3:
        raise ValueError("Need three games for 64x64 split")
    splits = {k: [mid for mid in old["splits"][k] if mid in counts] for k in ("train", "val", "test")}
    splits["train"].extend(mid for mid in extra if mid in counts and mid not in ranked_ids)
    if limit is not None and min(map(len, splits.values())) == 0:
        # Five-game smoke test only; no persisted split override of the full run.
        ordered = list(counts)
        splits = {"train": ordered[2:], "val": [ordered[1]], "test": [ordered[0]]}
    old_train = set(old["splits"]["train"])
    item_vocab = old["item_vocab"]
    train_counts = Counter()
    for mid in splits["train"]:
        with np.load(processed / "labels" / f"{mid}.npz") as z:
            train_counts.update(map(int, z["region"]))
    freq = np.array([train_counts.get(i, 0) for i in range(GRID**2)], dtype=np.float64)
    weights = np.sqrt((freq.sum() + GRID**2) / (freq + 1))
    weights = np.clip(weights / np.mean(weights[freq > 0]), .3, 5).tolist()
    meta = {"schema_version": 1, "grid": GRID, "seed": CONFIG.seed, "window": CONFIG.window,
            "feature_dim": FEATURE_DIM, "splits": splits, "counts": counts, "sources": sources,
            "item_vocab": item_vocab, "region_weights": weights, "errors": errors,
            "observations": sum(counts.values()), "old_ranked_train_matches": len(old_train & set(splits["train"])),
            "extra_training_matches": sum(sources[mid]["domain"] != "ranked_solo" for mid in splits["train"]),
            "description": "Legacy 16x16 ranked val/test matches preserved; extra same-PUUID Summoner's Rift games enter training only."}
    atomic_json(processed / "meta.json", meta)
    return meta


class Grid64Dataset(Dataset):
    def __init__(self, meta: dict, split: str, processed: Path = ROOT64, max_cached: int = 2):
        self.meta, self.processed = meta, processed
        self.index = [(mid, i) for mid in meta["splits"][split] for i in range(meta["counts"][mid])]
        self.cache = OrderedDict()
        self.max_cached = max_cached

    def __len__(self): return len(self.index)

    def __getitem__(self, j):
        mid, i = self.index[j]
        if mid not in self.cache:
            source = CONFIG.processed / "matches" / f"{mid}.npz"
            if not source.exists(): source = self.processed / "matches" / f"{mid}.npz"
            with np.load(source) as z, np.load(self.processed / "labels" / f"{mid}.npz") as labels:
                self.cache[mid] = {"x": z["x"], "champion": z["champion"],
                                   "region": labels["region"], "previous": labels["previous"],
                                   "xy": labels["xy"]}
            if len(self.cache) > self.max_cached: self.cache.popitem(last=False)
        self.cache.move_to_end(mid)
        a = self.cache[mid]
        return (torch.from_numpy(a["x"][i].copy()), torch.tensor(int(a["champion"][i])),
                torch.tensor(int(a["region"][i])), torch.from_numpy(a["xy"][i].copy()))


class Grid64Transformer(nn.Module):
    def __init__(self, width: int = 128, layers: int = 2):
        super().__init__()
        self.numeric = nn.Linear(FEATURE_DIM, width)
        self.champion = nn.Embedding(1000, width)
        self.time = nn.Embedding(64, width)
        block = nn.TransformerEncoderLayer(width, 4, width * 3, dropout=.1, batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(block, layers)
        self.norm = nn.LayerNorm(width)
        self.region = nn.Linear(width, GRID**2)
        self.xy = nn.Linear(width, 2)
        self.distance_scale = nn.Parameter(torch.tensor(1.0))
        yy, xx = torch.meshgrid(torch.arange(GRID), torch.arange(GRID), indexing="ij")
        self.register_buffer("centers", torch.stack(((xx.flatten() + .5) / GRID, (yy.flatten() + .5) / GRID), dim=1).float())

    def forward(self, x, champion):
        h = self.numeric(x) + self.champion(champion.clamp(0, 999))[:, None, :]
        h = h + self.time(torch.arange(x.shape[1], device=x.device))[None]
        h = self.norm(self.encoder(h)[:, -1])
        next_xy = (x[:, -1, 17:19] + .35 * torch.tanh(self.xy(h))).clamp(0, 1)
        dist = ((next_xy[:, None] - self.centers[None]) ** 2).sum(-1)
        return self.region(h) - F.softplus(self.distance_scale) * 18 * dist, next_xy


def coarse_logits(logits: torch.Tensor, grid: int = 16) -> torch.Tensor:
    block = GRID // grid
    return logits.reshape(-1, grid, block, grid, block).logsumexp(-1).logsumexp(2).reshape(-1, grid * grid)


def coarse_labels(labels: torch.Tensor | np.ndarray, grid: int = 16):
    block = GRID // grid
    return (labels // GRID // block) * grid + (labels % GRID // block)


def _epoch(model, loader, optimizer, device, weights, train: bool):
    model.train(train)
    loss_total = acc_total = count = 0
    for x, champion, region, target_xy in loader:
        x, champion, region, target_xy = (v.to(device) for v in (x, champion, region, target_xy))
        with torch.set_grad_enabled(train):
            logits, forecast_xy = model(x, champion)
            fine = .8 * F.cross_entropy(logits, region) + .2 * F.cross_entropy(logits, region, weight=weights)
            coarse = F.cross_entropy(coarse_logits(logits), coarse_labels(region))
            loss = fine + .65 * coarse + .15 * F.smooth_l1_loss(forecast_xy, target_xy)
            if train:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1)
                optimizer.step()
        batch = len(region)
        loss_total += float(loss.detach()) * batch
        acc_total += int((logits.argmax(-1) == region).sum())
        count += batch
    return {"loss": loss_total / count, "top1": acc_total / count}


def train(meta: dict | None = None, processed: Path = ROOT64, models: Path = MODELS64,
          epochs: int = 25, batch_size: int = 64, patience: int = 5, lr: float = 3e-4,
          width: int = 128, layers: int = 2) -> dict:
    meta = meta or read_json(processed / "meta.json")
    seed_all(CONFIG.seed)
    signature = hashlib.sha256(json.dumps({"splits": meta["splits"], "counts": meta["counts"],
                                           "grid": GRID, "schema": meta["schema_version"]}, sort_keys=True).encode()).hexdigest()
    models.mkdir(parents=True, exist_ok=True)
    checkpoint = models / "best.pt"
    if checkpoint.exists():
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        if saved.get("signature") == signature and saved.get("epochs_target", 0) >= epochs:
            return read_json(models / "training.json")
    ds_train, ds_val = Grid64Dataset(meta, "train", processed), Grid64Dataset(meta, "val", processed)
    weights = torch.tensor(meta["region_weights"], dtype=torch.float32)
    times = {}
    for device in (["cpu", "mps"] if torch.backends.mps.is_available() else ["cpu"]):
        seed_all(CONFIG.seed)
        model = Grid64Transformer(width, layers).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=lr)
        loader = DataLoader(Subset(ds_train, range(min(128, len(ds_train)))), batch_size=batch_size)
        start = time.perf_counter()
        _epoch(model, loader, opt, device, weights.to(device), True)
        if device == "mps": torch.mps.synchronize()
        times[device] = round(time.perf_counter() - start, 3)
    device = min(times, key=times.get)
    seed_all(CONFIG.seed)
    model = Grid64Transformer(width, layers).to(device)
    parameters = sum(p.numel() for p in model.parameters())
    if parameters >= 5_000_000: raise ValueError("64x64 model exceeds 5M parameters")
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=.01)
    train_loader = DataLoader(ds_train, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(ds_val, batch_size=batch_size)
    weights = weights.to(device)
    report = {"grid": GRID, "parameters": parameters, "device": device, "benchmark_seconds": times,
              "signature": signature, "seed": CONFIG.seed, "train_matches": len(meta["splits"]["train"]),
              "val_matches": len(meta["splits"]["val"]), "history": [],
              "hyperparams": {"epochs": epochs, "lr": lr, "width": width, "layers": layers}}
    best, stale = float("inf"), 0
    for epoch in tqdm(range(1, epochs + 1), desc="train grid64", unit="epoch"):
        tr = _epoch(model, train_loader, optimizer, device, weights, True)
        va = _epoch(model, val_loader, optimizer, device, weights, False)
        report["history"].append({"epoch": epoch, "train": tr, "val": va})
        if va["loss"] < best - 1e-4:
            best, stale = va["loss"], 0
            temp = checkpoint.with_suffix(".tmp")
            torch.save({"state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                        "signature": signature, "epochs_target": epochs, "width": width, "layers": layers}, temp)
            os.replace(temp, checkpoint)
        else:
            stale += 1
            if stale >= patience: break
    report["epochs_ran"] = len(report["history"])
    report["best_val_loss"] = best
    atomic_json(models / "training.json", report)
    return report


def evaluate(split: str = "val", processed: Path = ROOT64, models: Path = MODELS64,
             artifacts: Path = ARTIFACTS64) -> dict:
    meta = read_json(processed / "meta.json")
    saved = torch.load(models / "best.pt", map_location="cpu", weights_only=False)
    model = Grid64Transformer(saved["width"], saved["layers"])
    model.load_state_dict(saved["state_dict"])
    model.eval()
    ds = Grid64Dataset(meta, split, processed)
    train_counts, prior_counts = Counter(), defaultdict(Counter)
    role_idx = FEATURE_NAMES.index("faker_role")
    for mid in meta["splits"]["train"]:
        source = CONFIG.processed / "matches" / f"{mid}.npz"
        if not source.exists(): source = processed / "matches" / f"{mid}.npz"
        with np.load(source) as z, np.load(processed / "labels" / f"{mid}.npz") as label:
            x = z["x"][:, -1]
            for region, role, minute in zip(label["region"], x[:, role_idx], x[:, 0] * 50):
                region = int(region)
                train_counts[region] += 1
                prior_counts[(round(float(role) * 5), int(minute >= 10) + int(minute >= 20))][region] += 1
    common = train_counts.most_common(1)[0][0]
    true, guess, prev, priors, mids, minutes, coarse_guess, top5 = [], [], [], [], [], [], [], []
    top25, top100, raw_set90_hit, raw_set90_size, true_probability, confidence = [], [], [], [], [], []
    calibration_scores, prior_mass_rows = [], []
    actual_density = np.zeros(GRID**2, dtype=np.int64)
    predicted_density = np.zeros(GRID**2, dtype=np.int64)
    with torch.no_grad():
        for x, champion, region, _ in tqdm(DataLoader(ds, batch_size=128), desc=f"evaluate grid64 {split}"):
            logits, _ = model(x, champion)
            guess.extend(logits.argmax(-1).tolist())
            coarse_guess.extend(coarse_logits(logits).argmax(-1).tolist())
            top5.extend((logits.topk(5, -1).indices == region[:, None]).any(-1).tolist())
            best100 = logits.topk(100, -1).indices
            top25.extend((best100[:, :25] == region[:, None]).any(-1).tolist())
            top100.extend((best100 == region[:, None]).any(-1).tolist())
            probs = logits.softmax(-1)
            ordered, order = probs.sort(dim=-1, descending=True)
            prior_mass = ordered.cumsum(-1) - ordered
            sizes = (prior_mass < .9).sum(-1)
            ranks = (order == region[:, None]).long().argmax(-1)
            raw_set90_hit.extend((ranks < sizes).tolist())
            raw_set90_size.extend(sizes.tolist())
            calibration_scores.extend(prior_mass.gather(1, ranks[:, None]).squeeze(-1).tolist())
            prior_mass_rows.append(prior_mass.numpy())
            true_probability.extend(probs.gather(1, region[:, None]).squeeze(-1).tolist())
            confidence.extend(probs.max(-1).values.tolist())
            true.extend(region.tolist())
    for mid in meta["splits"][split]:
        source = CONFIG.processed / "matches" / f"{mid}.npz"
        if not source.exists(): source = processed / "matches" / f"{mid}.npz"
        with np.load(source) as z, np.load(processed / "labels" / f"{mid}.npz") as label:
            prev.extend(label["previous"].tolist())
            minutes.extend(label["minute"].tolist())
            for region, role, minute in zip(label["region"], z["x"][:, -1, role_idx], z["x"][:, -1, 0] * 50):
                key = (round(float(role) * 5), int(minute >= 10) + int(minute >= 20))
                priors.append(prior_counts[key].most_common(1)[0][0] if prior_counts[key] else common)
            mids.extend([mid] * len(label["region"]))
    t, p, prev, prior = map(np.asarray, (true, guess, prev, priors))
    minutes = np.asarray(minutes)
    if len(minutes) != len(t):
        raise ValueError("Evaluation minutes and predictions are misaligned")
    def distance(a, b):
        a, b = np.asarray(a), np.asarray(b)
        return np.hypot(a % GRID - b % GRID, a // GRID - b // GRID)
    displacement = distance(p, t)
    previous_distance = distance(prev, t)
    confidence = np.asarray(confidence)
    accurate = p == t
    calibration_file = models / "calibration.json"
    if split == "val":
        # Held-out validation chooses one global rank-mass threshold. Match-level
        # correlation means the usual exchangeable-row guarantee does not apply.
        ordinal = min(len(calibration_scores) - 1, math.ceil((len(calibration_scores) + 1) * .9) - 1)
        threshold = float(np.sort(np.asarray(calibration_scores))[ordinal])
        atomic_json(calibration_file, {"target_coverage": .9, "rank_mass_threshold": threshold,
                                       "calibration_samples": len(calibration_scores),
                                       "calibration_matches": len(meta["splits"]["val"]),
                                       "checkpoint_signature": saved["signature"]})
    else:
        calibration = read_json(calibration_file)
        if not calibration or calibration.get("checkpoint_signature") != saved["signature"]:
            raise ValueError("Run 64x64 validation calibration for this checkpoint before test")
        threshold = float(calibration["rank_mass_threshold"])
    set90_hit = np.asarray(calibration_scores) <= threshold
    set90_size = [int(np.count_nonzero(row <= threshold)) for batch in prior_mass_rows for row in batch]
    calibration_bins = []
    for lo, hi in zip(np.linspace(0, 1, 11)[:-1], np.linspace(0, 1, 11)[1:]):
        selected = (confidence >= lo) & (confidence < hi if hi < 1 else confidence <= hi)
        if selected.any():
            calibration_bins.append({"range": [float(lo), float(hi)], "samples": int(selected.sum()),
                                     "mean_confidence": float(confidence[selected].mean()),
                                     "accuracy": float(accurate[selected].mean())})
    np.add.at(actual_density, t, 1); np.add.at(predicted_density, p, 1)
    phase_densities = {}
    for phase, selected in (("early", minutes < 10),
                            ("middle", (minutes >= 10) & (minutes < 20)),
                            ("late", minutes >= 20)):
        observed = np.bincount(t[selected], minlength=GRID**2)
        predicted = np.bincount(p[selected], minlength=GRID**2)
        phase_densities[phase] = {"samples": int(selected.sum()),
                                  "observed_density": observed.tolist(),
                                  "predicted_density": predicted.tolist()}
    baseline = {"most_frequent": float(np.mean(t == common)), "copy_previous": float(np.mean(t == prev)),
                "stay_mid": float(np.mean(t == (32 * GRID + 32))), "role_phase_prior": float(np.mean(t == prior))}
    grouped = defaultdict(list)
    for i, mid in enumerate(mids): grouped[mid].append(i)
    groups = [np.asarray(v) for v in grouped.values()]
    rng = np.random.default_rng(CONFIG.seed)
    gains = []
    for _ in range(1000):
        idx = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        base = max(np.mean(t[idx] == common), np.mean(t[idx] == prev[idx]),
                   np.mean(t[idx] == 32 * GRID + 32), np.mean(t[idx] == prior[idx]))
        gains.append(100 * (np.mean(p[idx] == t[idx]) - base))
    t16 = coarse_labels(t, 16)
    report = {"grid": GRID, "split": split, "matches": len(grouped), "samples": len(t),
              "model_top1": float(accurate.mean()), "model_top5": float(np.mean(top5)),
              "model_top25": float(np.mean(top25)), "model_top100": float(np.mean(top100)),
              "mean_distance_cells": float(displacement.mean()),
              "previous_mean_distance_cells": float(previous_distance[prev >= 0].mean()) if (prev >= 0).any() else None,
              "within_radius_cells": {str(r): {"model": float(np.mean(displacement <= r)),
                                                "copy_previous": float(np.mean(previous_distance <= r))}
                                      for r in (2, 4, 8, 16)},
              "set90": {"method": "validation_rank_mass_calibration", "rank_mass_threshold": threshold,
                        "empirical_coverage": float(np.mean(set90_hit)),
                        "mean_cells": float(np.mean(set90_size)),
                        "median_cells": float(np.median(set90_size)),
                        "mean_map_area_fraction": float(np.mean(set90_size) / (GRID * GRID))},
              "raw_set90": {"empirical_coverage": float(np.mean(raw_set90_hit)),
                            "mean_map_area_fraction": float(np.mean(raw_set90_size) / (GRID * GRID))},
              "mean_true_cell_probability": float(np.mean(true_probability)),
              "confidence_calibration_bins": calibration_bins,
              "baseline": baseline, "gain_vs_best_pp": 100 * (float(np.mean(p == t)) - max(baseline.values())),
              "gain_bootstrap95_pp": np.quantile(gains, [.025, .975]).tolist(),
              "pooled16_top1": float(np.mean(np.asarray(coarse_guess) == t16)),
              "observed_density": actual_density.tolist(), "predicted_density": predicted_density.tolist(),
              "phase_densities": phase_densities,
              "domain": "ranked_solo_holdout"}
    artifacts.mkdir(parents=True, exist_ok=True)
    atomic_json(artifacts / f"evaluation_{split}.json", report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("prepare", "train", "val", "test"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--epochs", type=int, default=25)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.stage == "prepare": result = prepare(args.limit)
    elif args.stage == "train": result = train(epochs=args.epochs)
    else: result = evaluate(args.stage)
    print({k: v for k, v in result.items() if k not in ("region_weights", "observed_density", "predicted_density", "phase_densities", "splits", "counts", "sources", "history", "item_vocab")})


if __name__ == "__main__": main()
