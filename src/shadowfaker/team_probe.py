"""Chronological, match-level test of prior co-play as a scoreboard feature.

This experiment predicts the *15-minute gold gap* from information available
at ten minutes in a separate professional summary domain. It does not predict
Faker's movement, clicks, visibility, communication or match outcome.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import sqlite3

import numpy as np

from .config import CONFIG
from .pro_team_matrix import DB, ROLES
from .util import atomic_json, read_json

ROOT = CONFIG.root
MATRIX = CONFIG.processed / "pro_team_probe.npz"
META = CONFIG.processed / "pro_team_probe.meta.json"
PUBLIC = ROOT / "docs" / "data" / "public_team_probe.json"
SCHEMA = 1
VAL_START = "2025-08-01"
TEST_START = "2025-10-01"
LAMBDAS = (0.1, 1.0, 10.0, 100.0, 1000.0)
FOCUS = ("Doran", "Oner", "Keria")
ROW_FIELDS = ("gold_diff10", "xp_diff10", "kills10", "assists10", "deaths10")
BASE_NAMES = tuple(f"{role}_{field}_at10" for role in ROLES for field in ROW_FIELDS) + (
    "calendar_years", "calendar_sin", "calendar_cos")
HISTORY_NAMES = tuple(f"{name}_{field}_prior" for name in FOCUS for field in
                      ("log_games", "effective90", "log_days_since"))


def split_for(day: str) -> int:
    """0 train, 1 validation, 2 held-out test; boundaries are whole days."""
    return 0 if day < VAL_START else 1 if day < TEST_START else 2


def load_records(db_path: Path = DB) -> tuple[list[dict], str]:
    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        stamp = db.execute("SELECT value FROM metadata WHERE key='source_stamp'").fetchone()
        if not stamp:
            raise RuntimeError("Build the professional team matrix before the probe")
        records: dict[str, dict] = {}
        for row in db.execute("SELECT game_id,game_date,league FROM games "
                              "WHERE complete_snapshot=1 ORDER BY game_date,game_id"):
            records[row["game_id"]] = {"id": row["game_id"], "date": row["game_date"],
                                       "day": row["game_date"][:10], "league": row["league"] or "UNKNOWN",
                                       "roles": {}, "history": {}}
        for row in db.execute("SELECT p.game_id,p.role,p.player,p.champion,p.gold_diff10,"
                              "p.gold_diff15,p.xp_diff10,p.kills10,p.assists10,p.deaths10 "
                              "FROM players p JOIN games g USING(game_id) WHERE g.complete_snapshot=1"):
            records[row["game_id"]]["roles"][row["role"]] = dict(row)
        for row in db.execute("SELECT h.game_id,h.teammate,h.prior_games,h.prior_effective90,h.days_since "
                              "FROM pair_history h JOIN games g USING(game_id) WHERE g.complete_snapshot=1"):
            records[row["game_id"]]["history"][row["teammate"]] = dict(row)
    ordered = sorted(records.values(), key=lambda row: (row["date"], row["id"]))
    if any(set(row["roles"]) != set(ROLES) for row in ordered):
        raise RuntimeError("Professional probe needs exactly five roles per complete game")
    if len({row["id"] for row in ordered}) != len(ordered):
        raise RuntimeError("Duplicate professional game in probe")
    return ordered, hashlib.sha256(stamp["value"].encode()).hexdigest()


def vocabulary(train: list[dict]) -> list[tuple[str, str]]:
    counts = Counter()
    for row in train:
        counts[("league", row["league"])] += 1
        for role in ("top", "jng", "bot", "sup"):
            counts[(f"{role}_player", row["roles"][role]["player"])] += 1
        counts[("mid_champion", row["roles"]["mid"]["champion"] or "UNKNOWN")] += 1
    return sorted(key for key, count in counts.items() if count >= 5)


def vector(row: dict, vocab: list[tuple[str, str]]) -> tuple[list[float], list[float]]:
    at10 = []
    for role in ROLES:
        actor = row["roles"][role]
        for field in ROW_FIELDS:
            value = actor[field]
            if value is None or not math.isfinite(float(value)):
                raise ValueError(f"Missing at-10 value: {field}")
            at10.append(float(value) / 1000 if field in ("gold_diff10", "xp_diff10") else float(value))
    played = date.fromisoformat(row["day"])
    elapsed = (played - date(2022, 1, 1)).days
    at10.extend([elapsed / 365.25, math.sin(2 * math.pi * played.timetuple().tm_yday / 365.25),
                 math.cos(2 * math.pi * played.timetuple().tm_yday / 365.25)])
    categories = {("league", row["league"]),
                  ("mid_champion", row["roles"]["mid"]["champion"] or "UNKNOWN")}
    categories.update((f"{role}_player", row["roles"][role]["player"])
                      for role in ("top", "jng", "bot", "sup"))
    at10.extend(float(category in categories) for category in vocab)
    history = []
    for name in FOCUS:
        prior = row["history"].get(name)
        n = prior["prior_games"] if prior else 0
        effective = prior["prior_effective90"] if prior else 0
        days = prior["days_since"] if prior and prior["days_since"] is not None else 0
        if n < 0 or effective < 0 or days < 0:
            raise ValueError("A future or negative co-play history was found")
        history.extend([math.log1p(n), effective / 100, math.log1p(days) / 5])
    return at10, history


def pilot(db_path: Path = DB) -> dict:
    rows, _ = load_records(db_path)
    sample = rows[:5]
    if len(sample) != 5:
        raise RuntimeError("Five professional games are required for the pilot")
    vocab = vocabulary(sample)
    base, past = zip(*(vector(row, vocab) for row in sample))
    if len({len(x) for x in base}) != 1 or len({len(x) for x in past}) != 1:
        raise RuntimeError("Inconsistent professional feature widths")
    if any("15" in name or "final" in name or "result" in name for name in BASE_NAMES + HISTORY_NAMES):
        raise RuntimeError("Future field reached feature schema")
    return {"games": 5, "base_features": len(base[0]), "history_features": len(past[0])}


def prepare(db_path: Path = DB, matrix_path: Path = MATRIX, meta_path: Path = META) -> tuple[dict, dict]:
    rows, source_sha = load_records(db_path)
    stamp = {"schema": SCHEMA, "source_sha256": source_sha,
             "val_start": VAL_START, "test_start": TEST_START}
    old = read_json(meta_path, {})
    if old.get("stamp") == stamp and matrix_path.is_file():
        with np.load(matrix_path, allow_pickle=False) as data:
            return {key: data[key] for key in data.files}, old
    train = [row for row in rows if split_for(row["day"]) == 0]
    vocab = vocabulary(train)
    pairs = [vector(row, vocab) for row in rows]
    arrays = {"base": np.asarray([pair[0] for pair in pairs], dtype=np.float64),
              "history": np.asarray([pair[1] for pair in pairs], dtype=np.float64),
              "targets": np.asarray([[row["roles"][role]["gold_diff15"] for role in ("mid", "bot")]
                                     for row in rows], dtype=np.float64),
              "persistence": np.asarray([[row["roles"][role]["gold_diff10"] for role in ("mid", "bot")]
                                         for row in rows], dtype=np.float64),
              "split": np.asarray([split_for(row["day"]) for row in rows], dtype=np.int8),
              "day": np.asarray([row["day"] for row in rows]),
              "game_id": np.asarray([row["id"] for row in rows])}
    if not all(np.isfinite(arrays[key]).all() for key in ("base", "history", "targets", "persistence")):
        raise RuntimeError("Non-finite professional model matrix")
    for split in range(3):
        if not np.any(arrays["split"] == split):
            raise RuntimeError(f"Empty chronological split: {split}")
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    pending = matrix_path.with_suffix(".npz.part")
    with pending.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
    pending.replace(matrix_path)
    meta = {"stamp": stamp, "base_features": list(BASE_NAMES) + [f"{key}:{value}" for key, value in vocab],
            "history_features": list(HISTORY_NAMES),
            "counts": {name: int(np.sum(arrays["split"] == index))
                       for index, name in enumerate(("train", "validation", "test"))},
            "days": {name: int(len(set(arrays["day"][arrays["split"] == index])))
                     for index, name in enumerate(("train", "validation", "test"))}}
    atomic_json(meta_path, meta)
    return arrays, meta


def ridge_fit(x: np.ndarray, y: np.ndarray, penalty: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    scale = np.maximum(x.std(axis=0), 1.0)
    centered = (x - mean) / scale
    target_mean = y.mean(axis=0)
    weights = np.linalg.solve(centered.T @ centered + penalty * np.eye(x.shape[1]),
                              centered.T @ (y - target_mean))
    return mean, scale, target_mean, weights


def ridge_predict(model: tuple, x: np.ndarray) -> np.ndarray:
    mean, scale, target_mean, weights = model
    return (x - mean) / scale @ weights + target_mean


def metrics(actual: np.ndarray, forecast: np.ndarray) -> dict:
    error = forecast - actual
    return {"mae_gold": round(float(np.abs(error).mean()), 2),
            "rmse_gold": round(float(np.sqrt(np.mean(error ** 2))), 2),
            "side_accuracy": round(float(np.mean((forecast >= 0) == (actual >= 0))), 4)}


def cluster_interval(day: np.ndarray, left: np.ndarray, right: np.ndarray,
                     seed: int = 42, draws: int = 5000) -> list[float]:
    unique, reverse = np.unique(day, return_inverse=True)
    delta = np.abs(left) - np.abs(right)
    sums = np.bincount(reverse, weights=delta, minlength=len(unique))
    counts = np.bincount(reverse, minlength=len(unique))
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, len(unique), size=(draws, len(unique)))
    sampled = sums[picks].sum(axis=1) / counts[picks].sum(axis=1)
    return [round(float(value), 2) for value in np.quantile(sampled, [.025, .975])]


def run(db_path: Path = DB, matrix_path: Path = MATRIX, meta_path: Path = META,
        output: Path = PUBLIC) -> dict:
    arrays, meta = prepare(db_path, matrix_path, meta_path)
    x0 = arrays["base"]
    x1 = np.concatenate([x0, arrays["history"]], axis=1)
    y = arrays["targets"]
    train, val, test = (arrays["split"] == index for index in range(3))
    if (set(arrays["day"][train]) & set(arrays["day"][val]) or
            set(arrays["day"][val]) & set(arrays["day"][test]) or
            set(arrays["day"][train]) & set(arrays["day"][test])):
        raise RuntimeError("A professional series day crossed the chronological split")
    scores = []
    for penalty in LAMBDAS:
        model = ridge_fit(x0[train], y[train], penalty)
        forecast = ridge_predict(model, x0[val])
        scores.append(float(np.mean(np.abs(forecast[:, 0] - y[val, 0]))))
    chosen = LAMBDAS[int(np.argmin(scores))]
    baseline = ridge_fit(x0[train], y[train], chosen)
    augmented = ridge_fit(x1[train], y[train], chosen)
    pred0 = ridge_predict(baseline, x0[test])
    pred1 = ridge_predict(augmented, x1[test])
    val0 = ridge_predict(baseline, x0[val])
    val1 = ridge_predict(augmented, x1[val])
    endpoints = {}
    for index, role in enumerate(("faker_mid", "bot")):
        endpoints[role] = {
            "test": {"persistence": metrics(y[test, index], arrays["persistence"][test, index]),
                     "ten_minute_context": metrics(y[test, index], pred0[:, index]),
                     "context_plus_history": metrics(y[test, index], pred1[:, index])},
            "validation_mae_gold": {"ten_minute_context": metrics(y[val, index], val0[:, index])["mae_gold"],
                                    "context_plus_history": metrics(y[val, index], val1[:, index])["mae_gold"]},
            "paired_test_delta_history_minus_context_mae_gold": round(float(np.mean(
                np.abs(pred1[:, index] - y[test, index]) - np.abs(pred0[:, index] - y[test, index]))), 2),
            "paired_test_delta_ci95_day_bootstrap_gold": cluster_interval(
                arrays["day"][test], pred1[:, index] - y[test, index],
                pred0[:, index] - y[test, index])}
    mid = endpoints["faker_mid"]
    confirmed = (mid["paired_test_delta_ci95_day_bootstrap_gold"][1] < 0 and
                 mid["test"]["context_plus_history"]["mae_gold"] < mid["test"]["persistence"]["mae_gold"])
    public = {"schema_version": SCHEMA, "domain": "professional_scoreboard_backtest_only",
              "primary_incremental_signal_confirmed": bool(confirmed),
              "provenance": "unverified_public_mirror_of_Oracle_Elixir",
              "source": "https://github.com/twodotone/finalLOL/tree/main/data/csv",
              "target": "15-minute lane gold difference to opposing role; primary Faker mid, secondary bot",
              "features_available_by": "10 minutes, except date/league/roster known before match",
              "split": {"train_through": "2025-07-31", "validation": "2025-08-01 to 2025-09-30",
                        "test_from": "2025-10-01", "games": meta["counts"], "unique_days": meta["days"]},
              "features": {"context": len(meta["base_features"]), "prior_coplay_added": len(meta["history_features"]),
                           "prior_names": list(FOCUS), "history_half_life_days": 90},
              "model": {"type": "ridge_multioutput", "seed": 42, "same_penalty_both_variants": chosen,
                        "penalty_chosen_on_context_only_validation": list(LAMBDAS),
                        "context_validation_mid_mae_by_penalty_gold": [round(value, 2) for value in scores]},
              "endpoints": endpoints,
              "limits": "Historical chronological backtest, not prospective data collection. 10-minute lane gold/XP differences are omniscient scoreboard summaries, not Faker POV. No positions, pings, voice, decision labels or causal team synergy. Test games share patches/teams and may be serially dependent; 2026 mirror ends in April. This result cannot establish a gain for the ranked spatial model or 90% action accuracy."}
    atomic_json(output, public)
    return public
