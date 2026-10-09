import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from .config import CONFIG
from .dataset import MatchDataset
from .model import MacroTransformer
from .train import signature
from .util import atomic_json, read_json


def load_model(meta: dict, checkpoint: Path, device: str = "cpu", use_calibration: bool = True):
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if saved.get("signature") != signature(meta):
        raise ValueError("Checkpoint and dataset split/vocabulary differ; retrain")
    config = saved.get("config") or {}
    model = MacroTransformer(meta["feature_dim"], len(meta["item_vocab"]) + 2,
                             width=config.get("width", 128), layers=config.get("layers", 2),
                             spatial_head=config.get("spatial_head", False))
    model.load_state_dict(saved["state_dict"])
    calibration = saved.get("calibration") if use_calibration else None
    model.has_calibration = bool(calibration)
    if calibration:
        model.region_log_prior.copy_(torch.tensor(calibration["log_prior"], dtype=torch.float32))
        model.prior_alpha = float(calibration["alpha"])
        model.item_none_bias = float(calibration.get("item_none_bias", 0.0))
        model.skill_none_bias = float(calibration.get("skill_none_bias", 0.0))
    model.to(device).eval()
    model.view = config.get("view", "proxy")
    return model


def evaluate(processed: Path = CONFIG.processed, models: Path = CONFIG.models,
             artifacts: Path = CONFIG.artifacts, batch_size: int = 128,
             split: str = "test") -> dict:
    if split not in ("val", "test"):
        raise ValueError("Evaluation split must be val or test")
    meta = read_json(processed / "meta.json")
    model = load_model(meta, models / "best.pt")
    ds = MatchDataset(processed, meta, split, view=model.view)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=0)
    train_regions = Counter()
    for mid in meta["splits"]["train"]:
        with np.load(processed / "matches" / f"{mid}.npz") as z:
            train_regions.update(int(x) for x in z["region"])
    most_common = train_regions.most_common(1)[0][0]
    predictions, truths, item_pred, item_true, skill_pred, skill_true, champions, top5 = [], [], [], [], [], [], [], []
    value_pred, value_true, prior_predictions = [], [], []
    macro_predictions = {8: [], 4: []}
    macro_prior_predictions = {8: [], 4: []}
    def pooled_region(logits: torch.Tensor, grid: int) -> torch.Tensor:
        block = 16 // grid
        return logits.reshape(-1, grid, block, grid, block).logsumexp(-1).logsumexp(2).reshape(-1, grid * grid).argmax(-1)
    with torch.no_grad():
        for x, champ, r, item, skill, win in tqdm(loader, desc="evaluate", unit="batch"):
            out_r, out_i, out_s, out_v = model(x, champ)
            predictions.extend(out_r.argmax(-1).numpy().tolist())
            for grid in macro_predictions:
                macro_predictions[grid].extend(pooled_region(out_r, grid).numpy().tolist())
            top5.extend((out_r.topk(5, dim=-1).indices == r[:, None]).any(-1).numpy().tolist())
            truths.extend(r.numpy().tolist())
            item_pred.extend(out_i.argmax(-1).numpy().tolist())
            item_true.extend(item.numpy().tolist())
            skill_pred.extend(out_s.argmax(-1).numpy().tolist())
            skill_true.extend(skill.numpy().tolist())
            champions.extend(champ.numpy().tolist())
            value_pred.extend(out_v.sigmoid().numpy().tolist())
            value_true.extend(win.numpy().tolist())
            if model.has_calibration:
                role = (x[:, -1, model.role_feature_index] * 5).round().long().clamp(0, 5)
                minute = x[:, -1, 0] * 50
                phase = (minute >= 10).long() + (minute >= 20).long()
                prior_logits = model.region_log_prior[role, phase]
                prior_predictions.extend(prior_logits.argmax(-1).numpy().tolist())
                for grid in macro_prior_predictions:
                    macro_prior_predictions[grid].extend(pooled_region(prior_logits, grid).numpy().tolist())
    previous, minutes, gold_diffs = [], [], []
    for mid in meta["splits"][split]:
        with np.load(processed / "matches" / f"{mid}.npz") as z:
            previous.extend(z["previous"].tolist())
            minutes.extend(z["minute"].tolist())
            gold_diffs.extend((z["x"][:, -1, 7] * 30000).tolist())
    true, pred, prev = np.asarray(truths), np.asarray(predictions), np.asarray(previous)
    items, item_predictions = np.asarray(item_true), np.asarray(item_pred)
    skills, skill_predictions = np.asarray(skill_true), np.asarray(skill_pred)
    value_prob, value_actual = np.asarray(value_pred), np.asarray(value_true)
    def grid_distance(a, b):
        valid = (np.asarray(a) >= 0) & (np.asarray(b) >= 0)
        return float(np.mean(np.hypot((np.asarray(a)[valid] % 16) - (np.asarray(b)[valid] % 16),
                                      (np.asarray(a)[valid] // 16) - (np.asarray(b)[valid] // 16))))
    train_win_rate = float(np.mean([meta["faker_wins"][mid] for mid in meta["splits"]["train"]]))
    conditional = items != 0
    skill_conditional = skills != 0
    prior = np.asarray(prior_predictions) if prior_predictions else None
    result = {"view": model.view, "split": split, "matches": len(meta["splits"][split]), "samples": len(true),
              "model_region_top1": float((pred == true).mean()), "model_region_top5": float(np.mean(top5)),
              "model_region_distance_cells": grid_distance(pred, true),
              "baseline_most_frequent": float((true == most_common).mean()),
              "baseline_most_frequent_distance_cells": grid_distance(np.full_like(true, most_common), true),
              "baseline_copy_previous": float((true == prev).mean()),
              "baseline_copy_previous_distance_cells": grid_distance(prev, true),
              "baseline_stay_mid": float((true == (8 * 16 + 8)).mean()),
              "baseline_stay_mid_distance_cells": grid_distance(np.full_like(true, 8 * 16 + 8), true),
              "model_item_accuracy": float((item_predictions == items).mean()),
              "baseline_item_none": float((items == 0).mean()),
              "item_event_rate": float(conditional.mean()),
              "item_accuracy_when_purchase": float((item_predictions[conditional] == items[conditional]).mean()) if conditional.any() else None,
              "model_skill_accuracy": float((skill_predictions == skills).mean()),
              "baseline_skill_none": float((skills == 0).mean()),
              "skill_event_rate": float(skill_conditional.mean()),
              "skill_accuracy_when_upgrade": float((skill_predictions[skill_conditional] == skills[skill_conditional]).mean()) if skill_conditional.any() else None,
              "value_brier": float(np.mean((value_prob - value_actual) ** 2)),
              "baseline_value_brier": float(np.mean((train_win_rate - value_actual) ** 2)),
              "value_train_win_rate": train_win_rate,
              "most_frequent_region": most_common}
    if prior is not None:
        result["baseline_role_phase_prior"] = float(np.mean(prior == true))
        result["baseline_role_phase_prior_distance_cells"] = grid_distance(prior, true)
        result["calibration"] = {"alpha": model.prior_alpha, "item_none_bias": model.item_none_bias,
                                  "skill_none_bias": model.skill_none_bias}
    by_champion = defaultdict(lambda: [0, 0])
    by_patch = defaultdict(lambda: [0, 0])
    confusion = np.zeros((256, 256), dtype=np.int64)
    for (mid, _), champion, actual, guess in zip(ds.index, champions, truths, predictions):
        by_champion[str(champion)][0] += int(actual == guess)
        by_champion[str(champion)][1] += 1
        patch = meta.get("patches", {}).get(mid, "unknown")
        by_patch[patch][0] += int(actual == guess)
        by_patch[patch][1] += 1
        confusion[actual, guess] += 1
    result["by_champion"] = {k: {"accuracy": a / n, "samples": n} for k, (a, n) in by_champion.items()}
    result["by_patch"] = {k: {"accuracy": a / n, "samples": n} for k, (a, n) in by_patch.items()}
    def group_scores(indices):
        idx = np.asarray(indices, dtype=int)
        return {"samples": int(len(idx)), "model_region_top1": float(np.mean(pred[idx] == true[idx])),
                "baseline_most_frequent": float(np.mean(true[idx] == most_common)),
                "baseline_copy_previous": float(np.mean(true[idx] == prev[idx]))}
    groups = {"by_phase": defaultdict(list), "by_faker_role": defaultdict(list), "by_gold_state": defaultdict(list)}
    for j, ((mid, _), minute, diff) in enumerate(zip(ds.index, minutes, gold_diffs)):
        groups["by_phase"]["early_0_10" if minute < 10 else "mid_10_20" if minute < 20 else "late_20_plus"].append(j)
        groups["by_faker_role"][meta["faker_roles"].get(mid, "unknown")].append(j)
        groups["by_gold_state"]["ahead_2000" if diff > 2000 else "behind_2000" if diff < -2000 else "even"].append(j)
    for name, values in groups.items():
        result[name] = {key: group_scores(indices) for key, indices in values.items()}
    baseline_keys = ["baseline_most_frequent", "baseline_copy_previous", "baseline_stay_mid"]
    if prior is not None:
        baseline_keys.append("baseline_role_phase_prior")
    strongest = max(result[k] for k in baseline_keys)
    result["beats_all_region_baselines"] = result["model_region_top1"] > strongest
    result["region_gain_vs_best_baseline_pp"] = 100 * (result["model_region_top1"] - strongest)
    # Paired, match-level bootstrap: adjacent minutes in a game are correlated.
    by_match = defaultdict(list)
    for index, (mid, _) in enumerate(ds.index):
        by_match[mid].append(index)
    match_indices = [np.asarray(by_match[mid], dtype=int) for mid in meta["splits"][split]]
    rng = np.random.default_rng(CONFIG.seed)
    gains = []
    for _ in range(2000):
        chosen = rng.integers(0, len(match_indices), size=len(match_indices))
        idx = np.concatenate([match_indices[j] for j in chosen])
        model_score = np.mean(pred[idx] == true[idx])
        base_score = max(np.mean(true[idx] == most_common), np.mean(true[idx] == prev[idx]),
                         np.mean(true[idx] == 8 * 16 + 8))
        if prior is not None:
            base_score = max(base_score, np.mean(true[idx] == prior[idx]))
        gains.append(100 * (model_score - base_score))
    result["region_gain_bootstrap95_pp"] = [float(v) for v in np.quantile(gains, [.025, .975])]
    result["region_gain_clear_by_bootstrap"] = result["region_gain_bootstrap95_pp"][0] > 0
    def coarse_labels(regions: np.ndarray, grid: int) -> np.ndarray:
        block = 16 // grid
        regions = np.asarray(regions)
        return np.where(regions >= 0, (regions // 16 // block) * grid + (regions % 16 // block), -1)
    result["macro_grids_exploratory"] = {}
    for grid in (8, 4):
        coarse_true = coarse_labels(true, grid)
        coarse_prev = coarse_labels(prev, grid)
        coarse_model = np.asarray(macro_predictions[grid])
        # Several fine cells pool to one coarse cell, so sum their training counts.
        coarse_train = Counter()
        for region, count in train_regions.items():
            coarse_train[int(coarse_labels(np.array([region]), grid)[0])] += count
        common_coarse = coarse_train.most_common(1)[0][0]
        baseline_scores = {"most_frequent": float(np.mean(coarse_true == common_coarse)),
                           "copy_previous": float(np.mean(coarse_true == coarse_prev)),
                           "stay_mid": float(np.mean(coarse_true == (grid // 2 * grid + grid // 2)))}
        if prior is not None:
            coarse_prior = np.asarray(macro_prior_predictions[grid])
            baseline_scores["role_phase_prior"] = float(np.mean(coarse_true == coarse_prior))
        model_score = float(np.mean(coarse_true == coarse_model))
        coarse_gains = []
        coarse_rng = np.random.default_rng(CONFIG.seed + grid)
        for _ in range(2000):
            chosen = coarse_rng.integers(0, len(match_indices), size=len(match_indices))
            idx = np.concatenate([match_indices[j] for j in chosen])
            base = max(np.mean(coarse_true[idx] == common_coarse),
                       np.mean(coarse_true[idx] == coarse_prev[idx]),
                       np.mean(coarse_true[idx] == (grid // 2 * grid + grid // 2)))
            if prior is not None:
                base = max(base, np.mean(coarse_true[idx] == coarse_prior[idx]))
            coarse_gains.append(100 * (np.mean(coarse_true[idx] == coarse_model[idx]) - base))
        interval = [float(v) for v in np.quantile(coarse_gains, [.025, .975])]
        result["macro_grids_exploratory"][f"{grid}x{grid}"] = {
            "model_top1": model_score, "baselines": baseline_scores,
            "gain_vs_best_baseline_pp": 100 * (model_score - max(baseline_scores.values())),
            "gain_bootstrap95_pp": interval}
    artifacts.mkdir(parents=True, exist_ok=True)
    suffix = "" if split == "test" else f"_{split}"
    np.save(artifacts / f"region_confusion{suffix}.npy", confusion)
    fig, ax = plt.subplots(figsize=(8, 7))
    image = ax.imshow(np.log1p(confusion), origin="lower", cmap="magma", aspect="auto")
    fig.colorbar(image, ax=ax, label="log(1 + count)")
    ax.set(xlabel="Predicted region", ylabel="Actual region", title=f"{split.title()} region confusion (16×16 labels)")
    fig.tight_layout()
    fig.savefig(artifacts / f"region_confusion{suffix}.png", dpi=140)
    plt.close(fig)
    atomic_json(artifacts / f"evaluation{suffix}.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--split", choices=["val", "test"], default="test")
    args = parser.parse_args()
    print(json.dumps(evaluate(batch_size=args.batch_size, split=args.split), indent=2))


if __name__ == "__main__":
    main()
