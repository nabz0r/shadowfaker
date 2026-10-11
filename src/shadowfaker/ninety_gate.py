"""Exploratory exact-cell selective-prediction audit on ranked development games.

No historical test or prospective match is read. The M3 checkpoint was already
selected on these validation matches, so even cross-fold thresholds are not
independent confirmation of a 90% claim.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from .config import CONFIG
from .finegrid import coarse_labels
from .hierarchical import (DecisionDataset, HierarchicalPolicy, SOURCE,
                           feature_mask, prior_table, train_statistics)
from .util import atomic_json, read_json

CHECKPOINT = CONFIG.models / "hierarchical" / "full.pt"
REFERENCE = CONFIG.artifacts / "hierarchical" / "validation_full.json"
PUBLIC = CONFIG.root / "docs" / "data" / "public_ninety_gate.json"
GRID = (0.05, 0.10, 0.20, 0.50, 1.0)
THRESHOLD_GRID = (0.10, 0.20, 0.40, 0.60, 0.80, 1.0)
MIN_COVERAGE = 0.10
MIN_CALIBRATION = 50
TARGET = 0.90


def wilson_lower(hits: int, count: int, z: float = 1.96) -> float:
    if count <= 0 or hits < 0 or hits > count:
        raise ValueError("Invalid binomial counts")
    p = hits / count
    divisor = 1 + z * z / count
    center = p + z * z / (2 * count)
    margin = z * math.sqrt(p * (1 - p) / count + z * z / (4 * count * count))
    return (center - margin) / divisor


def fixed_coverage(confidence: np.ndarray, correct: np.ndarray, fractions=GRID) -> list[dict]:
    if len(confidence) != len(correct) or not len(confidence):
        raise ValueError("Confidence and correctness must align")
    order = np.argsort(-confidence, kind="stable")
    rows = []
    for fraction in fractions:
        if not 0 < fraction <= 1:
            raise ValueError("Coverage must be within (0,1]")
        count = max(1, math.ceil(len(order) * fraction))
        hits = int(correct[order[:count]].sum())
        rows.append({"coverage_target": fraction, "served": count,
                     "coverage_actual": round(count / len(order), 4),
                     "correct": hits, "exact_accuracy": round(hits / count, 4),
                     "wilson_lower95": round(wilson_lower(hits, count), 4)})
    return rows


def select_threshold(confidence: np.ndarray, correct: np.ndarray) -> dict | None:
    """Predeclared 90% lower-bound rule fitted on calibration matches only."""
    candidates = []
    for fraction in THRESHOLD_GRID:
        threshold = float(np.sort(confidence)[::-1][max(0, math.ceil(len(confidence) * fraction) - 1)])
        selected = confidence >= threshold
        n = int(selected.sum())
        if n < MIN_CALIBRATION or n / len(confidence) < MIN_COVERAGE:
            continue
        hits = int(correct[selected].sum())
        lower = wilson_lower(hits, n)
        if lower >= TARGET:
            candidates.append({"threshold": threshold, "calibration_served": n,
                               "calibration_accuracy": hits / n,
                               "calibration_lower95": lower,
                               "calibration_coverage": n / len(confidence)})
    return max(candidates, key=lambda item: item["calibration_served"], default=None)


def score_fold(confidence: np.ndarray, correct: np.ndarray, matches: np.ndarray,
               calibration_matches: set[str]) -> dict:
    calibration = np.isin(matches, list(calibration_matches))
    threshold = select_threshold(confidence[calibration], correct[calibration])
    result = {"calibration_cases": int(calibration.sum()),
              "assessment_cases": int((~calibration).sum()),
              "threshold_selected": threshold is not None}
    if threshold is None:
        return result
    selected = (~calibration) & (confidence >= threshold["threshold"])
    n = int(selected.sum())
    hits = int(correct[selected].sum())
    result.update({"calibration": {k: round(v, 5) for k, v in threshold.items()},
                   "assessment": {"served": n, "coverage": round(n / int((~calibration).sum()), 4),
                                  "exact_accuracy": round(hits / n, 4) if n else None,
                                  "wilson_lower95": round(wilson_lower(hits, n), 4) if n else None,
                                  "gate_pass": bool(n >= MIN_CALIBRATION and
                                                    n / int((~calibration).sum()) >= MIN_COVERAGE and
                                                    wilson_lower(hits, n) >= TARGET)}})
    return result


def predict(ids: list[str], meta: dict, checkpoint: Path = CHECKPOINT,
            reference: Path = REFERENCE) -> dict[str, np.ndarray]:
    published = read_json(reference)
    digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    if not published or digest != published.get("checkpoint_sha256"):
        raise ValueError("M3 checkpoint differs from its recorded validation result")
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if saved.get("signature") != published.get("checkpoint_signature"):
        raise ValueError("M3 checkpoint signature mismatch")
    names = meta["feature_names"]
    model = HierarchicalPolicy(len(names), saved["width"], saved["layers"], saved.get("phase_gate", False))
    model.load_state_dict(saved["state_dict"])
    model.eval()
    priors = train_statistics(meta["splits"]["train"], meta["counts"], names)
    table = prior_table(priors)
    alpha = float(published["prior_alpha"])
    dataset = DecisionDataset(ids, meta["counts"], feature_mask(names, "full"))
    truth, confidence, prediction, minute = [], [], [], []
    role_index = names.index("faker_role")
    with torch.no_grad():
        for x, champion, y64, _, _, _, m, _ in DataLoader(dataset, batch_size=128):
            log8 = model(x, champion)[0]
            role = (x[:, -1, role_index] * 5).round().long().clamp(0, 5)
            phase = (m >= 10).long() + (m >= 20).long()
            probabilities = torch.softmax(log8 + alpha * table[role, phase], dim=-1)
            c, p = probabilities.max(dim=-1)
            confidence.extend(c.tolist()); prediction.extend(p.tolist())
            truth.extend(coarse_labels(y64, 8).tolist()); minute.extend(m.tolist())
    matches = np.asarray([mid for mid, _ in dataset.index])
    output = {"match": matches, "confidence": np.asarray(confidence),
              "correct": np.asarray(prediction) == np.asarray(truth),
              "minute": np.asarray(minute)}
    if not all(len(value) == len(matches) for value in output.values()):
        raise RuntimeError("Confidence rows do not align with match labels")
    return output


def run(*, pilot: bool = False, output: Path = PUBLIC) -> dict:
    meta = read_json(SOURCE / "meta.json")
    if not meta or len(meta["feature_names"]) != meta["feature_dim"]:
        raise ValueError("Interaction schema missing or invalid")
    train, val, test = (meta["splits"][key] for key in ("train", "val", "test"))
    if set(train) & set(val) or set(train) & set(test) or set(val) & set(test):
        raise ValueError("Match splits overlap")
    ids = list(val[:5] if pilot else val)
    rows = predict(ids, meta)
    total = len(rows["correct"])
    if pilot:
        if len(ids) != 5 or total < 5:
            raise ValueError("Five-game pilot did not produce observations")
        return {"status": "pilot", "matches": 5, "transitions": total,
                "exact_accuracy": round(float(rows["correct"].mean()), 4)}
    if len(ids) != 46 or total != 1275:
        raise ValueError(f"Unexpected validation cohort: {len(ids)} matches, {total} transitions")
    curve = fixed_coverage(rows["confidence"], rows["correct"])
    rng = np.random.default_rng(CONFIG.seed)
    shuffled = np.asarray(ids).copy(); rng.shuffle(shuffled)
    half = len(shuffled) // 2
    folds = [score_fold(rows["confidence"], rows["correct"], rows["match"], set(shuffled[:half])),
             score_fold(rows["confidence"], rows["correct"], rows["match"], set(shuffled[half:]))]
    phase = {}
    for name, selected in (("early", rows["minute"] < 10),
                           ("middle", (rows["minute"] >= 10) & (rows["minute"] < 20)),
                           ("late", rows["minute"] >= 20)):
        phase[name] = {"cases": int(selected.sum()),
                       "exact_accuracy": round(float(rows["correct"][selected].mean()), 4)}
    outcome = {"schema_version": 1, "status": "exploratory_not_independent",
               "target": "one exact next-minute 8x8 Faker destination cell, all ranked validation transitions",
               "model": "selected M3 full-context hierarchical checkpoint with recorded role/phase prior",
               "model_checkpoint_sha256": read_json(REFERENCE)["checkpoint_sha256"],
               "pilot_games_first": 5, "validation_matches": len(ids), "validation_transitions": total,
               "all_transitions_accuracy": round(float(rows["correct"].mean()), 4),
               "accuracy_at_fixed_served_coverage": curve, "phase": phase,
               "selective_gate": {"target_exact_accuracy": TARGET, "minimum_coverage": MIN_COVERAGE,
                                  "minimum_calibration_cases": MIN_CALIBRATION,
                                  "criterion": "Wilson lower 95% at least 0.90 on calibration and assessment",
                                  "folds": folds,
                                  "status": "no_qualifying_threshold" if not all(
                                      item.get("assessment", {}).get("gate_pass") for item in folds)
                                  else "exploratory_candidate_only"},
               "prospective": {"status": "blocked_by_expired_riot_key", "snapshot": "20261011",
                               "new_games_scored": 0, "required_new_games": 100},
               "limits": "The checkpoint and prior were already selected on all 46 development validation games. Confidence ranking is diagnostic, not an independent test. A selective score must always name served coverage; neither top-k map coverage nor a majority class is exact accuracy. No historical test or future lockbox was read."}
    atomic_json(output, outcome)
    return outcome
