"""Train-only role/phase spatial priors, with interpolation chosen on validation."""
import json
import os
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from .config import CONFIG
from .dataset import MatchDataset
from .evaluate import load_model
from .features import FEATURE_NAMES
from .util import read_json


def role_phase(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    last = x[:, -1]
    role = np.clip(np.rint(last[:, FEATURE_NAMES.index("faker_role")] * 5).astype(int), 0, 5)
    minute = last[:, 0] * 50
    phase = (minute >= 10).astype(int) + (minute >= 20).astype(int)
    return role, phase


def calibrate(processed: Path = CONFIG.processed, checkpoint: Path = CONFIG.models / "best.pt") -> dict:
    meta = read_json(processed / "meta.json")
    model = load_model(meta, checkpoint, use_calibration=False)
    counts = np.zeros((6, 3, 256), dtype=np.float64)
    global_counts = np.zeros(256, dtype=np.float64)
    for mid in meta["splits"]["train"]:
        with np.load(processed / "matches" / f"{mid}.npz") as z:
            r, p = role_phase(z["x"])
            labels = z["region"]
        for role, phase, label in zip(r, p, labels):
            counts[role, phase, label] += 1
            global_counts[label] += 1
    global_probability = (global_counts + 1) / (global_counts.sum() + 256)
    ds = MatchDataset(processed, meta, "val", view=model.view)
    scores, labels, roles, phases = [], [], [], []
    item_scores, item_labels, skill_scores, skill_labels = [], [], [], []
    with torch.no_grad():
        for x, champion, y, item, skill, _ in DataLoader(ds, batch_size=128, shuffle=False):
            region_logits, item_logits, skill_logits, _ = model(x, champion)
            scores.append(region_logits.numpy())
            labels.append(y.numpy())
            item_scores.append(item_logits.numpy())
            item_labels.append(item.numpy())
            skill_scores.append(skill_logits.numpy())
            skill_labels.append(skill.numpy())
            r, p = role_phase(x.numpy())
            roles.append(r)
            phases.append(p)
    logits = np.concatenate(scores)
    actual = np.concatenate(labels)
    val_role, val_phase = np.concatenate(roles), np.concatenate(phases)
    best = {"accuracy": -1.0, "alpha": 0.0, "strength": 100}
    best_prior = None
    for strength in (20, 100, 500):
        probabilities = (counts + strength * global_probability) / (counts.sum(-1, keepdims=True) + strength)
        log_prior = np.log(probabilities).astype(np.float32)
        example_prior = log_prior[val_role, val_phase]
        for alpha in (0.0, .1, .2, .3, .5, .75, 1.0):
            accuracy = float(np.mean((logits + alpha * example_prior).argmax(-1) == actual))
            if accuracy > best["accuracy"] + 1e-12:
                best = {"accuracy": accuracy, "alpha": alpha, "strength": strength}
                best_prior = log_prior
    def none_bias(scores_list, labels_list):
        scores = np.concatenate(scores_list)
        labels = np.concatenate(labels_list)
        candidates = sorted((-1, -.5, 0, .25, .5, .75, 1, 1.5, 2, 3, 4, 6, 8), key=abs)
        best_bias, best_accuracy = 0.0, -1.0
        for bias in candidates:
            adjusted = scores.copy()
            adjusted[:, 0] += bias
            accuracy = float(np.mean(adjusted.argmax(-1) == labels))
            if accuracy > best_accuracy + 1e-12:
                best_bias, best_accuracy = float(bias), accuracy
        return best_bias, best_accuracy
    item_bias, item_accuracy = none_bias(item_scores, item_labels)
    skill_bias, skill_accuracy = none_bias(skill_scores, skill_labels)
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    saved["calibration"] = {**best, "log_prior": best_prior.tolist(),
                            "item_none_bias": item_bias, "item_validation_accuracy": item_accuracy,
                            "skill_none_bias": skill_bias, "skill_validation_accuracy": skill_accuracy,
                            "method": "train role/phase counts with global Dirichlet smoothing; region alpha and no-event biases selected on validation"}
    temp = checkpoint.with_suffix(".tmp")
    torch.save(saved, temp)
    os.replace(temp, checkpoint)
    return {key: value for key, value in saved["calibration"].items() if key != "log_prior"}


if __name__ == "__main__":
    print(json.dumps(calibrate(), indent=2))
