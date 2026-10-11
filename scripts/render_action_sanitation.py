#!/usr/bin/env python3
"""Render the paired Faker action challenge from publishable aggregates."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "data" / "public_faker_actions_sanitation.json"
OUTPUT = ROOT / "docs" / "figures" / "faker_actions_sanitized.png"
NAMES = ("Purchase", "Skill point", "Ward placed", "Ward cleared",
         "Kill outcome", "Death outcome", "Assist outcome")


def main() -> None:
    report = json.loads(SOURCE.read_text())
    scores = report["scores"]
    classes = list(scores["candidate"]["per_class"])
    old = np.array([scores["incumbent"]["per_class"][name]["average_precision"] for name in classes]) * 100
    new = np.array([scores["candidate"]["per_class"][name]["average_precision"] for name in classes]) * 100
    phase = np.array([scores["phase_train_frequency"]["per_class"][name]["average_precision"] for name in classes]) * 100
    counts = [scores["candidate"]["per_class"][name]["positives"] for name in classes]
    plt.rcParams.update({"figure.facecolor": "#090b13", "axes.facecolor": "#161b28",
                         "axes.edgecolor": "#544254", "axes.labelcolor": "#f5eeee",
                         "text.color": "#f5eeee", "xtick.color": "#c5bfc9",
                         "ytick.color": "#f5eeee", "font.size": 10,
                         "savefig.facecolor": "#090b13"})
    fig, ax = plt.subplots(figsize=(13, 7.2), layout="constrained")
    fig.suptitle("SHADOW FAKER  /  10-SECOND PREDICTION CHALLENGE",
                 fontsize=20, fontweight="black", x=.035, ha="left")
    y = np.arange(len(classes))
    ax.barh(y + .25, new, .23, color="#ef4d70", label="Audited candidate · 48 state signals")
    ax.barh(y, old, .23, color="#e4aa65", label="Frozen incumbent · 37 signals")
    ax.barh(y - .25, phase, .23, color="#66cdd4", label="Train-only phase frequency")
    ax.axhline(3.5, color="#7f7281", linestyle="--", lw=1)
    for i in y:
        ax.text(new[i] + .25, i + .25, f"{new[i]:.1f}", va="center", fontsize=9)
    ax.set_yticks(y, [f"{name}  ·  {count} positives" for name, count in zip(NAMES, counts)])
    ax.invert_yaxis()
    ax.set_xlim(0, max(new) * 1.22)
    ax.set_xlabel("Average precision on the same 46 historical validation games (%) · higher is better")
    ax.grid(axis="x", alpha=.17)
    ax.legend(loc="lower right", facecolor="#161b28", edgecolor="#544254", labelcolor="#f5eeee")
    ax.text(.99, .97, "Actions above dashed line  ·  combat outcomes below  ·  7,480 windows",
            transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#d7c7d0")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=170)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
