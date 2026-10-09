"""Descriptive, match-level analysis of Faker's rotations and team outcomes.

Proximity is an association, never an estimate of causal contribution to winning.
"""
from collections import defaultdict
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from .config import CONFIG
from .features import FEATURE_NAMES, ROLE_ID
from .util import atomic_json, read_json

ROLES = ("JUNGLE", "BOTTOM", "UTILITY", "MIDDLE", "TOP")
PHASES = ("early_0_10", "mid_10_20", "late_20_plus")
OBJECTIVES = {"DRAGON": np.array([9866, 4414]) / 15000,
              "BARON": np.array([5007, 10471]) / 15000}


def phase(minute: float) -> str:
    return PHASES[0] if minute < 10 else PHASES[1] if minute < 20 else PHASES[2]


def analyze(processed: Path = CONFIG.processed, artifacts: Path = CONFIG.artifacts) -> dict:
    meta = read_json(processed / "meta.json")
    if not meta:
        raise FileNotFoundError("Process matches first")
    # One value per match/phase/target avoids treating long matches as many independent wins.
    match_values = defaultdict(list)
    followup_values = defaultdict(list)
    xp_index = FEATURE_NAMES.index("xp_diff")
    match_count = 0
    for mid in tqdm(meta["counts"], desc="analyze Faker rotations", unit="game"):
        with np.load(processed / "matches" / f"{mid}.npz") as z:
            x = z["x"][:, -1, :]
            minutes = z["minute"]
        win = bool(meta["faker_wins"][mid])
        own_role = meta["faker_roles"][mid]
        own_pos = x[:, 17:19]
        per_phase = defaultdict(lambda: defaultdict(list))
        per_phase_followup = defaultdict(lambda: defaultdict(list))
        for idx, minute in enumerate(minutes):
            p = phase(float(minute))
            current = x[idx]
            if current[19] == 0:  # a missing Faker position is never evidence of proximity
                continue
            future = int(np.searchsorted(minutes, minute + 2))
            has_followup = future < len(minutes) and minutes[future] <= minute + 3
            if has_followup:
                gold_change = float((x[future, 7] - current[7]) * 30000)
                xp_change = float((x[future, xp_index] - current[xp_index]) * 50000)
            for role in ROLES:
                if role == own_role:
                    continue
                ally_slots = [slot for slot in range(1, 5) if abs(current[17 + slot * 9 + 4] - ROLE_ID[role] / 5) < .001]
                if not ally_slots:
                    continue
                if current[17 + ally_slots[0] * 9 + 2] == 0:
                    continue
                ally = current[17 + ally_slots[0] * 9:19 + ally_slots[0] * 9]
                near = float(np.linalg.norm(own_pos[idx] - ally) <= 2000 / 15000)
                per_phase[p][role].append(near)
                if has_followup:
                    per_phase_followup[p][(role, bool(near))].append((gold_change, xp_change))
            for name, center in OBJECTIVES.items():
                per_phase[p][name].append(float(np.linalg.norm(own_pos[idx] - center) <= 2500 / 15000))
            per_phase[p]["ahead"].append(float(current[7] * 30000 > 2000))
            per_phase[p]["behind"].append(float(current[7] * 30000 < -2000))
        for p, groups in per_phase.items():
            for name, values in groups.items():
                match_values[(p, name, win)].append(float(np.mean(values)))
        for p, groups in per_phase_followup.items():
            for (role, near), changes in groups.items():
                followup_values[(p, role, near, win)].append(np.mean(changes, axis=0))
        match_count += 1
    rows = []
    for (p, name, win), values in sorted(match_values.items()):
        rows.append({"phase": p, "target": name, "faker_win": win,
                     "matches": len(values), "mean_match_fraction": float(np.mean(values)),
                     "median_match_fraction": float(np.median(values))})
    followup_rows = []
    for (p, role, near, win), values in sorted(followup_values.items()):
        mean = np.mean(values, axis=0)
        followup_rows.append({"phase": p, "target": role, "nearby": near, "faker_win": win,
                              "matches": len(values), "mean_team_gold_diff_change_2m": float(mean[0]),
                              "mean_team_xp_diff_change_2m": float(mean[1])})
    result = {"matches": match_count, "distance_ally_units": 2000, "distance_objective_units": 2500,
              "rows": rows, "followup_rows": followup_rows,
              "interpretation": "Match-averaged proximity, outcome and subsequent two-minute team advantage associations only. Nearby ally presence does not prove Faker caused a gain; communication and exact vision are unavailable."}
    artifacts.mkdir(parents=True, exist_ok=True)
    atomic_json(artifacts / "faker_rotations.json", result)
    index = {(r["phase"], r["target"], r["faker_win"]): r for r in rows}
    targets = ("JUNGLE", "BOTTOM", "UTILITY", "TOP", "DRAGON", "BARON")
    values = np.full((len(targets), len(PHASES)), np.nan)
    for y, target in enumerate(targets):
        for xindex, p in enumerate(PHASES):
            won = index.get((p, target, True))
            lost = index.get((p, target, False))
            if won and lost:
                values[y, xindex] = won["mean_match_fraction"] - lost["mean_match_fraction"]
    fig, ax = plt.subplots(figsize=(7.5, 5))
    image = ax.imshow(values, cmap="coolwarm", vmin=-.3, vmax=.3, aspect="auto")
    ax.set_xticks(range(len(PHASES)), ["0–10 min", "10–20 min", "20+ min"])
    ax.set_yticks(range(len(targets)), ["Jungler", "Bot carry", "Support", "Top", "Dragon pit", "Baron pit"])
    ax.set_title("Faker proximity: win minus loss match averages\nAssociation only; match length normalized")
    fig.colorbar(image, ax=ax, label="Difference in fraction of observed minutes")
    fig.tight_layout()
    fig.savefig(artifacts / "faker_rotations.png", dpi=150)
    plt.close(fig)
    return result


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2))
