"""Development-only coarse-to-fine Faker policy and controlled context ablations.

Only ranked train/validation matches are read. The frozen prospective model and
the previously inspected test split are never loaded by this experiment.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict, defaultdict
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
from torch.utils.data import DataLoader, Dataset, Subset
from tqdm import tqdm

from .config import CONFIG
from .features import FEATURE_NAMES
from .finegrid import coarse_labels
from .util import atomic_json, read_json, seed_all

SOURCE = CONFIG.root / "data" / "interaction"
LABELS = CONFIG.root / "data" / "processed64" / "labels"
TAGS = CONFIG.processed / "macro_actions"
MODELS = CONFIG.models / "hierarchical"
ARTIFACTS = CONFIG.artifacts / "hierarchical"
DECISIONS = ("hold", "reset_base", "dragon_side", "baron_side", "other_move")
VARIANTS = ("faker", "allies", "full")


def feature_mask(names: list[str], variant: str) -> np.ndarray:
    """Same input width for every ablation; remove entire unavailable channels."""
    if variant not in VARIANTS:
        raise ValueError(f"Unknown context variant: {variant}")
    if variant == "full":
        return np.ones(len(names), dtype=np.float32)
    own = {"minute", "own_gold", "own_level", "own_xp", "own_cs", "own_kills",
           "own_deaths", "recent_purchases", "faker_role", "team_side",
           "own_current_gold", "own_at_base", "own_recent_deaths",
           "own_level_delta", "own_gold_delta"}
    ally = {"team_gold", "team_xp", "recent_ally_wards", "recent_ally_ward_kills",
            "recent_ally_kills", "recent_jungle_kill_participation",
            "recent_bot_kill_participation", "allies_within_2500"}
    result = []
    for name in names:
        allowed = name in own or name.startswith("p0_")
        if variant == "allies":
            allowed = (allowed or name in ally or name.startswith(tuple(f"p{i}_" for i in range(1, 5)))
                       or name.startswith("ally_") and name.endswith("_distance"))
        result.append(float(allowed))
    return np.asarray(result, np.float32)


def decision_labels(x: np.ndarray, next_xy: np.ndarray, tags: np.ndarray,
                    valid: np.ndarray) -> np.ndarray:
    """Observed movement classes; -100 masks missing current position.

    Priority: reset > Dragon approach > Baron approach > nearby hold > other.
    Dragon/Baron tags are valid only if the objective was live at time t.
    """
    if not (len(x) == len(next_xy) == len(tags) == len(valid)):
        raise ValueError("Decision sources are misaligned")
    current = x[:, -1, 17:19]
    known = x[:, -1, 19] > .5
    travel = np.linalg.norm(next_xy - current, axis=1) * 15000
    output = np.full(len(x), 4, dtype=np.int64)
    output[travel <= 1200] = 0
    output[(tags[:, 6] > 0) & valid[:, 6]] = 3
    output[(tags[:, 5] > 0) & valid[:, 5]] = 2
    output[(tags[:, 7] > 0) & valid[:, 7]] = 1
    output[~known] = -100
    return output


class DecisionDataset(Dataset):
    """Only offsets stay in RAM; at most two decompressed matches are cached."""
    def __init__(self, ids: list[str], counts: dict[str, int], mask: np.ndarray,
                 source: Path = SOURCE, labels: Path = LABELS, tags: Path = TAGS,
                 max_cached: int = 2):
        self.index = [(mid, i) for mid in ids for i in range(counts[mid])]
        self.mask = mask
        self.source, self.labels, self.tags = source, labels, tags
        self.max_cached = max_cached
        self.cache: OrderedDict[str, dict] = OrderedDict()

    def __len__(self) -> int:
        return len(self.index)

    def _match(self, mid: str) -> dict:
        if mid not in self.cache:
            with np.load(self.source / "matches" / f"{mid}.npz") as xz, \
                 np.load(self.labels / f"{mid}.npz") as yz, \
                 np.load(self.tags / f"{mid}.npz") as tz:
                x = xz["x"]
                y64, xy = yz["region"], yz["xy"]
                if (len(x) != len(y64) or len(x) != len(tz["tags"]) or
                    not np.array_equal(coarse_labels(y64, 16), xz["region"])):
                    raise ValueError(f"Hierarchical labels differ from original labels: {mid}")
                if not np.allclose(xz["minute"], yz["minute"], atol=.001):
                    raise ValueError(f"Hierarchical timestamps differ: {mid}")
                self.cache[mid] = {"x": x, "champion": xz["champion"], "region64": y64,
                                   "previous": yz["previous"], "minute": yz["minute"],
                                   "decision": decision_labels(x, xy, tz["tags"], tz["valid"]),
                                   "tags": tz["tags"], "valid": tz["valid"]}
            if len(self.cache) > self.max_cached:
                self.cache.popitem(last=False)
        self.cache.move_to_end(mid)
        return self.cache[mid]

    def __getitem__(self, index: int):
        mid, i = self.index[index]
        a = self._match(mid)
        return (torch.from_numpy((a["x"][i] * self.mask).copy()),
                torch.tensor(int(a["champion"][i])), torch.tensor(int(a["region64"][i])),
                torch.tensor(int(a["decision"][i])),
                torch.from_numpy(a["tags"][i].astype(np.float32)),
                torch.from_numpy(a["valid"][i].astype(np.float32)),
                torch.tensor(float(a["minute"][i])), torch.tensor(int(a["previous"][i])))


class MatchBatchSampler:
    """Shuffle match order, then read each match contiguously before eviction."""
    def __init__(self, dataset: DecisionDataset, batch_size: int, seed: int = CONFIG.seed):
        self.groups: dict[str, list[int]] = defaultdict(list)
        for index, (mid, _) in enumerate(dataset.index): self.groups[mid].append(index)
        self.batch_size, self.seed, self.epoch = batch_size, seed, 0
        self.total = len(dataset)

    def __len__(self) -> int:
        return math.ceil(self.total / self.batch_size)

    def __iter__(self):
        rng = np.random.default_rng(self.seed + self.epoch)
        self.epoch += 1
        mids = list(self.groups)
        rng.shuffle(mids)
        pending = []
        for mid in mids:
            pending.extend(rng.permutation(self.groups[mid]).tolist())
            while len(pending) >= self.batch_size:
                yield pending[:self.batch_size]
                pending = pending[self.batch_size:]
        if pending: yield pending


class HierarchicalPolicy(nn.Module):
    def __init__(self, feature_dim: int, width: int = 96, layers: int = 2):
        super().__init__()
        self.numeric = nn.Linear(feature_dim, width)
        self.champion = nn.Embedding(1000, width)
        self.time = nn.Embedding(64, width)
        block = nn.TransformerEncoderLayer(width, 4, width * 3, dropout=.1,
                                           batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(block, layers)
        self.norm = nn.LayerNorm(width)
        self.coarse = nn.Linear(width, 64)
        self.mid = nn.Linear(width, 64 * 4)
        self.fine = nn.Linear(width, 256 * 16)
        self.decision = nn.Linear(width, len(DECISIONS))
        self.tags = nn.Linear(width, 8)
        self.proximity_scale = nn.Parameter(torch.tensor(1.0))
        yy, xx = torch.meshgrid(torch.arange(8), torch.arange(8), indexing="ij")
        self.register_buffer("centers8", torch.stack(((xx.flatten() + .5) / 8,
                                                      (yy.flatten() + .5) / 8), -1).float())

    def forward(self, x: torch.Tensor, champion: torch.Tensor):
        h = self.numeric(x) + self.champion(champion.clamp(0, 999))[:, None]
        h = h + self.time(torch.arange(x.shape[1], device=x.device))[None]
        h = self.norm(self.encoder(h)[:, -1])
        current = x[:, -1, 17:19]
        distance = ((current[:, None] - self.centers8[None]) ** 2).sum(-1)
        coarse = self.coarse(h) - F.softplus(self.proximity_scale) * 8 * distance
        log8 = F.log_softmax(coarse, -1).reshape(-1, 8, 8)
        local16 = F.log_softmax(self.mid(h).reshape(-1, 8, 8, 4), -1).reshape(-1, 8, 8, 2, 2)
        log16 = (log8[..., None, None] + local16).permute(0, 1, 3, 2, 4).reshape(-1, 16, 16)
        local64 = F.log_softmax(self.fine(h).reshape(-1, 16, 16, 16), -1).reshape(-1, 16, 16, 4, 4)
        log64 = (log16[..., None, None] + local64).permute(0, 1, 3, 2, 4).reshape(-1, 4096)
        return log8.flatten(1), log16.flatten(1), log64, self.decision(h), self.tags(h)


def train_statistics(ids: list[str], counts: dict[str, int], names: list[str],
                     source: Path = SOURCE, labels: Path = LABELS, tags: Path = TAGS) -> dict:
    """Class balance and baselines are derived only from training matches."""
    dataset = DecisionDataset(ids, counts, np.ones(len(names), np.float32), source, labels, tags)
    counts8, counts16, counts64, decisions = Counter(), Counter(), Counter(), Counter()
    role_phase: dict[tuple[int, int], Counter] = defaultdict(Counter)
    positives = np.zeros(8, dtype=np.float64)
    available = np.zeros(8, dtype=np.float64)
    role_index = names.index("faker_role")
    for mid in tqdm(ids, desc="training priors", unit="game"):
        data = dataset._match(mid)
        y64 = data["region64"]
        y16, y8 = coarse_labels(y64, 16), coarse_labels(y64, 8)
        counts64.update(map(int, y64)); counts16.update(map(int, y16)); counts8.update(map(int, y8))
        decisions.update(map(int, data["decision"][data["decision"] >= 0]))
        original = data["x"][:, -1]
        for target, role, minute in zip(y8, original[:, role_index], data["minute"]):
            role_phase[(round(float(role) * 5), int(minute >= 10) + int(minute >= 20))][int(target)] += 1
        positives += (data["tags"] * data["valid"]).sum(0)
        available += data["valid"].sum(0)
    decision_weight = np.array([min(4.0, math.sqrt(sum(decisions.values()) /
                                    (len(DECISIONS) * max(1, decisions[i])))) for i in range(len(DECISIONS))],
                               dtype=np.float32)
    decision_weight /= decision_weight.mean()
    tag_pos_weight = np.clip((available - positives) / np.maximum(positives, 1), 1, 10).astype(np.float32)
    return {"counts8": counts8, "counts16": counts16, "counts64": counts64,
            "decisions": decisions, "role_phase": role_phase,
            "decision_weight": decision_weight, "tag_pos_weight": tag_pos_weight,
            "tag_positives": positives.astype(int).tolist(), "tag_valid": available.astype(int).tolist()}


def batch_loss(outputs, batch, weights: dict[str, torch.Tensor]) -> torch.Tensor:
    log8, log16, log64, decision_logits, tag_logits = outputs
    _, _, y64, decision, tags, valid, _, _ = batch
    y16 = coarse_labels(y64, 16)
    y8 = coarse_labels(y64, 8)
    loss = (F.nll_loss(log8, y8) + .5 * F.nll_loss(log16, y16) +
            .2 * F.nll_loss(log64, y64))
    available = decision >= 0
    if available.any():
        loss = loss + .25 * F.cross_entropy(decision_logits[available], decision[available],
                                            weight=weights["decision"])
    tag_loss = F.binary_cross_entropy_with_logits(tag_logits, tags, reduction="none",
                                                  pos_weight=weights["tags"])
    loss = loss + .08 * (tag_loss * valid).sum() / valid.sum().clamp_min(1)
    return loss


def epoch(model, loader, optimizer, device: str, weights: dict, *, train: bool) -> dict:
    model.train(train)
    total_loss = hits8 = hits16 = samples = 0
    for batch in loader:
        batch = tuple(v.to(device) for v in batch)
        with torch.set_grad_enabled(train):
            outputs = model(batch[0], batch[1])
            loss = batch_loss(outputs, batch, weights)
            if train:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1)
                optimizer.step()
        n = len(batch[2]); samples += n
        total_loss += float(loss.detach()) * n
        hits8 += int((outputs[0].argmax(-1) == coarse_labels(batch[2], 8)).sum())
        hits16 += int((outputs[1].argmax(-1) == coarse_labels(batch[2], 16)).sum())
    return {"loss": total_loss / samples, "top1_8": hits8 / samples,
            "top1_16": hits16 / samples, "samples": samples}


def probe_device(dataset: Dataset, feature_dim: int, weights: dict, batch_size: int) -> dict:
    times = {}
    for device in (["cpu", "mps"] if torch.backends.mps.is_available() else ["cpu"]):
        seed_all(CONFIG.seed)
        model = HierarchicalPolicy(feature_dim).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
        loader = DataLoader(Subset(dataset, range(min(len(dataset), 128))), batch_size=batch_size)
        local_weights = {key: value.to(device) for key, value in weights.items()}
        start = time.perf_counter()
        epoch(model, loader, optimizer, device, local_weights, train=True)
        if device == "mps": torch.mps.synchronize()
        times[device] = round(time.perf_counter() - start, 4)
    return times


def prior_table(stats: dict, smoothing: float = .5) -> torch.Tensor:
    """Train-only role/phase 8x8 log prior with additive smoothing."""
    table = np.zeros((6, 3, 64), np.float32)
    for role in range(6):
        for phase in range(3):
            counts = stats["role_phase"].get((role, phase), stats["counts8"])
            row = np.asarray([counts.get(i, 0) + smoothing for i in range(64)], np.float32)
            table[role, phase] = np.log(row / row.sum())
    return torch.from_numpy(table)


def adjusted_hierarchy(log8: torch.Tensor, log16: torch.Tensor, log64: torch.Tensor,
                       bias8: torch.Tensor, alpha: float):
    """Change parent masses while preserving both conditional distributions."""
    if not alpha:
        return log8, log16, log64
    mixed8 = F.log_softmax(log8 + alpha * bias8, -1)
    change = (mixed8 - log8).reshape(-1, 8, 8)
    change16 = change[..., None, None].expand(-1, -1, -1, 2, 2).permute(0, 1, 3, 2, 4).reshape(-1, 256)
    change64 = change[..., None, None].expand(-1, -1, -1, 8, 8).permute(0, 1, 3, 2, 4).reshape(-1, 4096)
    return mixed8, log16 + change16, log64 + change64


def choose_prior_alpha(model: HierarchicalPolicy, dataset: DecisionDataset,
                       stats: dict, names: list[str], batch_size: int = 128) -> dict:
    """Small validation-only sweep; ties choose the less adjusted policy."""
    scales = (0.0, .25, .5, 1.0, 1.5, 2.0, 3.0)
    hits = {scale: 0 for scale in scales}
    table = prior_table(stats)
    role_index = names.index("faker_role")
    model.eval()
    samples = 0
    with torch.no_grad():
        for x, champion, y64, _, _, _, minute, _ in DataLoader(dataset, batch_size=batch_size):
            log8 = model(x, champion)[0]
            role = (x[:, -1, role_index] * 5).round().long().clamp(0, 5)
            phase = (minute >= 10).long() + (minute >= 20).long()
            bias = table[role, phase]
            truth = coarse_labels(y64, 8)
            for scale in scales:
                hits[scale] += int(((log8 + scale * bias).argmax(-1) == truth).sum())
            samples += len(truth)
    selected = max(scales, key=lambda scale: (hits[scale], -scale))
    return {"alpha": selected, "validation_accuracy_by_alpha":
            {str(scale): hits[scale] / samples for scale in scales}}


def score(model: HierarchicalPolicy, dataset: DecisionDataset, stats: dict,
          names: list[str], batch_size: int = 128, prior_alpha: float = 0.0) -> dict:
    model.eval()
    truth64, pred8, pred16, pred64, true_decision, pred_decision = [], [], [], [], [], []
    minutes, champions, previous, roles = [], [], [], []
    tag_true, tag_pred, tag_valid = [], [], []
    role_index = names.index("faker_role")
    table = prior_table(stats)
    with torch.no_grad():
        for x, champion, y64, decision, tags, valid, minute, prev in tqdm(
                DataLoader(dataset, batch_size=batch_size), desc="validation", unit="batch"):
            log8, log16, log64, dlogit, tlogit = model(x, champion)
            if prior_alpha:
                role = (x[:, -1, role_index] * 5).round().long().clamp(0, 5)
                phase = (minute >= 10).long() + (minute >= 20).long()
                log8, log16, log64 = adjusted_hierarchy(log8, log16, log64,
                                                          table[role, phase], prior_alpha)
            truth64.extend(y64.tolist())
            pred8.extend(log8.argmax(-1).tolist())
            pred16.extend(log16.argmax(-1).tolist())
            pred64.extend(log64.argmax(-1).tolist())
            true_decision.extend(decision.tolist()); pred_decision.extend(dlogit.argmax(-1).tolist())
            minutes.extend(minute.tolist()); champions.extend(champion.tolist())
            previous.extend(prev.tolist())
            roles.extend((x[:, -1, role_index] * 5).round().long().tolist())
            tag_true.extend(tags.tolist()); tag_pred.extend((tlogit.sigmoid() >= .5).tolist())
            tag_valid.extend(valid.tolist())
    y64 = np.asarray(truth64, np.int64); y16 = coarse_labels(y64, 16); y8 = coarse_labels(y64, 8)
    p8, p16, p64 = map(np.asarray, (pred8, pred16, pred64))
    minutes, previous, roles, champions = map(np.asarray, (minutes, previous, roles, champions))
    pprev = coarse_labels(previous, 8)
    pprev[previous < 0] = -1
    frequent = stats["counts8"].most_common(1)[0][0]
    role_prior = np.asarray([stats["role_phase"][(int(role), int(minute >= 10) + int(minute >= 20))].most_common(1)[0][0]
                             if stats["role_phase"].get((int(role), int(minute >= 10) + int(minute >= 20)))
                             else frequent for role, minute in zip(roles, minutes)])
    baselines = {"most_frequent": float(np.mean(y8 == frequent)),
                 "copy_previous": float(np.mean(y8 == pprev)),
                 "stay_mid": float(np.mean(y8 == 4 * 8 + 4)),
                 "role_phase_prior": float(np.mean(y8 == role_prior))}
    match_groups = defaultdict(list)
    for i, (mid, _) in enumerate(dataset.index): match_groups[mid].append(i)
    groups = [np.asarray(v) for v in match_groups.values()]
    by_match8 = {mid: {"samples": len(rows), "correct": int(np.sum(y8[rows] == p8[rows]))}
                 for mid, rows in match_groups.items()}
    rng = np.random.default_rng(CONFIG.seed)
    gains = []
    for _ in range(1000):
        idx = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        base = max(np.mean(y8[idx] == frequent), np.mean(y8[idx] == pprev[idx]),
                   np.mean(y8[idx] == 4 * 8 + 4), np.mean(y8[idx] == role_prior[idx]))
        gains.append(100 * (np.mean(y8[idx] == p8[idx]) - base))
    dtrue, dpred = np.asarray(true_decision), np.asarray(pred_decision)
    dvalid = dtrue >= 0
    majority_decision = stats["decisions"].most_common(1)[0][0]
    def decision_classes(predictions):
        rows = []
        for i, name in enumerate(DECISIONS):
            t, p = dtrue[dvalid] == i, predictions[dvalid] == i
            tp, fp, fn = int((t & p).sum()), int((~t & p).sum()), int((t & ~p).sum())
            rows.append({"class": name, "support": int(t.sum()),
                         "precision": tp / (tp + fp) if tp + fp else 0.0,
                         "recall": tp / (tp + fn) if tp + fn else 0.0,
                         "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0})
        return rows
    decision_rows = decision_classes(dpred)
    baseline_decision_rows = decision_classes(np.full_like(dpred, majority_decision))
    supported = [i for i, row in enumerate(decision_rows) if row["support"]]
    tag_true, tag_pred, tag_valid = map(np.asarray, (tag_true, tag_pred, tag_valid))
    tag_metrics = []
    for j, name in enumerate(("approach_jungle", "approach_bot", "approach_support", "approach_mid",
                              "approach_top", "approach_dragon", "approach_baron", "reset_base")):
        v = tag_valid[:, j] > .5; t = tag_true[v, j] > .5; p = tag_pred[v, j] > .5
        tp, fp, fn = int((t & p).sum()), int((~t & p).sum()), int((t & ~p).sum())
        tag_metrics.append({"tag": name, "valid": int(v.sum()), "positive": int(t.sum()),
                            "precision": tp / (tp + fp) if tp + fp else None,
                            "recall": tp / (tp + fn) if tp + fn else None,
                            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None})
    phase_rows = {}
    for phase, selected in (("early", minutes < 10), ("middle", (minutes >= 10) & (minutes < 20)),
                            ("late", minutes >= 20)):
        phase_rows[phase] = {"samples": int(selected.sum()),
                             "top1_8": float(np.mean(y8[selected] == p8[selected])) if selected.any() else None}
    champion_rows = []
    for champion, n in Counter(champions.tolist()).most_common():
        if n < 20: continue
        selected = champions == champion
        champion_rows.append({"champion_id": int(champion), "samples": n,
                              "top1_8": float(np.mean(y8[selected] == p8[selected]))})
    exact8 = float(np.mean(y8 == p8))
    return {"split": "val", "matches": len(groups), "samples": len(y8),
            "prior_alpha": prior_alpha, "by_match8": by_match8,
            "top1_8": exact8, "top1_16": float(np.mean(y16 == p16)),
            "top1_64": float(np.mean(y64 == p64)), "baselines8": baselines,
            "gain_vs_best_pp": 100 * (exact8 - max(baselines.values())),
            "gain_bootstrap95_pp": np.quantile(gains, [.025, .975]).tolist(),
            "decision_accuracy": float(np.mean(dtrue[dvalid] == dpred[dvalid])) if dvalid.any() else None,
            "decision_valid": int(dvalid.sum()),
            "decision_most_frequent_baseline": float(np.mean(dtrue[dvalid] == majority_decision))
                if dvalid.any() else None,
            "decision_macro_f1": float(np.mean([decision_rows[i]["f1"] for i in supported])) if supported else None,
            "decision_majority_macro_f1": float(np.mean([baseline_decision_rows[i]["f1"] for i in supported]))
                if supported else None,
            "decision_by_class": decision_rows,
            "decision_counts": {DECISIONS[i]: int((dtrue == i).sum()) for i in range(len(DECISIONS))},
            "tags": tag_metrics, "by_phase": phase_rows, "by_champion": champion_rows,
            "scope": "historical development validation only; no old test or prospective score"}


def run(*, pilot: bool = False, epochs: int = 25, batch_size: int = 128,
        patience: int = 5, width: int = 96, layers: int = 2,
        variants: tuple[str, ...] = VARIANTS) -> dict:
    meta = read_json(SOURCE / "meta.json")
    if not meta:
        raise FileNotFoundError("Build interaction features first")
    if meta["feature_dim"] != len(meta["feature_names"]):
        raise ValueError("Feature names and dimensions differ")
    ids_train = meta["splits"]["train"][:3] if pilot else meta["splits"]["train"]
    ids_val = meta["splits"]["val"][:2] if pilot else meta["splits"]["val"]
    if set(ids_train) & set(ids_val) or set(ids_train + ids_val) & set(meta["splits"]["test"]):
        raise ValueError("Training/validation/test match overlap")
    output_models = MODELS.parent / "hierarchical-pilot" if pilot else MODELS
    output_artifacts = ARTIFACTS.parent / "hierarchical-pilot" if pilot else ARTIFACTS
    output_models.mkdir(parents=True, exist_ok=True)
    output_artifacts.mkdir(parents=True, exist_ok=True)
    stats = train_statistics(ids_train, meta["counts"], meta["feature_names"])
    weights_cpu = {"decision": torch.from_numpy(stats["decision_weight"]),
                   "tags": torch.from_numpy(stats["tag_pos_weight"])}
    probe = DecisionDataset(ids_train, meta["counts"], feature_mask(meta["feature_names"], "full"))
    times = probe_device(probe, meta["feature_dim"], weights_cpu, batch_size)
    device = min(times, key=times.get)
    results = {}
    for variant in variants:
        mask = feature_mask(meta["feature_names"], variant)
        train_set = DecisionDataset(ids_train, meta["counts"], mask)
        val_set = DecisionDataset(ids_val, meta["counts"], mask)
        signature = hashlib.sha256(json.dumps({"train": ids_train, "val": ids_val,
            "counts": meta["counts"], "schema": meta["schema_version"], "variant": variant,
            "mask": mask.tolist(), "epochs": epochs, "width": width, "layers": layers,
            "lr": 3e-4, "loss": [1, .5, .2, .25, .08]}, sort_keys=True).encode()).hexdigest()
        checkpoint = output_models / f"{variant}.pt"
        training_path = output_models / f"{variant}_training.json"
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False) if checkpoint.exists() else None
        finished = read_json(training_path, {})
        if (saved and saved.get("signature") == signature and
            finished.get("signature") == signature and finished.get("status") == "complete"):
            print(f"{variant}: matched checkpoint reused", flush=True)
        else:
            seed_all(CONFIG.seed)
            model = HierarchicalPolicy(meta["feature_dim"], width, layers).to(device)
            parameters = sum(p.numel() for p in model.parameters())
            if parameters >= 5_000_000: raise ValueError("Policy exceeds 5M parameters")
            optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=.01)
            weights = {key: value.to(device) for key, value in weights_cpu.items()}
            train_loader = DataLoader(train_set, batch_sampler=MatchBatchSampler(train_set, batch_size))
            val_loader = DataLoader(val_set, batch_size=batch_size)
            history = []
            best8, best_loss, stale = -1.0, float("inf"), 0
            for number in tqdm(range(1, epochs + 1), desc=f"{variant} {device}", unit="epoch"):
                training = epoch(model, train_loader, optimizer, device, weights, train=True)
                validation = epoch(model, val_loader, None, device, weights, train=False)
                history.append({"epoch": number, "train": training, "val": validation})
                better = (validation["top1_8"] > best8 + 1e-9 or
                          abs(validation["top1_8"] - best8) < 1e-9 and validation["loss"] < best_loss - 1e-4)
                if better:
                    best8, best_loss, stale = validation["top1_8"], validation["loss"], 0
                    temporary = checkpoint.with_suffix(".tmp")
                    torch.save({"state_dict": {k:v.detach().cpu().clone() for k,v in model.state_dict().items()},
                                "signature": signature, "variant": variant, "width": width, "layers": layers,
                                "parameters": parameters, "epoch": number, "selected_val8": best8}, temporary)
                    os.replace(temporary, checkpoint)
                else:
                    stale += 1
                    if stale >= patience: break
            atomic_json(training_path, {"variant": variant, "signature": signature, "status": "complete",
                "device": device, "benchmark_seconds": times, "parameters": parameters,
                "selected_val8": best8, "selected_epoch": torch.load(checkpoint, map_location="cpu", weights_only=False)["epoch"],
                "history": history, "train_matches": len(ids_train), "val_matches": len(ids_val),
                "active_features": int(mask.sum()), "total_features": len(mask), "seed": CONFIG.seed})
            saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        model = HierarchicalPolicy(meta["feature_dim"], saved["width"], saved["layers"])
        model.load_state_dict(saved["state_dict"])
        sweep = choose_prior_alpha(model, val_set, stats, meta["feature_names"])
        raw = score(model, val_set, stats, meta["feature_names"])
        result = (score(model, val_set, stats, meta["feature_names"], prior_alpha=sweep["alpha"])
                  if sweep["alpha"] else raw)
        result.update({"variant": variant, "active_features": int(mask.sum()),
                       "parameters": saved["parameters"], "checkpoint_signature": signature,
                       "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                       "selected_epoch": saved["epoch"], "raw_top1_8": raw["top1_8"],
                       "prior_sweep": sweep, "raw_by_match8": raw["by_match8"]})
        results[variant] = result
        atomic_json(output_artifacts / f"validation_{variant}.json", result)
    winner = max(results, key=lambda name: (results[name]["top1_8"], results[name]["top1_16"],
                                            results[name]["top1_64"]))
    rng = np.random.default_rng(CONFIG.seed)
    paired = {}
    for context in ("allies", "full"):
        if context not in results or "faker" not in results: continue
        mids = ids_val
        a, b = results[context]["raw_by_match8"], results["faker"]["raw_by_match8"]
        delta = 100 * (sum(a[mid]["correct"] for mid in mids) - sum(b[mid]["correct"] for mid in mids)) / sum(a[mid]["samples"] for mid in mids)
        draws = []
        for _ in range(1000):
            pick = rng.integers(0, len(mids), len(mids))
            draws.append(100 * sum(a[mids[j]]["correct"] - b[mids[j]]["correct"] for j in pick) /
                         sum(a[mids[j]]["samples"] for j in pick))
        paired[context + "_minus_faker_raw_pp"] = {"delta": delta,
                                                   "bootstrap95": np.quantile(draws, [.025, .975]).tolist()}
    frozen_protocol = read_json(CONFIG.root / "data" / "prospective" / "protocol.json", {})
    frozen_expected = frozen_protocol.get("checkpoint_sha256")
    frozen_paths = (CONFIG.root / "data" / "prospective" / "frozen_checkpoint.pt",
                    CONFIG.models / "best.pt")
    frozen_verified = (all(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == frozen_expected
                           for path in frozen_paths) if frozen_expected else None)
    if frozen_verified is False:
        raise RuntimeError("Frozen M0 checkpoint hash changed; refusing to publish M3 report")
    report = {"status": "development_only", "pilot": pilot, "train_matches": len(ids_train),
              "val_matches": len(ids_val), "train_samples": sum(meta["counts"][mid] for mid in ids_train),
              "val_samples": sum(meta["counts"][mid] for mid in ids_val), "device": device,
              "device_probe_seconds": times, "selected_variant": winner,
              "selected_checkpoint_signature": results[winner]["checkpoint_signature"],
              "paired_context_deltas": paired,
              "variants": {name: {key: result[key] for key in ("top1_8", "top1_16", "top1_64",
                           "raw_top1_8", "prior_alpha", "prior_sweep",
                           "gain_vs_best_pp", "gain_bootstrap95_pp", "decision_accuracy",
                           "decision_most_frequent_baseline", "decision_macro_f1",
                           "decision_majority_macro_f1", "active_features", "parameters", "selected_epoch",
                           "checkpoint_sha256")}
                           for name, result in results.items()},
              "baseline8": results[winner]["baselines8"],
              "frozen_model_unchanged": frozen_verified,
              "historical_test_unread_for_selection": True}
    atomic_json(output_artifacts / "comparison.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--variants", nargs="+", choices=VARIANTS, default=list(VARIANTS))
    args = parser.parse_args()
    report = run(pilot=args.pilot_only, epochs=args.epochs,
                 batch_size=args.batch_size, variants=tuple(args.variants))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
