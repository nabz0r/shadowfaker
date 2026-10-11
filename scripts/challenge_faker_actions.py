#!/usr/bin/env python3
"""Train an audited candidate and compare it with the frozen incumbent.

Selection is on the reused 46-match validation split only. The old test is
neither loaded nor scored. Models and per-match details remain local.
"""
from __future__ import annotations

import argparse
import hashlib
import json

import numpy as np
import torch

from shadowfaker.action_sanitation import DATA, FEATURE_NAMES, SCHEMA_VERSION
from shadowfaker.config import CONFIG
from shadowfaker.faker_actions import DATA as OLD_DATA, CLASSES
from shadowfaker.faker_action_model import (ActionMLP, MODEL, metrics, run,
                                           train_priors, _phase)
from shadowfaker.util import atomic_json, read_json

CANDIDATE = CONFIG.models / "faker_actions_sanitized_10s.pt"
PRIVATE = CONFIG.artifacts / "faker_actions_sanitized_challenge.json"
PUBLIC = CONFIG.root / "docs" / "data" / "public_faker_actions_sanitation.json"
CHECKPOINT = CONFIG.artifacts / "faker_actions_sanitized_checkpoint.json"
TRAIN_REPORT = CONFIG.artifacts / "faker_actions_sanitized_train.json"


def signature() -> str:
    """Invalidate a trained checkpoint when data, incumbent or trainer changes."""
    h = hashlib.sha256()
    for path in (DATA / "private_manifest.json", MODEL,
                 CONFIG.root / "src/shadowfaker/faker_action_model.py",
                 CONFIG.root / "src/shadowfaker/action_sanitation.py",
                 CONFIG.root / "scripts/challenge_faker_actions.py"):
        h.update(path.read_bytes())
    h.update(b"epochs=50;batch=512;seed=42")
    return h.hexdigest()


def _group(scores: dict, start: int, stop: int) -> dict:
    names = CLASSES[start:stop]
    return {"nll": float(np.mean([scores["per_class"][name]["nll"] for name in names])),
            "macro_ap": float(np.mean([scores["per_class"][name]["average_precision"]
                                       for name in names]))}


def compare(*, pilot: bool = False) -> dict:
    split = read_json(CONFIG.processed / "meta.json")["splits"]
    audit = read_json(DATA / "private_manifest.json")
    eligible = {mid for mid, row in audit.items() if row.get("status") == "eligible"}
    ids = [mid for mid in (split["val"][:2] if pilot else split["val"]) if mid in eligible]
    train_ids = [mid for mid in (split["train"][:3] if pilot else split["train"]) if mid in eligible]
    if not ids or not train_ids:
        raise ValueError("No eligible matches after sanitation")
    path = CANDIDATE.with_name(CANDIDATE.stem + "_pilot.pt") if pilot else CANDIDATE
    incumbent = ActionMLP()
    incumbent.load_state_dict(torch.load(MODEL, map_location="cpu", weights_only=True))
    candidate = ActionMLP(len(FEATURE_NAMES))
    candidate.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    incumbent.eval(), candidate.eval()
    prior = train_priors(train_ids, DATA)[1]
    labels, old_ps, new_ps, phase_ps, per_match = [], [], [], [], []
    with torch.no_grad():
        for mid in ids:
            with np.load(DATA / f"{mid}.npz") as z:
                x, y, t = z["x"].astype(np.float32), z["y"], z["t_ms"]
            with np.load(OLD_DATA / f"{mid}.npz") as z:
                if not np.array_equal(y, z["y"]) or not np.array_equal(t, z["t_ms"]):
                    raise AssertionError("Incumbent and candidate do not share labels and windows")
                if not np.array_equal(x[:, :z["x"].shape[1]], z["x"]):
                    raise AssertionError("The frozen incumbent state changed")
            old = torch.sigmoid(incumbent(torch.from_numpy(x[:, :37]))).numpy()
            new = torch.sigmoid(candidate(torch.from_numpy(x))).numpy()
            phase = prior[_phase(x)]
            labels.append(y)
            old_ps.append(old)
            new_ps.append(new)
            phase_ps.append(phase)
            a = y[:, :4].astype(np.float64)
            o, n = np.clip(old[:, :4], 1e-7, 1 - 1e-7), np.clip(new[:, :4], 1e-7, 1 - 1e-7)
            old_loss = float(-(a*np.log(o) + (1-a)*np.log1p(-o)).sum())
            new_loss = float(-(a*np.log(n) + (1-a)*np.log1p(-n)).sum())
            per_match.append({"match_id": mid, "windows": len(y),
                              "old_action_nll_sum": old_loss, "new_action_nll_sum": new_loss})
    y = np.concatenate(labels)
    old_score = metrics(y, np.concatenate(old_ps))
    new_score = metrics(y, np.concatenate(new_ps))
    phase_score = metrics(y, np.concatenate(phase_ps))
    matrix = np.asarray([[r["windows"]*4, r["old_action_nll_sum"], r["new_action_nll_sum"]]
                         for r in per_match])
    rng = np.random.default_rng(CONFIG.seed)
    draws = matrix[rng.integers(0, len(matrix), size=(2000, len(matrix)))].sum(axis=1)
    gains = (draws[:, 1] - draws[:, 2]) / draws[:, 0]
    old_actions, new_actions = _group(old_score, 0, 4), _group(new_score, 0, 4)
    outcome_old, outcome_new = _group(old_score, 4, 7), _group(new_score, 4, 7)
    report = {"schema_version": SCHEMA_VERSION, "pilot": pilot, "validation_matches": len(ids),
              "validation_windows": len(y), "features_incumbent": 37,
              "features_candidate": len(FEATURE_NAMES), "target": "Faker event in next 10 s",
              "acts": list(CLASSES[:4]), "outcomes": list(CLASSES[4:]),
              "scores": {"incumbent": old_score, "candidate": new_score, "phase_train_frequency": phase_score},
              "action_summary": {"incumbent": old_actions, "candidate": new_actions,
                                 "phase_train_frequency": _group(phase_score, 0, 4)},
              "outcome_summary": {"incumbent": outcome_old, "candidate": outcome_new},
              "action_nll_gain_candidate_vs_incumbent": old_actions["nll"] - new_actions["nll"],
              "action_nll_gain_ci95_match_bootstrap": np.quantile(gains, [.025, .975]).tolist(),
              "promote_candidate": (new_actions["nll"] < old_actions["nll"]
                                    and new_actions["macro_ap"] > old_actions["macro_ap"]),
              "selection": "same reused validation matches/windows; old test and future lockbox untouched",
              "limits": "events only; ~60 s sampled player state; omniscient positions; no clicks or causal skill",
              "per_match": per_match}
    atomic_json(PRIVATE.with_name(PRIVATE.stem + "_pilot.json") if pilot else PRIVATE, report)
    if not pilot:
        atomic_json(PUBLIC, {k: v for k, v in report.items() if k != "per_match"})
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    pilot_report = run(pilot=True, epochs=4, data=DATA, model_path=CANDIDATE,
                       private_path=CONFIG.artifacts / "faker_actions_sanitized_train.json",
                       public_path=PUBLIC, schema_version=SCHEMA_VERSION)
    pilot = compare(pilot=True)
    print(json.dumps({"pilot_train_windows": pilot_report["train_windows"],
                      "pilot_validation_windows": pilot["validation_windows"],
                      "pilot_action_summary": pilot["action_summary"]}, indent=2))
    if not args.pilot_only:
        key = signature()
        checkpoint = read_json(CHECKPOINT) or {}
        reused = (checkpoint.get("signature") == key and CANDIDATE.is_file()
                  and TRAIN_REPORT.is_file() and PRIVATE.is_file() and PUBLIC.is_file())
        if reused:
            trained, report = read_json(TRAIN_REPORT), read_json(PRIVATE)
        else:
            trained = run(data=DATA, model_path=CANDIDATE,
                          private_path=TRAIN_REPORT,
                          public_path=CONFIG.artifacts / "faker_actions_sanitized_train_aggregate.json",
                          schema_version=SCHEMA_VERSION)
            report = compare()
            atomic_json(CHECKPOINT, {"signature": key, "schema_version": SCHEMA_VERSION})
        print(json.dumps({"best_epoch": trained["best_epoch"],
                          "checkpoint_reused": reused,
                          "validation_matches": report["validation_matches"],
                          "validation_windows": report["validation_windows"],
                          "action_summary": report["action_summary"],
                          "outcome_summary": report["outcome_summary"],
                          "gain_ci95": report["action_nll_gain_ci95_match_bootstrap"],
                          "promote_candidate": report["promote_candidate"]}, indent=2))


if __name__ == "__main__":
    main()
