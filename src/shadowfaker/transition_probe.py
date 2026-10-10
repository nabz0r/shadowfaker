"""Train-only geometric transition baselines for the next Faker 8x8 cell.

The internal holdout is drawn from training matches. The 46-match historical
development validation is scored once after choosing a transition rule there.
No test or prospective matches are read.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .features import FEATURE_NAMES
from .finegrid import coarse_labels
from .util import atomic_json, read_json

SOURCE = CONFIG.root / "data" / "interaction"
LABELS = CONFIG.root / "data" / "processed64" / "labels"
OUTPUT = CONFIG.artifacts / "transition_probe.json"


def rows_for_matches(ids: list[str], *, progress: bool = True) -> tuple[list[dict], dict]:
    """Read one compressed match at a time and retain only compact geometry."""
    rows = []
    checked = mismatched = missing_current = 0
    for mid in tqdm(ids, desc="transition geometry", unit="game", disable=not progress):
        with np.load(SOURCE / "matches" / f"{mid}.npz") as z, \
             np.load(LABELS / f"{mid}.npz") as labels:
            x = z["x"]
            target = coarse_labels(labels["region"], 8)
            if len(x) != len(target) or not np.allclose(z["minute"], labels["minute"], atol=.001):
                raise ValueError(f"Misaligned input and target in {mid}")
            current = x[:, -1, 17:19]
            known = x[:, -1, 19] > .5
            prev = x[:, -2, 17:19]
            prev_known = x[:, -2, 19] > .5
            minute = labels["minute"]
            role = np.rint(x[:, -1, FEATURE_NAMES.index("faker_role")] * 5).astype(int)
            # The original previous-cell label is recomputed independently at 64x64.
            local64 = (np.floor(current[:, 1] * 64).astype(int) * 64 +
                       np.floor(current[:, 0] * 64).astype(int))
            checked += int(known.sum())
            mismatched += int(np.count_nonzero(known & (local64 != labels["previous"])))
            missing_current += int((~known).sum())
            for i in range(len(target)):
                if known[i]:
                    start = int(current[i, 1] * 8) * 8 + int(current[i, 0] * 8)
                else:
                    start = -1
                if known[i] and prev_known[i]:
                    delta = current[i] - prev[i]
                    if np.linalg.norm(delta) < .025:
                        direction = 8  # nearly stationary over the last observed minute
                    else:
                        direction = int(np.floor((math.atan2(float(delta[1]), float(delta[0])) +
                                                   math.pi / 8) / (math.pi / 4))) % 8
                else:
                    direction = 9  # unknown prior direction
                rows.append({"match": mid, "start": start, "target": int(target[i]),
                             "phase": int(minute[i] >= 10) + int(minute[i] >= 20),
                             "role": int(role[i]), "direction": direction,
                             "current_xy": current[i].copy(), "previous_xy": prev[i].copy(),
                             "previous_known": bool(prev_known[i]), "current_known": bool(known[i])})
    return rows, {"current_positions_checked": checked,
                  "current_vs_previous64_mismatches": mismatched,
                  "current_positions_missing": missing_current}


def _counts(rows: list[dict], fields: tuple[str, ...]):
    counts = defaultdict(lambda: np.zeros(64, np.float64))
    for row in rows:
        counts[tuple(row[field] for field in fields)][row["target"]] += 1
    return counts


class TransitionPrior:
    def __init__(self, rows: list[dict], fields: tuple[str, ...], strength: float):
        self.fields, self.strength = fields, strength
        self.global_counts = np.bincount([row["target"] for row in rows], minlength=64).astype(float)
        self.global_prob = (self.global_counts + .5) / (self.global_counts.sum() + 32)
        self.start_counts = _counts(rows, ("start",))
        self.conditional_counts = _counts(rows, fields)

    def probabilities(self, row: dict) -> np.ndarray:
        start = self.start_counts.get((row["start"],), np.zeros(64))
        start_prob = (start + 8 * self.global_prob) / (start.sum() + 8)
        if self.fields == ("start",):
            return start_prob
        key = tuple(row[field] for field in self.fields)
        conditional = self.conditional_counts.get(key, np.zeros(64))
        return (conditional + self.strength * start_prob) / (conditional.sum() + self.strength)


def ballistic_cell(row: dict, multiplier: float) -> int:
    if not row["current_known"]:
        return -1
    xy = row["current_xy"]
    if row["previous_known"]:
        xy = xy + multiplier * (xy - row["previous_xy"])
    xy = np.clip(xy, 0, .99999)
    return int(xy[1] * 8) * 8 + int(xy[0] * 8)


def evaluate(prior: TransitionPrior, rows: list[dict]) -> dict:
    correct = top5 = 0
    by_match = defaultdict(lambda: {"samples": 0, "correct": 0})
    by_phase = defaultdict(lambda: {"samples": 0, "correct": 0})
    for row in rows:
        probs = prior.probabilities(row)
        pred = int(probs.argmax())
        hit = pred == row["target"]
        correct += hit
        top5 += row["target"] in np.argpartition(probs, -5)[-5:]
        by_match[row["match"]]["samples"] += 1
        by_match[row["match"]]["correct"] += hit
        by_phase[row["phase"]]["samples"] += 1
        by_phase[row["phase"]]["correct"] += hit
    return {"top1": correct / len(rows), "top5": top5 / len(rows),
            "samples": len(rows), "matches": len(by_match),
            "by_match": dict(by_match), "by_phase": dict(by_phase)}


def run(*, pilot: bool = False) -> dict:
    meta = read_json(SOURCE / "meta.json")
    if not meta:
        raise FileNotFoundError("Build interaction data before transition audit")
    train_ids = meta["splits"]["train"][:4] if pilot else meta["splits"]["train"]
    val_ids = meta["splits"]["val"][:1] if pilot else meta["splits"]["val"]
    if set(train_ids) & set(val_ids) or set(train_ids + val_ids) & set(meta["splits"]["test"]):
        raise ValueError("Match split overlap")
    rng = np.random.default_rng(CONFIG.seed)
    order = rng.permutation(train_ids).tolist()
    internal_count = 1 if pilot else 75
    internal_ids = order[:internal_count]
    fit_ids = order[internal_count:]
    fit, audit_fit = rows_for_matches(fit_ids)
    internal, audit_internal = rows_for_matches(internal_ids)
    variants = (("start",), ("start", "phase"), ("start", "role", "phase"),
                ("start", "direction"), ("start", "direction", "phase"))
    options = []
    for fields in variants:
        for strength in ((0,) if fields == ("start",) else (4, 16, 64)):
            prior = TransitionPrior(fit, fields, strength)
            measured = evaluate(prior, internal)
            options.append({"fields": fields, "strength": strength,
                            "internal_top1": measured["top1"], "internal_top5": measured["top5"]})
    chosen = max(options, key=lambda row: (row["internal_top1"], row["internal_top5"],
                                           -len(row["fields"]), -row["strength"]))
    train, audit_train = rows_for_matches(train_ids)
    validation, audit_val = rows_for_matches(val_ids)
    prior = TransitionPrior(train, tuple(chosen["fields"]), chosen["strength"])
    scored = evaluate(prior, validation)
    ballistic = {str(scale): float(np.mean([ballistic_cell(row, scale) == row["target"]
                                           for row in validation])) for scale in (0, .5, 1)}
    original = read_json(CONFIG.artifacts / "hierarchical" / "validation_full.json", {})
    paired = None
    if original.get("by_match8") and set(original["by_match8"]) == set(scored["by_match"]):
        draws = []
        mids = list(scored["by_match"])
        for _ in range(1000):
            pick = rng.integers(0, len(mids), len(mids))
            numerator = sum(scored["by_match"][mids[j]]["correct"] -
                            original["by_match8"][mids[j]]["correct"] for j in pick)
            denominator = sum(scored["by_match"][mids[j]]["samples"] for j in pick)
            draws.append(100 * numerator / denominator)
        paired = {"delta_pp": 100 * (scored["top1"] - original["top1_8"]),
                  "bootstrap95_pp": np.quantile(draws, [.025, .975]).tolist(),
                  "comparison": "M3 full-context model, chosen on the same old validation"}
    report = {"status": "development_only", "pilot": pilot,
              "split": "train-internal selection then historical validation",
              "fit_matches": len(fit_ids), "internal_matches": len(internal_ids),
              "train_matches": len(train_ids), "val_matches": len(val_ids),
              "selection_options": options, "selected": chosen,
              "validation": scored, "ballistic_validation_top1": ballistic,
              "paired_vs_m3": paired,
              "alignment": {"fit": audit_fit, "internal": audit_internal,
                            "train": audit_train, "val": audit_val},
              "warning": "No old test or prospective games read; prior uses position and movement, not Faker POV."}
    atomic_json(OUTPUT.with_name("transition_probe_pilot.json") if pilot else OUTPUT, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    report = run(pilot=args.pilot_only)
    print(json.dumps({key: report[key] for key in ("selected", "validation", "paired_vs_m3",
                                                     "ballistic_validation_top1", "alignment")
                      if key != "validation"}, indent=2))
    print(json.dumps({"validation_top1": report["validation"]["top1"],
                      "validation_top5": report["validation"]["top5"]}, indent=2))


if __name__ == "__main__":
    main()
