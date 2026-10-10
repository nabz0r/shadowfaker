"""Private episodic memory of Faker decisions and a match-disjoint challenger.

This is retrieval-based behavioral cloning, not a language model or a game
simulator. It uses only state at t and past context to find similar train cases.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sqlite3

import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .util import atomic_json, read_json, seed_all

SOURCE = CONFIG.root / "data" / "ioc_static"
LABELS = CONFIG.root / "data" / "processed64" / "labels"
DB = CONFIG.root / "data" / "processed" / "faker_memory.sqlite"
PUBLIC = CONFIG.root / "docs" / "data" / "public_faker_memory.json"
PRIVATE = CONFIG.root / "data" / "processed" / "faker_memory_challenge.json"
SCHEMA_VERSION = 1

CORE_NAMES = (
    "minute", "own_gold", "own_level", "own_xp", "own_cs", "gold_diff",
    "dragon_alive", "baron_alive", "herald_alive", "recent_kills",
    "recent_dragons", "recent_towers", "recent_purchases",
    "recent_ally_wards", "recent_ally_ward_kills", "recent_ally_kills",
    "recent_enemy_kills", "recent_jungle_kill_participation",
    "recent_bot_kill_participation", "gold_diff_delta", "xp_diff_delta",
    "own_current_gold", "own_at_base", "own_recent_deaths",
    "ally_jungle_distance", "ally_bot_distance", "ally_support_distance",
    "dragon_distance", "baron_distance", "visible_enemy_count",
    "enemy_within_2500", "nearest_visible_enemy_distance",
    "enemy_dragon_presence", "enemy_baron_presence", "jungler_cover_under_pressure",
    *(f"p{i}_{field}" for i in range(10) for field in
      ("x", "y", "visible", "age")),
)
IOC_NAMES = tuple(
    f"p{i}_{field}" for i in range(10) for field in
    ("item_slots", "item_changes_last_minute", "item_history_known",
     "static_catalog_value", "static_catalog_known_fraction")
)

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS matches (
 match_id TEXT PRIMARY KEY, split TEXT NOT NULL, source_stamp TEXT NOT NULL,
 observations INTEGER NOT NULL, patch TEXT, role TEXT
);
CREATE TABLE IF NOT EXISTS episodes (
 match_id TEXT NOT NULL, frame_index INTEGER NOT NULL, split TEXT NOT NULL,
 minute REAL NOT NULL, champion INTEGER NOT NULL, role TEXT NOT NULL, patch TEXT,
 state BLOB NOT NULL, current_x REAL, current_y REAL, next_x REAL NOT NULL,
 next_y REAL NOT NULL, next_cell8 INTEGER NOT NULL, next_cell64 INTEGER NOT NULL,
 next_cell512 INTEGER NOT NULL, previous_cell8 INTEGER,
 PRIMARY KEY(match_id,frame_index),
 FOREIGN KEY(match_id) REFERENCES matches(match_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS memory_split_role ON episodes(split,role,minute);
CREATE TABLE IF NOT EXISTS challenge_runs (
 run_id INTEGER PRIMARY KEY AUTOINCREMENT, created_utc TEXT NOT NULL,
 configuration TEXT NOT NULL, calibration_top1_8 REAL NOT NULL,
 validation_top1_8 REAL NOT NULL, validation_matches INTEGER NOT NULL,
 validation_cases INTEGER NOT NULL
);
"""


def feature_indices(names: list[str]) -> tuple[list[int], list[str]]:
    wanted = CORE_NAMES + IOC_NAMES
    missing = [name for name in wanted if name not in names]
    if missing:
        raise ValueError(f"Missing IoC feature names: {missing[:5]}")
    return [names.index(name) for name in wanted], list(wanted)


def cell_at(x: float, y: float, grid: int) -> int:
    return min(grid - 1, max(0, int(y * grid))) * grid + min(grid - 1, max(0, int(x * grid)))


def build(db_path: Path = DB, limit: int | None = None) -> dict:
    meta = read_json(SOURCE / "meta.json")
    if not meta:
        raise FileNotFoundError("Build patch-matched IoC first")
    indices, selected = feature_indices(meta["feature_names"])
    splits = {split: list(meta["splits"][split]) for split in ("train", "val")}
    if limit is not None:
        splits = {key: value[:limit] for key, value in splits.items()}
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.executescript(SCHEMA)
        previous = db.execute("SELECT value FROM metadata WHERE key='feature_names'").fetchone()
        if previous and json.loads(previous[0]) != selected:
            db.execute("DELETE FROM episodes")
            db.execute("DELETE FROM matches")
        db.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)", ("feature_names", json.dumps(selected)))
        db.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)", ("schema_version", str(SCHEMA_VERSION)))
        written = skipped = 0
        for split, ids in splits.items():
            for mid in tqdm(ids, desc=f"Faker memory {split}", unit="game"):
                source_path, label_path = SOURCE / "matches" / f"{mid}.npz", LABELS / f"{mid}.npz"
                stamp = ":".join(str(v) for p in (source_path, label_path)
                                 for v in (p.stat().st_size, p.stat().st_mtime_ns))
                existing = db.execute("SELECT split,source_stamp,observations FROM matches WHERE match_id=?", (mid,)).fetchone()
                if existing and existing[0] == split and existing[1] == stamp:
                    skipped += 1
                    continue
                with np.load(source_path) as data, np.load(label_path) as labels:
                    x, xy = data["x"], labels["xy"]
                    if len(x) != len(xy) or not np.allclose(data["minute"], labels["minute"], atol=.001):
                        raise ValueError("Source and labels do not align")
                    vector = np.nan_to_num(x[:, -1, indices], nan=0, posinf=0, neginf=0).astype("<f4")
                    role = str(meta.get("faker_roles", {}).get(mid, "UNKNOWN"))
                    patch = str(meta.get("patches", {}).get(mid, ""))
                    rows = []
                    own_x, own_y = meta["feature_names"].index("p0_x"), meta["feature_names"].index("p0_y")
                    for i in range(len(x)):
                        nx, ny = float(xy[i, 0]), float(xy[i, 1])
                        previous = int(labels["previous"][i])
                        rows.append((mid, i, split, float(data["minute"][i]), int(data["champion"][i]),
                                     role, patch, vector[i].tobytes(), float(x[i, -1, own_x]),
                                     float(x[i, -1, own_y]), nx, ny, cell_at(nx, ny, 8),
                                     cell_at(nx, ny, 64), cell_at(nx, ny, 512),
                                     None if previous < 0 else (previous // 64 // 8) * 8 + (previous % 64 // 8)))
                    with db:
                        db.execute("DELETE FROM matches WHERE match_id=?", (mid,))
                        db.execute("INSERT INTO matches VALUES (?,?,?,?,?,?)", (mid, split, stamp, len(rows), patch, role))
                        db.executemany("INSERT INTO episodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
                    written += 1
        counts = dict(db.execute("SELECT split,COUNT(*) FROM episodes GROUP BY split"))
        matches = dict(db.execute("SELECT split,COUNT(*) FROM matches GROUP BY split"))
    return {"written_matches": written, "cached_matches": skipped,
            "episodes": counts, "matches": matches, "feature_dim": len(selected)}


def load_split(db: sqlite3.Connection, split: str, width: int) -> dict:
    rows = db.execute("SELECT match_id,frame_index,minute,champion,role,state,next_cell8,next_cell64,"
                      "next_cell512,previous_cell8,current_x,current_y,next_x,next_y "
                      "FROM episodes WHERE split=? ORDER BY match_id,frame_index", (split,)).fetchall()
    if not rows:
        raise ValueError(f"No {split} episodes")
    vectors = np.frombuffer(b"".join(row[5] for row in rows), dtype="<f4").reshape(len(rows), width).copy()
    return {"state": vectors, "match": np.asarray([row[0] for row in rows]),
            "frame": np.asarray([row[1] for row in rows], np.int32),
            "minute": np.asarray([row[2] for row in rows], np.float32),
            "champion": np.asarray([row[3] for row in rows], np.int32),
            "role": np.asarray([row[4] for row in rows]),
            "y8": np.asarray([row[6] for row in rows], np.int16),
            "y64": np.asarray([row[7] for row in rows], np.int16),
            "y512": np.asarray([row[8] for row in rows], np.int32),
            "previous8": np.asarray([-1 if row[9] is None else row[9] for row in rows], np.int16),
            "current_xy": np.asarray([[row[10], row[11]] for row in rows], np.float32),
            "next_xy": np.asarray([[row[12], row[13]] for row in rows], np.float32)}


def subset(data: dict, selected: np.ndarray) -> dict:
    return {key: value[selected] for key, value in data.items()}


def partition_train(matches: np.ndarray, seed: int = CONFIG.seed) -> tuple[np.ndarray, np.ndarray]:
    unique = np.unique(matches)
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    held = set(unique[:max(1, round(len(unique) * .2))])
    calibration = np.isin(matches, list(held))
    return ~calibration, calibration


def transform(base: np.ndarray, query: np.ndarray, width: int, use_ioc: bool,
              position_weight: float) -> tuple[np.ndarray, np.ndarray]:
    count = width if use_ioc else len(CORE_NAMES)
    mean = base[:, :count].mean(axis=0)
    scale = np.maximum(base[:, :count].std(axis=0), .08)
    a = np.clip((base[:, :count] - mean) / scale, -3, 3).astype(np.float32)
    b = np.clip((query[:, :count] - mean) / scale, -3, 3).astype(np.float32)
    if use_ioc:
        a[:, len(CORE_NAMES):] *= np.sqrt(.35)
        b[:, len(CORE_NAMES):] *= np.sqrt(.35)
    for field in ("p0_x", "p0_y"):
        index = CORE_NAMES.index(field)
        a[:, index] *= np.sqrt(position_weight)
        b[:, index] *= np.sqrt(position_weight)
    return a / np.sqrt(count), b / np.sqrt(count)


def predict(memory: dict, query: dict, width: int, *, use_ioc: bool,
            champion_bonus: float, k: int, action_mode: str = "absolute",
            position_weight: float = 1.0, batch_size: int = 64,
            details: bool = False) -> tuple[np.ndarray, np.ndarray | None]:
    if action_mode not in ("absolute", "delta"):
        raise ValueError("action_mode must be absolute or delta")
    a, b = transform(memory["state"], query["state"], width, use_ioc, position_weight)
    y = memory["y8"]
    result = np.empty(len(b), np.int16)
    closest = np.empty(len(b), np.int32) if details else None
    norms = (a * a).sum(axis=1)
    for start in range(0, len(b), batch_size):
        stop = min(len(b), start + batch_size)
        scores = -(b[start:stop] * b[start:stop]).sum(axis=1)[:, None] - norms[None, :] + 2 * b[start:stop] @ a.T
        if champion_bonus:
            scores += champion_bonus * (query["champion"][start:stop, None] == memory["champion"][None, :])
        chosen = np.argpartition(scores, -k, axis=1)[:, -k:]
        chosen = np.take_along_axis(chosen, np.argsort(np.take_along_axis(scores, chosen, axis=1), axis=1)[:, ::-1], axis=1)
        for i, neighbors in enumerate(chosen):
            votes = np.zeros(64, np.float32)
            if action_mode == "delta":
                move = memory["next_xy"][neighbors] - memory["current_xy"][neighbors]
                proposed = np.clip(query["current_xy"][start + i] + move, 0, 1)
                labels = np.asarray([cell_at(x, y, 8) for x, y in proposed], np.int16)
            else:
                labels = y[neighbors]
            np.add.at(votes, labels, 1 / np.arange(1, k + 1, dtype=np.float32))
            result[start + i] = int(votes.argmax())
            if closest is not None:
                closest[start + i] = neighbors[0]
    return result, closest


def baselines(train: dict, query: dict) -> dict[str, float]:
    majority = Counter(train["y8"].tolist()).most_common(1)[0][0]
    by_role_phase: dict[tuple[str, int], Counter] = defaultdict(Counter)
    for role, minute, y in zip(train["role"], train["minute"], train["y8"]):
        by_role_phase[(str(role), 0 if minute < 10 else 1 if minute < 20 else 2)][int(y)] += 1
    role_pred = np.asarray([by_role_phase[(str(role), 0 if minute < 10 else 1 if minute < 20 else 2)].most_common(1)[0][0]
                            if by_role_phase[(str(role), 0 if minute < 10 else 1 if minute < 20 else 2)] else majority
                            for role, minute in zip(query["role"], query["minute"])])
    return {"most_frequent": float(np.mean(query["y8"] == majority)),
            "copy_previous": float(np.mean(query["y8"] == query["previous8"])),
            "stay_mid": float(np.mean(query["y8"] == 36)),
            "role_phase_prior": float(np.mean(query["y8"] == role_pred))}


def challenge(db_path: Path = DB, public_path: Path = PUBLIC) -> dict:
    seed_all(CONFIG.seed)
    with sqlite3.connect(db_path) as db:
        names = json.loads(db.execute("SELECT value FROM metadata WHERE key='feature_names'").fetchone()[0])
        train, val = load_split(db, "train", len(names)), load_split(db, "val", len(names))
        keep, held = partition_train(train["match"])
        memory, calibration = subset(train, keep), subset(train, held)
        trials = []
        for use_ioc in (False, True):
            for mode in ("absolute", "delta"):
                for position_weight in (1.0, 4.0):
                    for bonus in (0.0, .25):
                        for k in (1, 7, 15):
                            pred, _ = predict(memory, calibration, len(names), use_ioc=use_ioc,
                                              champion_bonus=bonus, k=k, action_mode=mode,
                                              position_weight=position_weight)
                            trials.append({"use_ioc": use_ioc, "action_mode": mode,
                                           "position_weight": position_weight,
                                           "champion_bonus": bonus, "k": k,
                                           "calibration_top1_8": float(np.mean(pred == calibration["y8"]))})
        winner = max(trials, key=lambda x: (x["calibration_top1_8"], -x["k"], int(x["use_ioc"])))
        prediction, neighbor = predict(train, val, len(names), use_ioc=winner["use_ioc"],
                                       champion_bonus=winner["champion_bonus"], k=winner["k"],
                                       action_mode=winner["action_mode"],
                                       position_weight=winner["position_weight"], details=True)
        score = float(np.mean(prediction == val["y8"]))
        if winner["action_mode"] == "delta":
            nearest_xy = np.clip(val["current_xy"] + train["next_xy"][neighbor] - train["current_xy"][neighbor], 0, 1)
            nearest64 = np.asarray([cell_at(x, y, 64) for x, y in nearest_xy])
            nearest512 = np.asarray([cell_at(x, y, 512) for x, y in nearest_xy])
        else:
            nearest64, nearest512 = train["y64"][neighbor], train["y512"][neighbor]
        outcome = {"schema_version": SCHEMA_VERSION, "method": "train-only episodic nearest-neighbor challenger",
                   "training_matches": len(np.unique(train["match"])),
                   "calibration_memory_matches": len(np.unique(memory["match"])),
                   "calibration_matches": len(np.unique(calibration["match"])),
                   "validation_matches": len(np.unique(val["match"])),
                   "training_episodes": len(train["y8"]), "validation_episodes": len(val["y8"]),
                   "feature_dim": len(names), "core_features": len(CORE_NAMES), "ioc_features": len(IOC_NAMES),
                   "selected": winner,
                   "best_calibrated_with_ioc": max(t["calibration_top1_8"] for t in trials if t["use_ioc"]),
                   "best_calibrated_without_ioc": max(t["calibration_top1_8"] for t in trials if not t["use_ioc"]),
                   "validation_top1_8": score,
                   "validation_baselines": baselines(train, val),
                   "validation_top1_64_nearest": float(np.mean(nearest64 == val["y64"])),
                   "validation_top1_512_nearest": float(np.mean(nearest512 == val["y512"])),
                   "historical_test_read": False,
                   "limit": "Validation is reused for project design. A similar past state is not a causal explanation or a 512 Hz observation."}
        from datetime import datetime, timezone
        with db:
            config_json = json.dumps(winner, sort_keys=True)
            existing = db.execute("SELECT 1 FROM challenge_runs WHERE configuration=? AND validation_matches=? "
                                  "AND validation_cases=? AND ABS(validation_top1_8-?)<1e-12",
                                  (config_json, outcome["validation_matches"], len(val["y8"]), score)).fetchone()
            if not existing:
                db.execute("INSERT INTO challenge_runs(created_utc,configuration,calibration_top1_8,validation_top1_8,validation_matches,validation_cases) VALUES (?,?,?,?,?,?)",
                           (datetime.now(timezone.utc).isoformat(), config_json,
                            winner["calibration_top1_8"], score, outcome["validation_matches"], len(val["y8"])))
        catalogs = sorted((CONFIG.raw / "ddragon").glob("*/en_US_champion.json"))
        champion_catalog = catalogs[-1] if catalogs else None
        names_by_id = ({int(item["key"]): item["name"] for item in
                        json.loads(champion_catalog.read_text()).get("data", {}).values()}
                       if champion_catalog and champion_catalog.is_file() else {})
        private = {"selected": winner,
                   "examples": [{"minute": round(float(val["minute"][i]), 1),
                                 "champion_id": int(val["champion"][i]),
                                 "champion": names_by_id.get(int(val["champion"][i]),
                                                             str(int(val["champion"][i]))),
                                 "role": str(val["role"][i]),
                                 "predicted_cell8": int(prediction[i]),
                                 "observed_cell8": int(val["y8"][i]),
                                 "nearest_train_cell8": int(train["y8"][neighbor[i]]),
                                 "predicted_cell512": int(nearest512[i]),
                                 "observed_cell512": int(val["y512"][i])}
                                for i in np.linspace(0, len(val["y8"]) - 1, min(24, len(val["y8"])), dtype=int)]}
        atomic_json(PRIVATE, private)
    atomic_json(public_path, outcome)
    return outcome


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true")
    args = parser.parse_args()
    pilot_path = CONFIG.root / "data" / "pilot_faker_memory.sqlite"
    pilot = build(pilot_path, limit=5)
    print(f"Pilot: {pilot['matches']} matches, {pilot['episodes']} episodes, {pilot['feature_dim']} features")
    if args.pilot_only:
        return
    full = build()
    result = challenge()
    print(f"Full: {full['episodes']} episodes; selected {result['selected']}; validation top-1 8x8={result['validation_top1_8']:.4f}")


if __name__ == "__main__":
    main()
